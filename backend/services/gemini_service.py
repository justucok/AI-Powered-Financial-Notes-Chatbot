import json
import logging
from datetime import datetime
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

MODEL_NAME = "gemini-3.1-flash-lite"
ERROR_FALLBACK: dict[str, Any] = {
    "is_transaction": False,
    "transactions": [],
    "action": "chat",
    "reply": "Maaf, terjadi kesalahan teknis.",
}
CHAT_SYSTEM_PROMPT = """
Kamu adalah asisten keuangan pribadi yang profesional dan formal.
Tugasmu adalah membantu pengguna mencatat dan memantau keuangan pribadi mereka.

INSTRUKSI UTAMA:
1. Jika pengguna menyebutkan transaksi keuangan (bisa satu atau lebih dari satu transaksi sekaligus), ekstrak semua transaksi tersebut ke dalam list "transactions" pada format JSON berikut:
{
  "is_transaction": true,
  "transactions": [
    {
      "type": "income" atau "expense",
      "amount": <angka tanpa titik/koma>,
      "category": <string, contoh: Makanan, Transport, Gaji, dll>,
      "description": <string deskripsi singkat>,
      "date": <"YYYY-MM-DD" atau null jika tidak disebutkan>
    }
  ],
  "reply": <string balasan formal yang menyapa pengguna dan menegaskan seluruh transaksi yang berhasil dicatat>
}

2. Jika pengguna bertanya tentang saldo atau ringkasan bulan tertentu, kembalikan:
{
  "is_transaction": false,
  "action": "query_summary",
  "month": <"YYYY-MM" atau null>,
  "reply": <string balasan formal terkait ringkasan>
}

3. Jika pengguna ingin menambahkan sumber uang (seperti bank, e-wallet, dompet, dll) baru, kembalikan:
{
  "is_transaction": false,
  "action": "add_fund_source",
  "fund_source": {
    "name": <string, nama sumber uang>,
    "type": <string, "bank", "ewallet", "cash", atau "other">,
    "icon": <string emoji, contoh: 💳, 📱, 💵>,
    "initial_balance": <angka tanpa titik/koma>
  },
  "reply": <string balasan formal>
}

4. Jika pengguna ingin mengatur/mengubah budget (anggaran pengeluaran) bulanan secara total (contoh: "atur budget bulan ini 5 juta", "set budget 3.000.000"), kembalikan:
{
  "is_transaction": false,
  "action": "set_budget",
  "budget": {
    "month": <"YYYY-MM" format, default bulan berjalan jika tidak ditentukan>,
    "amount": <angka nominal budget tanpa titik/koma>
  },
  "reply": <string balasan formal>
}

5. Jika pengguna ingin mengatur/mengubah budget untuk kategori pengeluaran tertentu (contoh: "set budget makanan 1.5 juta", "atur budget kategori transportasi 500 ribu"), kembalikan:
{
  "is_transaction": false,
  "action": "set_category_budget",
  "category_budget": {
    "month": <"YYYY-MM" format, default bulan berjalan jika tidak ditentukan>,
    "category_name": <string nama kategori yang diatur budgetnya>,
    "amount": <angka nominal budget tanpa titik/koma>
  },
  "reply": <string balasan formal>
}

6. Jika pengguna meminta untuk dipanggil dengan sebutan/sapaan lain (contoh: "panggil saya kak", "panggil saya mba", "jangan panggil bapak"), kembalikan:
{
  "is_transaction": false,
  "action": "update_greeting",
  "greeting": <string panggilan baru, contoh: "Kak", "Mba", "Bro">,
  "reply": <string balasan formal yang mengonfirmasi bahwa mulai sekarang bot akan memanggil dengan sebutan tersebut>
}

7. Jika pengguna ingin menyesuaikan atau mengubah saldo suatu sumber uang ke nominal tertentu (contoh: "ubah saldo bca jadi 100 ribu", "adjust saldo gopay menjadi 50000"), kembalikan:
{
  "is_transaction": false,
  "action": "adjust_balance",
  "fund_source_name": <string nama sumber uang yang disebut pengguna>,
  "target_balance": <angka nominal saldo yang diinginkan tanpa titik/koma>,
  "reply": <string balasan formal>
}

8. Jika bukan transaksi, bukan query keuangan, bukan penambahan sumber uang, bukan pengaturan budget, bukan permintaan ubah nama panggilan, dan bukan penyesuaian saldo, balas secara natural:
{
  "is_transaction": false,
  "action": "chat",
  "reply": <string balasan formal>
}

ATURAN:
- Selalu gunakan Bahasa Indonesia yang formal dan sopan
- Jika amount tidak jelas, tanyakan kembali kepada pengguna
- Kategori transaksi harus sesuai dengan daftar kategori pengguna. Jika tidak ada yang cocok, gunakan salah satu kategori yang paling relevan.
- Jangan pernah mengasumsikan amount jika tidak disebutkan secara eksplisit
""".strip()

IMAGE_EXTRACTION_PROMPT = """
Analisis gambar nota atau bukti transaksi ini.
Ekstrak semua transaksi yang tertera (bisa satu atau lebih jika berupa gabungan struk) dan kembalikan hanya JSON dengan struktur berikut:
{
  "is_transaction": true atau false,
  "transactions": [
    {
      "type": "income" atau "expense",
      "amount": <angka tanpa titik/koma>,
      "category": <string kategori>,
      "description": <deskripsi singkat transaksi>,
      "date": <"YYYY-MM-DD" atau null>
    }
  ],
  "reply": <balasan formal singkat dalam Bahasa Indonesia mengenai apa saja yang berhasil dicatat>
}

ATURAN:
- Jika gambar tidak cukup jelas atau bukan bukti transaksi, set is_transaction ke false
- Jangan mengarang nominal atau tanggal
- Gunakan Bahasa Indonesia yang formal dan sopan
""".strip()

PDF_STATEMENT_PROMPT = """
Kamu diberikan teks yang diekstrak dari e-statement/mutasi rekening bank Indonesia.
Ekstrak SEMUA transaksi (debit/kredit) yang tercantum dan kembalikan dalam format JSON berikut:
{
  "is_transaction": true,
  "transactions": [
    {
      "type": "income" atau "expense",
      "amount": <angka tanpa titik/koma>,
      "category": <string kategori>,
      "description": <deskripsi singkat dari kolom keterangan/mutasi>,
      "date": <"YYYY-MM-DD">
    }
  ],
  "reply": <ringkasan formal: berapa transaksi ditemukan, rentang tanggal, total debit/kredit>
}

ATURAN PENTING:
- Kredit/CR/Masuk = "income"
- Debit/DB/Keluar = "expense"
- Abaikan baris saldo akhir/saldo awal, hanya ambil baris mutasi
- Jika tanggal hanya berisi hari/bulan (tanpa tahun), inferensikan tahun dari konteks dokumen
- Kategori: gunakan Gaji, Transfer, Belanja, Makanan, Transport, Tagihan, Investasi, Lainnya
- Gunakan Bahasa Indonesia yang formal pada field 'reply'
""".strip()

CHAT_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "is_transaction": {"type": "boolean"},
        "transactions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "amount": {"type": "number"},
                    "category": {"type": "string"},
                    "description": {"type": ["string", "null"]},
                    "date": {"type": ["string", "null"]},
                    "fund_source_name": {"type": ["string", "null"]},
                },
                "required": ["type", "amount", "category"]
            }
        },
        "action": {"type": ["string", "null"]},
        "month": {"type": ["string", "null"]},
        "reply": {"type": ["string", "null"]},
        "greeting": {"type": ["string", "null"]},
        "fund_source_name": {"type": ["string", "null"]},
        "target_balance": {"type": ["number", "null"]},
        "fund_source": {
            "type": ["object", "null"],
            "properties": {
                "name": {"type": "string"},
                "type": {"type": "string"},
                "icon": {"type": "string"},
                "initial_balance": {"type": "number"}
            }
        },
        "budget": {
            "type": ["object", "null"],
            "properties": {
                "month": {"type": "string"},
                "amount": {"type": "number"}
            }
        },
        "category_budget": {
            "type": ["object", "null"],
            "properties": {
                "month": {"type": "string"},
                "category_name": {"type": "string"},
                "amount": {"type": "number"}
            }
        }
    },
    "required": ["is_transaction"],
}

IMAGE_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "is_transaction": {"type": "boolean"},
        "transactions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "amount": {"type": "number"},
                    "category": {"type": "string"},
                    "description": {"type": ["string", "null"]},
                    "date": {"type": ["string", "null"]},
                },
                "required": ["type", "amount", "category"]
            }
        },
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


def _build_chat_prompt(
    message: str,
    history: list[dict[str, Any]],
    nickname: str | None = None,
    greeting: str | None = None,
    fund_sources: list[dict[str, Any]] | None = None,
    categories: list[Any] | None = None,
) -> str:
    """Build the text prompt sent to Gemini for chat processing.

    Injects the user's nickname preference and available fund sources.
    """

    current_date = datetime.now()
    current_month_str = current_date.strftime("%Y-%m")
    system_prompt = CHAT_SYSTEM_PROMPT + f"\n\nKONTEKS TANGGAL SAAT INI:\n- Bulan berjalan saat ini (ini/bulan ini) adalah: {current_month_str} (format YYYY-MM)."
    
    greeting_str = greeting or "Bapak/Ibu"
    if nickname:
        system_prompt += (
            f"\n\nATURAN TAMBAHAN:\n"
            f"- Nama pengguna adalah: '{nickname}', dan sapaan yang disukai adalah '{greeting_str}'.\n"
            f"- Sapa dan panggil pengguna dengan sebutan '{greeting_str} {nickname}' secara formal dan sopan "
            f"(contoh: 'Baik, {greeting_str} {nickname}' atau 'Silakan {greeting_str}')."
        )
    
    if fund_sources:
        sources_str = ", ".join(f'"{s["name"]}" ({s["type"]})' for s in fund_sources)
        system_prompt += (
            f"\n\nSUMBER UANG TERSEDIA: {sources_str}\n"
            f"- Jika pengguna menyebutkan salah satu sumber uang, isi 'fund_source_name' pada item transaksi dengan nama yang paling cocok.\n"
            f"- Jika sumber uang tidak disebutkan dengan jelas, isi 'fund_source_name' dengan null."
        )

    if categories:
        cats_str = ", ".join(f'"{c.name}" ({c.type})' for c in categories)
        system_prompt += (
            f"\n\nKATEGORI TRANSAKSI PENGGUNA SAAT INI: {cats_str}\n"
            f"- Harap klasifikasikan transaksi ke dalam salah satu kategori di atas.\n"
            f"- Jika tidak ada yang pas, pilih yang paling mendekati."
        )

    history_text = _format_history(history)
    if history_text:
        return (
            f"{system_prompt}\n\n"
            f"Riwayat percakapan terakhir:\n{history_text}\n\n"
            f"Pesan pengguna terbaru:\n{message}"
        )

    return f"{system_prompt}\n\nPesan pengguna terbaru:\n{message}"


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


async def process_chat(
    message: str,
    history: list[dict[str, Any]],
    nickname: str | None = None,
    greeting: str | None = None,
    fund_sources: list[dict[str, Any]] | None = None,
    categories: list[Any] | None = None,
) -> dict[str, Any]:
    """Process a text message with Gemini and return structured JSON output."""

    prompt = _build_chat_prompt(message, history, nickname, greeting, fund_sources, categories)
    generation_config = _get_generation_config(CHAT_RESPONSE_SCHEMA)

    print(f"\n[LOG] ===================== Mengirim Pesan ke Gemini =====================")
    print(f"[LOG] Prompt:\n{prompt}")
    print(f"[LOG] ======================================================================\n")

    try:
        response = await _get_client().aio.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=generation_config,
        )
        print("[LOG] Berhasil mendapatkan balasan dari Gemini.")
        return _parse_response(response)
    except errors.APIError as e:
        print(f"[LOG] Gagal mengirim pesan ke Gemini: API Error: {e}")
        logger.exception("Gemini API returned an error for chat processing.")
    except JSONDecodeError as e:
        print(f"[LOG] Gagal memproses balasan: JSONDecodeError: {e}")
        logger.exception("Gemini returned invalid JSON for chat processing.")
    except Exception as e:
        print(f"[LOG] Gagal: Exception lainnya: {e}")
        logger.exception("Gemini chat processing failed.")

    return ERROR_FALLBACK.copy()


async def process_image(
    image_bytes: bytes,
    mime_type: str,
    message: str = "",
    nickname: str | None = None,
    greeting: str | None = None,
    categories: list[Any] | None = None,
) -> dict[str, Any]:
    """Process a receipt image with Gemini and return structured JSON output."""

    generation_config = _get_generation_config(IMAGE_RESPONSE_SCHEMA)
    trimmed_message = message.strip()
    
    prompt = IMAGE_EXTRACTION_PROMPT
    greeting_str = greeting or "Bapak/Ibu"
    if nickname:
        prompt += (
            f"\n\nATURAN TAMBAHAN:\n"
            f"- Nama pengguna adalah: '{nickname}', dan sapaan yang disukai adalah '{greeting_str}'.\n"
            f"- Sapa dan panggil pengguna dengan sebutan '{greeting_str} {nickname}' secara formal dan sopan "
            f"pada field 'reply' (contoh: 'Baik, {greeting_str} {nickname}' atau 'Silakan {greeting_str}')."
        )
    
    if categories:
        cats_str = ", ".join(f'"{c.name}" ({c.type})' for c in categories)
        prompt += (
            f"\n\nKATEGORI TRANSAKSI PENGGUNA SAAT INI: {cats_str}\n"
            f"- Harap klasifikasikan transaksi ke dalam salah satu kategori di atas jika memungkinkan."
        )

    if trimmed_message:
        prompt = (
            f"{prompt}\n\n"
            f"Konteks tambahan dari pengguna:\n{trimmed_message}"
        )

    contents: list[Any] = [
        prompt,
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


async def process_pdf_statement(
    pdf_text: str,
    nickname: str | None = None,
    greeting: str | None = None,
    categories: list[Any] | None = None,
) -> dict[str, Any]:
    """Proses teks e-statement bank dan ekstrak semua transaksi.

    Args:
        pdf_text: Teks yang sudah diekstrak dari PDF e-statement.
        nickname: Nama panggilan pengguna untuk personalisasi balasan.
        greeting: Sapaan yang disukai pengguna.
        categories: Daftar kategori pengguna untuk klasifikasi.

    Returns:
        Dict berisi list transaksi yang diekstrak atau error fallback.
    """
    prompt = PDF_STATEMENT_PROMPT
    greeting_str = greeting or "Bapak/Ibu"
    if nickname:
        prompt += (
            f"\n\nSapa pengguna dengan sebutan '{greeting_str} {nickname}' pada field 'reply'."
        )
    if categories:
        cats_str = ", ".join(f'"{c.name}"' for c in categories)
        prompt += f"\n\nKATEGORI TERSEDIA: {cats_str}"

    full_prompt = f"{prompt}\n\n--- TEKS E-STATEMENT ---\n{pdf_text}"
    generation_config = _get_generation_config(CHAT_RESPONSE_SCHEMA)

    try:
        response = await _get_client().aio.models.generate_content(
            model=MODEL_NAME,
            contents=full_prompt,
            config=generation_config,
        )
        return _parse_response(response)
    except Exception:
        logger.exception("Gagal memproses teks e-statement.")

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
