from datetime import date, datetime
from typing import Any

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.repositories import transaction_repository
    from backend.schemas.transaction import TransactionCreate, TransactionResponse
    from backend.services import gemini_service
except ModuleNotFoundError:
    from repositories import transaction_repository
    from schemas.transaction import TransactionCreate, TransactionResponse
    from services import gemini_service


def _format_summary_reply(month: str, total_income: float, total_expense: float, balance: float) -> str:
    """Build a formal summary reply for the requested month."""

    return (
        f"Ringkasan keuangan untuk {month}: "
        f"pemasukan sebesar Rp {total_income:,.0f}, "
        f"pengeluaran sebesar Rp {total_expense:,.0f}, "
        f"dan saldo sebesar Rp {balance:,.0f}."
    ).replace(",", ".")


def _normalize_transaction_payload(payload: dict[str, Any]) -> TransactionCreate:
    """Convert Gemini transaction output into a validated transaction payload."""

    transaction_date = payload.get("date")
    if transaction_date is None:
        transaction_date = date.today().isoformat()

    return TransactionCreate(
        type=payload["type"],
        amount=payload["amount"],
        category=payload["category"],
        description=payload.get("description"),
        date=transaction_date,
    )


def _normalize_month(month: str | None) -> str:
    """Return a valid YYYY-MM month string, defaulting to the current month."""

    if not month:
        return datetime.now().strftime("%Y-%m")

    try:
        parsed_month = datetime.strptime(month, "%Y-%m")
    except ValueError:
        return datetime.now().strftime("%Y-%m")

    return parsed_month.strftime("%Y-%m")


def _build_transaction_reply(payload: dict[str, Any], transaction: TransactionResponse) -> dict[str, Any]:
    """Build a consistent chat response after saving a transaction."""

    reply = payload.get("reply")
    if not reply:
        reply = (
            "Transaksi berhasil dicatat."
            f" {transaction.type.title()} sebesar Rp {transaction.amount:,.0f}"
            f" untuk kategori {transaction.category}."
        ).replace(",", ".")

    return {
        "reply": reply,
        "data": transaction.model_dump(mode="json"),
    }


async def handle_text_message(
    db: AsyncSession,
    message: str,
    history: list[dict[str, Any]],
) -> dict[str, Any]:
    """Process a text chat message and return the business result."""

    result = await gemini_service.process_chat(message, history)

    if result.get("is_transaction"):
        try:
            transaction_data = _normalize_transaction_payload(result)
        except (KeyError, TypeError, ValidationError):
            return {
                "reply": result.get(
                    "reply",
                    "Mohon lengkapi detail transaksi terlebih dahulu agar dapat saya catat.",
                ),
            }

        transaction = await transaction_repository.create(db, transaction_data)
        transaction_response = TransactionResponse.model_validate(transaction)
        return _build_transaction_reply(result, transaction_response)

    if result.get("action") == "query_summary":
        month = _normalize_month(result.get("month"))
        summary = await transaction_repository.get_summary(db, month)
        reply = result.get("reply") or _format_summary_reply(
            month,
            summary["total_income"],
            summary["total_expense"],
            summary["balance"],
        )
        return {
            "reply": reply,
            "data": {
                "month": month,
                **summary,
            },
        }

    return {
        "reply": result.get("reply", "Maaf, saya belum dapat memproses permintaan Anda."),
    }


async def handle_image_message(
    db: AsyncSession,
    image_bytes: bytes,
    mime_type: str,
) -> dict[str, Any]:
    """Process an image message and persist a transaction when extraction succeeds."""

    result = await gemini_service.process_image(image_bytes, mime_type)

    if result.get("is_transaction"):
        try:
            transaction_data = _normalize_transaction_payload(result)
        except (KeyError, TypeError, ValidationError):
            return {
                "reply": result.get(
                    "reply",
                    "Maaf, detail transaksi pada gambar belum cukup jelas untuk dicatat.",
                ),
            }

        transaction = await transaction_repository.create(db, transaction_data)
        transaction_response = TransactionResponse.model_validate(transaction)
        return _build_transaction_reply(result, transaction_response)

    return {
        "reply": result.get("reply", "Maaf, transaksi tidak dapat diekstrak dari gambar tersebut."),
    }
