from datetime import date, datetime
from typing import Any

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.repositories import transaction_repository, fund_source_repository
    from backend.schemas.transaction import TransactionCreate, TransactionResponse
    from backend.schemas.fund_source import FundSourceCreate
    from backend.schemas.budget import BudgetCreate, CategoryBudgetCreate
    from backend.services import gemini_service, category_service, budget_service
except ModuleNotFoundError:
    from repositories import transaction_repository, fund_source_repository
    from schemas.transaction import TransactionCreate, TransactionResponse
    from schemas.fund_source import FundSourceCreate
    from schemas.budget import BudgetCreate, CategoryBudgetCreate
    from services import gemini_service, category_service, budget_service


def _format_summary_reply(month: str, total_income: float, total_expense: float, balance: float) -> str:
    """Build a formal summary reply for the requested month."""

    return (
        f"Ringkasan keuangan untuk {month}: "
        f"pemasukan sebesar Rp {total_income:,.0f}, "
        f"pengeluaran sebesar Rp {total_expense:,.0f}, "
        f"dan saldo sebesar Rp {balance:,.0f}."
    ).replace(",", ".")


def _normalize_transaction_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Convert Gemini transaction item into a validated transaction dict."""

    transaction_date = payload.get("date")
    if transaction_date is None:
        transaction_date = date.today().isoformat()

    return {
        "type": payload["type"],
        "amount": payload["amount"],
        "category": payload["category"],
        "description": payload.get("description"),
        "date": transaction_date,
    }


def _normalize_month(month: str | None) -> str:
    """Return a valid YYYY-MM month string, defaulting to the current month."""

    if not month:
        return datetime.now().strftime("%Y-%m")

    try:
        parsed_month = datetime.strptime(month, "%Y-%m")
    except ValueError:
        return datetime.now().strftime("%Y-%m")

    return parsed_month.strftime("%Y-%m")


def _build_transaction_reply(payload: dict[str, Any], transactions: list[TransactionResponse]) -> dict[str, Any]:
    """Build a consistent chat response after saving multiple transactions."""

    reply = payload.get("reply")
    if not reply:
        if len(transactions) == 1:
            tx = transactions[0]
            reply = (
                "Transaksi berhasil dicatat."
                f" {tx.type.title()} sebesar Rp {tx.amount:,.0f}"
                f" untuk kategori {tx.category}."
            ).replace(",", ".")
        else:
            reply = f"Berhasil mencatat {len(transactions)} transaksi keuangan Anda."

    return {
        "reply": reply,
        "data": [tx.model_dump(mode="json") for tx in transactions],
    }


def _find_source_id(fund_sources: list[dict[str, Any]] | None, name_to_match: str | None) -> int | None:
    if not fund_sources or not name_to_match:
        return None
    name_to_match = name_to_match.lower()
    for source in fund_sources:
        if source.get("name", "").lower() == name_to_match:
            return source.get("id")
    # Basic fuzzy match: if part of the string matches
    for source in fund_sources:
        if name_to_match in source.get("name", "").lower():
            return source.get("id")
    return None


async def handle_text_message(
    db: AsyncSession,
    message: str,
    history: list[dict[str, Any]],
    nickname: str | None = None,
    greeting: str | None = None,
    fund_sources: list[dict[str, Any]] | None = None,
    auth_db: AsyncSession | None = None,
    current_user: Any = None,
) -> dict[str, Any]:
    """Process a text chat message with user's nickname preference and fund sources."""

    categories = await category_service.get_categories(db)

    result = await gemini_service.process_chat(message, history, nickname, greeting, fund_sources, categories)

    if result.get("is_transaction") and result.get("transactions"):
        processed_transactions = []
        needs_source = False

        for tx_item in result["transactions"]:
            try:
                transaction_data = _normalize_transaction_payload(tx_item)
                # Check for fund source match
                source_name = tx_item.get("fund_source_name")
                matched_id = _find_source_id(fund_sources, source_name)
                
                # If the user has fund sources but we couldn't confidently match one,
                # we need to ask the user. (Only if there are any fund sources available)
                if matched_id is None and fund_sources and len(fund_sources) > 0:
                    needs_source = True
                
                transaction_data["fund_source_id"] = matched_id
                processed_transactions.append(transaction_data)
            except (KeyError, TypeError, ValidationError) as exc:
                logger = logging.getLogger(__name__)
                logger.warning("Failed to parse individual transaction from Gemini response: %s", str(exc))

        if not processed_transactions:
            return {
                "reply": result.get(
                    "reply",
                    "Mohon lengkapi detail transaksi terlebih dahulu agar dapat saya catat.",
                ),
            }

        if needs_source:
            # Need user to pick the fund source for the transactions
            # Convert to dict for pending_transactions
            pending = []
            for tx in processed_transactions:
                pending.append({
                    "type": tx["type"],
                    "amount": tx["amount"],
                    "category": tx["category"],
                    "description": tx["description"],
                    "date": tx["date"],
                    "fund_source_id": tx["fund_source_id"],
                })

            return {
                "reply": result.get("reply", "Pilih sumber uang untuk transaksi Anda."),
                "requires_fund_source": True,
                "pending_transactions": pending,
            }

        # Safe to save all directly
        saved_transactions: list[TransactionResponse] = []
        for transaction_data in processed_transactions:
            tx_create = TransactionCreate(**transaction_data)
            transaction = await transaction_repository.create(db, tx_create)
            saved_transactions.append(TransactionResponse.model_validate(transaction))

        if saved_transactions:
            return _build_transaction_reply(result, saved_transactions)

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

    if result.get("action") == "add_fund_source":
        fs_data = result.get("fund_source")
        if fs_data:
            try:
                fs_create = FundSourceCreate(**fs_data)
                created_fs = await fund_source_repository.create(db, fs_create)
                reply = result.get("reply", f"Sumber uang {fs_create.name} berhasil ditambahkan.")
                return {
                    "action": "add_fund_source_success",
                    "reply": reply,
                    "data": {
                        "id": created_fs.id,
                        "name": created_fs.name,
                        "type": created_fs.type,
                        "icon": created_fs.icon,
                    }
                }
            except ValidationError as exc:
                logger = logging.getLogger(__name__)
                logger.warning("Invalid fund source data: %s", str(exc))
                return {
                    "reply": "Maaf, data sumber uang tidak valid atau kurang lengkap."
                }

    if result.get("action") == "set_budget":
        budget_data = result.get("budget")
        if budget_data:
            try:
                # Ensure valid month format or default
                month = _normalize_month(budget_data.get("month"))
                amount = float(budget_data.get("amount", 0.0))
                
                created_budget = await budget_service.set_budget(
                    db,
                    BudgetCreate(month=month, amount=amount)
                )
                reply = result.get("reply", f"Anggaran bulanan sebesar Rp {amount:,.0f} berhasil disimpan untuk bulan {month}.").replace(",", ".")
                return {
                    "action": "set_budget_success",
                    "reply": reply,
                    "data": created_budget.model_dump()
                }
            except (ValidationError, ValueError) as exc:
                logger = logging.getLogger(__name__)
                logger.warning("Invalid budget data: %s", str(exc))
                return {
                    "reply": "Maaf, nominal atau format bulan anggaran tidak valid."
                }

    if result.get("action") == "set_category_budget":
        cb_data = result.get("category_budget")
        if cb_data:
            try:
                month = _normalize_month(cb_data.get("month"))
                category_name = cb_data.get("category_name")
                amount = float(cb_data.get("amount", 0.0))
                
                # Check category exists (or match case)
                all_cats = await category_service.get_categories(db)
                matched_cat = next((c for c in all_cats if c.name.lower() == category_name.lower()), None)
                if not matched_cat:
                    # Create the category automatically or return error? Let's just use the name they asked
                    pass
                else:
                    category_name = matched_cat.name
                
                created_cb = await budget_service.set_category_budget(
                    db,
                    CategoryBudgetCreate(month=month, category_name=category_name, amount=amount)
                )
                reply = result.get("reply", f"Anggaran kategori {category_name} sebesar Rp {amount:,.0f} berhasil disimpan untuk bulan {month}.").replace(",", ".")
                return {
                    "action": "set_category_budget_success",
                    "reply": reply,
                    "data": created_cb.model_dump()
                }
            except (ValidationError, ValueError) as exc:
                logger = logging.getLogger(__name__)
                logger.warning("Invalid category budget data: %s", str(exc))
                return {
                    "reply": "Maaf, nominal atau format anggaran kategori tidak valid."
                }

    if result.get("action") == "update_greeting":
        new_greeting = result.get("greeting")
        if new_greeting and auth_db and current_user:
            try:
                from backend.repositories import user_repository
            except ModuleNotFoundError:
                from repositories import user_repository
                
            user = await user_repository.get_by_id(auth_db, int(current_user.sub))
            if user:
                user.preferred_greeting = new_greeting
                auth_db.add(user)
                await auth_db.commit()
                
                reply = result.get("reply", f"Sapaan berhasil diubah menjadi {new_greeting}.")
                return {
                    "action": "update_greeting_success",
                    "reply": reply,
                    "data": {"greeting": new_greeting}
                }

    return {
        "reply": result.get("reply", "Maaf, saya belum dapat memproses permintaan Anda."),
    }


async def handle_image_message(
    db: AsyncSession,
    image_bytes: bytes,
    mime_type: str,
    message: str = "",
    nickname: str | None = None,
    greeting: str | None = None,
    fund_sources: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Process an image message and persist transactions when extraction succeeds."""

    categories = await category_service.get_categories(db)

    result = await gemini_service.process_image(image_bytes, mime_type, message, nickname, greeting, categories)

    if result.get("is_transaction") and result.get("transactions"):
        saved_transactions: list[TransactionResponse] = []
        for tx_item in result["transactions"]:
            try:
                transaction_data = _normalize_transaction_payload(tx_item)
                # Ensure we have a fund_source_id for images, fallback to the first available if not specified
                if fund_sources and len(fund_sources) > 0:
                    transaction_data["fund_source_id"] = fund_sources[0]["id"]
                else:
                    transaction_data["fund_source_id"] = 1  # Fallback
                    
                tx_create = TransactionCreate(**transaction_data)
                transaction = await transaction_repository.create(db, tx_create)
                saved_transactions.append(TransactionResponse.model_validate(transaction))
            except (KeyError, TypeError, ValidationError):
                pass

        if saved_transactions:
            return _build_transaction_reply(result, saved_transactions)

        return {
            "reply": result.get(
                "reply",
                "Maaf, detail transaksi pada gambar belum cukup jelas untuk dicatat.",
            ),
        }

    return {
        "reply": result.get("reply", "Maaf, transaksi tidak dapat diekstrak dari gambar tersebut."),
    }
