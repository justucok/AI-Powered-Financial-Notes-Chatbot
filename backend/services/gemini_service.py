import json
import logging
from functools import lru_cache
from json import JSONDecodeError
from typing import Any

from google import genai
from google.genai import errors, types

try:
    from backend.config import get_settings
except ModuleNotFoundError:
    from config import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()

MODEL_NAME = "gemini-3.5-flash"
ERROR_FALLBACK: dict[str, Any] = {
    "is_transaction": False,
    "action": "chat",
    "reply": "Maaf, terjadi kesalahan teknis.",
}
CHAT_SYSTEM_PROMPT = """
Kamu adalah asisten keuangan pribadi yang profesional dan formal.
Tugasmu adalah membantu pengguna mencatat dan memantau keuangan pribadi mereka.

INSTRUKSI UTAMA:
1. Jika pengguna menyebutkan transaksi keuangan, ekstrak data dan kembalikan dalam format JSON berikut:
{
  "is_transaction": true,
  "type": "income" atau "expense",
  "amount": <angka tanpa titik/koma>,
  "category": <string, contoh: Makanan, Transport, Gaji, dll>,
  "description": <string deskripsi singkat>,
  "date": <"YYYY-MM-DD" atau null jika tidak disebutkan>
}

2. Jika pengguna bertanya tentang saldo atau ringkasan bulan tertentu, kembalikan:
{
  "is_transaction": false,
  "action": "query_summary",
  "month": <"YYYY-MM" atau null>
}

3. Jika bukan transaksi dan bukan query keuangan, balas secara natural:
{
  "is_transaction": false,
  "action": "chat",
  "reply": <string balasan formal>
}

ATURAN:
- Selalu gunakan Bahasa Indonesia yang formal dan sopan
- Jika amount tidak jelas, tanyakan kembali kepada pengguna
- Kategori umum: Makanan, Transport, Belanja, Kesehatan, Hiburan, Gaji, Freelance, Investasi, Lainnya
- Jangan pernah mengasumsikan amount jika tidak disebutkan secara eksplisit
""".strip()
IMAGE_EXTRACTION_PROMPT = """
Analisis gambar nota atau bukti transaksi ini.
Ekstrak data transaksi dan kembalikan hanya JSON dengan struktur berikut:
{
  "is_transaction": true atau false,
  "type": "income" atau "expense" atau null,
  "amount": <angka tanpa titik/koma atau null>,
  "category": <string kategori atau null>,
  "description": <deskripsi singkat transaksi atau null>,
  "date": <"YYYY-MM-DD" atau null>,
  "reply": <balasan formal singkat dalam Bahasa Indonesia>
}

ATURAN:
- Jika gambar tidak cukup jelas atau bukan bukti transaksi, set is_transaction ke false
- Jangan mengarang nominal atau tanggal
- Gunakan Bahasa Indonesia yang formal dan sopan
""".strip()
CHAT_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "is_transaction": {"type": "boolean"},
        "type": {"type": ["string", "null"]},
        "amount": {"type": ["number", "null"]},
        "category": {"type": ["string", "null"]},
        "description": {"type": ["string", "null"]},
        "date": {"type": ["string", "null"]},
        "action": {"type": ["string", "null"]},
        "month": {"type": ["string", "null"]},
        "reply": {"type": ["string", "null"]},
    },
    "required": ["is_transaction"],
}
IMAGE_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "is_transaction": {"type": "boolean"},
        "type": {"type": ["string", "null"]},
        "amount": {"type": ["number", "null"]},
        "category": {"type": ["string", "null"]},
        "description": {"type": ["string", "null"]},
        "date": {"type": ["string", "null"]},
        "reply": {"type": ["string", "null"]},
    },
    "required": ["is_transaction"],
}


@lru_cache
def _get_client() -> genai.Client:
    """Create and cache the Google GenAI client."""

    return genai.Client(api_key=settings.gemini_api_key)


def _format_history(history: list[dict[str, Any]]) -> str:
    """Format the last ten chat messages into plain text context."""

    formatted_messages: list[str] = []
    for item in history[-10:]:
        role = str(item.get("role", "user")).strip() or "user"
        content = str(item.get("content", "")).strip()
        if content:
            formatted_messages.append(f"{role}: {content}")

    return "\n".join(formatted_messages)


def _build_chat_prompt(message: str, history: list[dict[str, Any]]) -> str:
    """Build the text prompt sent to Gemini for chat processing."""

    history_text = _format_history(history)
    if history_text:
        return (
            f"{CHAT_SYSTEM_PROMPT}\n\n"
            f"Riwayat percakapan terakhir:\n{history_text}\n\n"
            f"Pesan pengguna terbaru:\n{message}"
        )

    return f"{CHAT_SYSTEM_PROMPT}\n\nPesan pengguna terbaru:\n{message}"


def _get_generation_config(schema: dict[str, Any]) -> types.GenerateContentConfig:
    """Create a structured-output generation config."""

    return types.GenerateContentConfig(
        response_mime_type="application/json",
        response_json_schema=schema,
    )


def _parse_response(response: Any) -> dict[str, Any]:
    """Convert a Gemini response into a Python dictionary."""

    parsed_response = getattr(response, "parsed", None)
    if isinstance(parsed_response, dict):
        return parsed_response

    text_response = getattr(response, "text", "")
    if not text_response:
        raise JSONDecodeError("Empty response", "", 0)

    loaded_response = json.loads(text_response)
    if not isinstance(loaded_response, dict):
        raise JSONDecodeError("Response is not a JSON object", text_response, 0)

    return loaded_response


async def process_chat(message: str, history: list[dict[str, Any]]) -> dict[str, Any]:
    """Process a text message with Gemini and return structured JSON output."""

    prompt = _build_chat_prompt(message, history)
    generation_config = _get_generation_config(CHAT_RESPONSE_SCHEMA)

    try:
        response = await _get_client().aio.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=generation_config,
        )
        return _parse_response(response)
    except errors.APIError:
        logger.exception("Gemini API returned an error for chat processing.")
    except JSONDecodeError:
        logger.exception("Gemini returned invalid JSON for chat processing.")
    except Exception:
        logger.exception("Gemini chat processing failed.")

    return ERROR_FALLBACK.copy()


async def process_image(image_bytes: bytes, mime_type: str) -> dict[str, Any]:
    """Process a receipt image with Gemini and return structured JSON output."""

    generation_config = _get_generation_config(IMAGE_RESPONSE_SCHEMA)
    contents: list[Any] = [
        IMAGE_EXTRACTION_PROMPT,
        types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
    ]

    try:
        response = await _get_client().aio.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=generation_config,
        )
        return _parse_response(response)
    except errors.APIError:
        logger.exception("Gemini API returned an error for image processing.")
    except JSONDecodeError:
        logger.exception("Gemini returned invalid JSON for image processing.")
    except Exception:
        logger.exception("Gemini image processing failed.")

    return ERROR_FALLBACK.copy()


async def close_gemini_client() -> None:
    """Close underlying Google GenAI HTTP clients."""

    client = _get_client()

    try:
        await client.aio.aclose()
    except Exception:
        logger.exception("Failed to close Google GenAI async client cleanly.")

    try:
        client.close()
    except Exception:
        logger.exception("Failed to close Google GenAI client cleanly.")
