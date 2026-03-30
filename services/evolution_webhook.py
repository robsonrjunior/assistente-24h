import hmac
import hashlib
import json
import logging
import os
from typing import Any

from dotenv import load_dotenv
from fastapi import Body, FastAPI, HTTPException, Query, status
import uvicorn

from assistant.assistant import answer_question
from database_utils.evolution_database_utils import cleanup_processed_messages, register_processed_message
from integrations.evolution_api import send_text_message


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI()

logger = logging.getLogger("evolution_webhook")

# Rota de health check
@app.get("/health")
def health_check():
    return {"status": "ok"}


def _get_processed_message_retention_days() -> int:
    raw_value = os.getenv("EVOLUTION_PROCESSED_RETENTION_DAYS", "30").strip()
    try:
        parsed_value = int(raw_value)
        return parsed_value if parsed_value > 0 else 30
    except ValueError:
        return 30


def _is_messages_upsert_event(payload: dict[str, Any]) -> bool:
    event = str(payload.get("event", "")).strip().lower()
    if not event:
        return True
    return event in {"messages.upsert", "messages_upsert", "messages-upsert", "messagesupsert"}


def _is_from_me(payload: dict[str, Any]) -> bool:
    data = payload.get("data")
    if not isinstance(data, dict):
        return False

    key = data.get("key")
    if not isinstance(key, dict):
        return False

    return bool(key.get("fromMe"))


def _extract_message_key(payload: dict[str, Any], number: str, message_text: str) -> str:
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    key = data.get("key") if isinstance(data.get("key"), dict) else {}

    instance = (
        str(payload.get("instance") or payload.get("instanceName") or data.get("instance") or "").strip()
    )
    message_id = (
        str(key.get("id") or data.get("id") or payload.get("messageId") or payload.get("id") or "").strip()
    )

    if message_id:
        return f"{instance}:{message_id}" if instance else message_id

    fingerprint_base = {
        "event": payload.get("event"),
        "number": number,
        "message": message_text,
        "timestamp": data.get("messageTimestamp") or payload.get("messageTimestamp"),
    }
    fingerprint = json.dumps(fingerprint_base, ensure_ascii=True, sort_keys=True)
    return f"fallback:{hashlib.sha256(fingerprint.encode('utf-8')).hexdigest()}"


def _validate_token(token: str) -> None:
    expected_token = os.getenv("WEBHOOK_TOKEN")
    if not expected_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="WEBHOOK_TOKEN nao configurado",
        )

    if not hmac.compare_digest(token, expected_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido",
        )


def _extract_message_data(payload: dict[str, Any]) -> tuple[str, str]:
    message_text = (
        payload.get("message")
        or payload.get("text")
        or payload.get("body")
        or payload.get("content")
    )

    number = (
        payload.get("number")
        or payload.get("phone")
        or payload.get("from")
    )

    data = payload.get("data")
    if isinstance(data, dict):
        message = data.get("message")
        if isinstance(message, dict):
            message_text = (
                message_text
                or message.get("conversation")
                or message.get("extendedTextMessage", {}).get("text")
            )

        key = data.get("key")
        if isinstance(key, dict):
            # For incoming messages from Evolution, remoteJid is the correct destination.
            number = key.get("remoteJid") or key.get("remoteJidAlt") or number

    if not number:
        number = payload.get("sender")

    if isinstance(number, str):
        number = number.split("@")[0].strip()

    if not isinstance(message_text, str) or not message_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao foi possivel identificar o texto da mensagem no payload",
        )

    if not isinstance(number, str) or not number.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao foi possivel identificar o numero de destino no payload",
        )

    return number, message_text.strip()


@app.post("/evolution/webhook")
def evolution_receive_message(
    token: str = Query(..., description="Auth token"),
    payload: dict[str, Any] = Body(..., description="Evolution webhook payload"),
):
    logger.info("Webhook request received: event=%s", payload.get("event"))
    logger.info(
        "Webhook body: %s",
        json.dumps(payload, ensure_ascii=True, sort_keys=True, default=str),
    )
    _validate_token(token)

    if not _is_messages_upsert_event(payload):
        logger.info("Event ignored: not a messages upsert event")
        return {"status": "ignored", "reason": "event_not_supported"}

    if _is_from_me(payload):
        logger.info("Event ignored: outgoing message (fromMe=true)")
        return {"status": "ignored", "reason": "outgoing_message"}

    number, message = _extract_message_data(payload)
    message_key = _extract_message_key(payload=payload, number=number, message_text=message)

    is_new_message = register_processed_message(message_key)
    if not is_new_message:
        logger.info("Event ignored: duplicate message (%s)", message_key)
        return {
            "status": "ignored",
            "reason": "duplicated_message",
            "message_key": message_key,
        }

    cleanup_processed_messages(max_age_days=_get_processed_message_retention_days())

    answer = answer_question(message)
    evolution_response = send_text_message(number=number, text=answer)
    logger.info("Message processed and sent to %s", number)

    return {
        "status": "ok",
        "answer": answer,
        "evolution_response": evolution_response,
    }


def start() -> None:
    """Starts the FastAPI server to receive Evolution webhook events."""
    port = int(os.getenv("EVOLUTION_WEBHOOK_PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    start()
