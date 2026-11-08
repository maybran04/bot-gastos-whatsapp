import os
import httpx

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.services.bot_service import procesar_mensaje


router = APIRouter(
    prefix="/whatsapp",
    tags=["WhatsApp"],
)


VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
N8N_WEBHOOK_URL = os.getenv(
    "N8N_WEBHOOK_URL",
    "http://127.0.0.1:5678/webhook/whatsapp-verificacion",
)

@router.get("/webhook")
def verificar_webhook(
    request: Request,
):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    print(
        "VERIFICACION META:",
        {
            "mode": mode,
            "token_correcto": token == VERIFY_TOKEN,
            "challenge_recibido": bool(challenge),
        },
    )

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(
            content=challenge,
            status_code=200,
        )

    raise HTTPException(
        status_code=403,
        detail="Token de verificación incorrecto",
    )
@router.post("/webhook")
async def recibir_webhook(request: Request):
    payload = await request.json()

    print("WEBHOOK META RECIBIDO:")
    print(payload)

    async with httpx.AsyncClient() as client:
        respuesta = await client.post(
            N8N_WEBHOOK_URL,
            json=payload,
            timeout=10.0,
        )

    respuesta.raise_for_status()

    return {
        "estado": "reenviado_a_n8n",
        "status_n8n": respuesta.status_code,
    }