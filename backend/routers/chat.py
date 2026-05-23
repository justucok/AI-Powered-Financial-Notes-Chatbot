from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.database import get_db
    from backend.schemas.chat import ChatMessageRequest
    from backend.services import chat_service
except ModuleNotFoundError:
    from database import get_db
    from schemas.chat import ChatMessageRequest
    from services import chat_service


router = APIRouter(tags=["chat"])


@router.post("/chat")
async def post_chat(
    payload: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Handle text chat requests."""

    result = await chat_service.handle_text_message(db, payload.message, payload.history)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)


@router.post("/chat/image")
async def post_chat_image(
    file: UploadFile = File(...),
    message: Annotated[str, Form()] = "",
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Handle image chat requests."""

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File must be an image.",
        )

    image_bytes = await file.read()
    result = await chat_service.handle_image_message(db, image_bytes, file.content_type, message)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
