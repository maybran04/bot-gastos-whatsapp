import os

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
async def recibir_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    payload = await request.json()

    print("WEBHOOK RECIBIDO:")
    print(payload)

    try:
        entry = payload["entry"][0]
        change = entry["changes"][0]
        value = change["value"]

        messages = value.get("messages")

        if not messages:
            return {
                "estado": "ignorado",
                "motivo": "El webhook no contiene un mensaje",
            }

        message = messages[0]

        numero_usuario = message.get("from")
        tipo_mensaje = message.get("type")

        if tipo_mensaje != "text":
            return {
                "estado": "ignorado",
                "motivo": f"Tipo de mensaje no soportado: {tipo_mensaje}",
            }

        texto = message["text"]["body"]

        print("TEXTO RECIBIDO:", texto)

        try:
            resultado = procesar_mensaje(
                db=db,
                mensaje=texto,
            )

            return {
                "estado": "procesado",
                "usuario": numero_usuario,
                "mensaje": texto,
                "resultado": resultado,
            }

        except ValueError as error:
            print("MENSAJE NO PROCESADO:", str(error))

            return {
                "estado": "no_procesado",
                "usuario": numero_usuario,
                "mensaje": texto,
                "motivo": str(error),
            }

    except (KeyError, IndexError, TypeError) as error:
        return {
            "estado": "ignorado",
            "motivo": f"Estructura de webhook no reconocida: {error}",
        }