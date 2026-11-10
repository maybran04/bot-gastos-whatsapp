import os

from sqlalchemy.orm import Session

from app.schemas.movimiento import MovimientoCreate
from app.services import movimiento_service
from app.services.interpretador_service import interpretar_mensaje
from app.services.intencion_service import detectar_intencion
from app.services.periodo_service import detectar_periodo

def obtener_url_publica() -> str:
    url_configurada = os.getenv("PUBLIC_BASE_URL")

    if url_configurada:
        return url_configurada.rstrip("/")

    codespace_name = os.getenv("CODESPACE_NAME")
    forwarding_domain = os.getenv(
        "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN"
    )

    if codespace_name and forwarding_domain:
        return (
            f"https://{codespace_name}-8000."
            f"{forwarding_domain}"
        )

    return "http://127.0.0.1:8000"

def formatear_moneda(valor) -> str:
    texto = f"{valor:,.2f}"

    return (
        texto
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


EMOJIS_CATEGORIA = {
    "supermercado": "🛒",
    "transporte": "🚗",
    "comida": "🍔",
    "servicios": "💡",
    "salud": "💊",
    "educacion": "📚",
    "entretenimiento": "🎬",
    "ropa": "👕",
    "sueldo": "💰",
    "otros": "📦",
}


def procesar_mensaje(
    db: Session,
    mensaje: str,
) -> dict:

    intencion = detectar_intencion(mensaje)

    if intencion == "exportar_excel":
        url_base = obtener_url_publica()

        url_excel = (
            f"{url_base}/movimientos/exportar/excel"
        )

        return {
            "respuesta": (
                "📊 Tu archivo Excel está listo:\n\n"
                f"{url_excel}\n\n"
                "Tocá el enlace para descargarlo."
            ),
            "intencion": "exportar_excel",
            "url": url_excel,
        }

    # RESUMEN POR CATEGORÍAS
    if intencion == "consulta_categorias":
        fecha_desde, fecha_hasta, periodo = detectar_periodo(
            mensaje
        )

        resumen = movimiento_service.obtener_resumen_categorias(
            db=db,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )

        categorias = resumen["categorias"]

        if not categorias:
            return {
                "respuesta": (
                    f"📊 No encontré gastos registrados "
                    f"para {periodo}."
                ),
                "intencion": "consulta_categorias",
                "periodo": periodo,
                "resumen": resumen,
            }

        lineas = []
        total_gastos = 0

        for item in categorias:
            categoria = item["categoria"]
            total = item["total"]

            emoji = EMOJIS_CATEGORIA.get(
                categoria,
                "📦",
            )

            lineas.append(
                f"{emoji} {categoria.capitalize()}: "
                f"${formatear_moneda(total)}"
            )

            total_gastos += total

        respuesta = (
            f"📊 Gastos por categoría - {periodo}\n\n"
            + "\n".join(lineas)
            + f"\n\n💸 Total: ${formatear_moneda(total_gastos)}"
        )

        return {
            "respuesta": respuesta,
            "intencion": "consulta_categorias",
            "periodo": periodo,
            "resumen": resumen,
        }

    # RESUMEN GENERAL
    if intencion == "consulta":
        fecha_desde, fecha_hasta, periodo = detectar_periodo(
            mensaje
        )

        resumen = movimiento_service.obtener_resumen_general(
            db=db,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )

        return {
            "respuesta": (
                f"📊 Resumen de {periodo}\n\n"
                f"💰 Ingresos: "
                f"${formatear_moneda(resumen['total_ingresos'])}\n"
                f"💸 Gastos: "
                f"${formatear_moneda(resumen['total_gastos'])}\n"
                f"💵 Saldo: "
                f"${formatear_moneda(resumen['saldo'])}\n"
                f"📝 Movimientos: "
                f"{resumen['cantidad_movimientos']}"
            ),
            "intencion": "consulta",
            "periodo": periodo,
            "resumen": resumen,
        }

    # REGISTRO DE MOVIMIENTO
    datos = interpretar_mensaje(mensaje)

    movimiento_create = MovimientoCreate(
        **datos
    )

    movimiento = movimiento_service.crear_movimiento(
        db=db,
        movimiento=movimiento_create,
    )

    return {
        "respuesta": "Movimiento registrado correctamente",
        "intencion": "registrar",
        "movimiento": {
            "id": movimiento.id,
            "tipo": movimiento.tipo,
            "monto": movimiento.monto,
            "categoria": movimiento.categoria,
            "descripcion": movimiento.descripcion,
            "medio_pago": movimiento.medio_pago,
            "fecha": movimiento.fecha,
        },
    }