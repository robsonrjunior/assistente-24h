import os
from typing import Any

import requests
from dotenv import load_dotenv


load_dotenv()


def _get_evolution_send_endpoint() -> str:
    endpoint = os.getenv("EVOLUTION_SEND_MESSAGE_ENDPOINT", "").strip()
    if not endpoint:
        raise ValueError("EVOLUTION_SEND_MESSAGE_ENDPOINT nao configurado")
    return endpoint


def _get_evolution_instance_name() -> str:
    return os.getenv("EVOLUTION_INSTANCE_NAME", "").strip()


def _build_send_text_endpoint(raw_endpoint: str, instance_name: str) -> str:
    if "{instanceName}" in raw_endpoint:
        if not instance_name:
            raise ValueError("EVOLUTION_INSTANCE_NAME nao configurado")
        return raw_endpoint.replace("{instanceName}", instance_name)

    if "/message/sendText" in raw_endpoint:
        return raw_endpoint

    if instance_name:
        return f"{raw_endpoint.rstrip('/')}/message/sendText/{instance_name}"

    return raw_endpoint


def _get_evolution_api_token() -> str:
    token = os.getenv("EVOLUTION_API_TOKEN", "").strip()
    if not token:
        raise ValueError("EVOLUTION_API_TOKEN nao configurado")
    return token


def send_text_message(number: str, text: str) -> dict[str, Any]:
    """Sends a text message using the Evolution API endpoint."""
    raw_endpoint = _get_evolution_send_endpoint()
    instance_name = _get_evolution_instance_name()
    endpoint = _build_send_text_endpoint(raw_endpoint=raw_endpoint, instance_name=instance_name)
    token = _get_evolution_api_token()
    payload = {
        "number": number,
        "text": text,
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "apikey": token,
    }

    response = requests.post(endpoint, json=payload, headers=headers, timeout=15)
    response.raise_for_status()

    try:
        return response.json()
    except ValueError:
        return {"status": "ok", "raw_response": response.text}
