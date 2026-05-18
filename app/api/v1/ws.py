import json
import logging
from contextlib import suppress

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.api.deps import get_current_user_ws
from app.core.exceptions import AppException
from app.core.ws_manager import manager
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.message import (
    MessageRead,
    WSError,
    WSMessageIn,
    WSMessageOut,
)
from app.services.messaging import MessagingService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    current_user: User = Depends(get_current_user_ws),
) -> None:
    await websocket.accept()
    await manager.connect(current_user.id, websocket)

    try:
        while True:
            raw = await websocket.receive_text()

            try:
                data = json.loads(raw)
                incoming = WSMessageIn.model_validate(data)
            except (json.JSONDecodeError, ValidationError) as exc:
                await _send_error(
                    websocket,
                    code="INVALID_PAYLOAD",
                    message=f"Format de message invalide : {exc}",
                )
                continue

            try:
                with SessionLocal() as db:
                    service = MessagingService(db)
                    created, recipient_id = service.send_message(
                        conversation_id=incoming.conversation_id,
                        sender_id=current_user.id,
                        content=incoming.content,
                    )
                    message_read = MessageRead.model_validate(created)
            except AppException as exc:
                await _send_error(
                    websocket,
                    code=exc.__class__.__name__,
                    message=str(exc),
                )
                continue
            except Exception:
                logger.exception("Erreur inattendue lors du traitement d'un message WS")
                await _send_error(
                    websocket,
                    code="INTERNAL_ERROR",
                    message="Erreur interne du serveur.",
                )
                continue

            outgoing = WSMessageOut(
                conversation_id=incoming.conversation_id,
                message=message_read,
            )
            await manager.send_to_user(current_user.id, outgoing)
            await manager.send_to_user(recipient_id, outgoing)

    except WebSocketDisconnect:
        pass
    except Exception:
        logger.exception("Erreur fatale sur la connexion WebSocket")
    finally:
        await manager.disconnect(current_user.id, websocket)


async def _send_error(websocket: WebSocket, code: str, message: str) -> None:
    err = WSError(code=code, message=message)
    with suppress(Exception):
        await websocket.send_text(err.model_dump_json())
