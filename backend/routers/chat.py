from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.database import get_db
    from backend.dependencies.auth import get_current_user
    from backend.schemas.auth import TokenPayload
    from backend.schemas.chat import ChatMessageRequest
    from backend.services import chat_service
except ModuleNotFoundError:
    from database import get_db
    from dependencies.auth import get_current_user
    from schemas.auth import TokenPayload
    from schemas.chat import ChatMessageRequest
    from services import chat_service


router = APIRouter(tags=["chat"])


async def post_chat(
    payload: ChatMessageRequest,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Handle text chat requests (authenticated user with nickname preference)."""

    result = await chat_service.handle_text_message(
        db=db,
        message=payload.message,
        history=payload.history,
        nickname=current_user.nickname,
        greeting=current_user.preferred_greeting,
        fund_sources=payload.fund_sources,
        current_user=current_user,
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)


@router.post("/chat/image")
async def post_chat_image(
    file: UploadFile = File(...),
    message: Annotated[str, Form()] = "",
    fund_sources: Annotated[str, Form()] = "[]",
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Handle image chat requests (authenticated user with nickname preference)."""

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File must be an image.",
        )

    import json
    try:
        fund_sources_list = json.loads(fund_sources)
    except Exception:
        fund_sources_list = []

    image_bytes = await file.read()
    result = await chat_service.handle_image_message(
        db=db,
        image_bytes=image_bytes,
        mime_type=file.content_type,
        message=message,
        nickname=current_user.nickname,
        greeting=current_user.preferred_greeting,
        fund_sources=fund_sources_list,
        current_user=current_user,
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
