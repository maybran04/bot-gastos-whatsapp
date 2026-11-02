from sqlalchemy.orm import Session

from app.schemas.movimiento import MovimientoCreate
from app.services import movimiento_service
from app.services.interpretador_service import interpretar_mensaje
from app.services.intencion_service import detectar_intencion
from app.services.periodo_service import detectar_periodo


def procesar_mensaje(
    db: Session,
    mensaje: str,
) -> dict:

    intencion = detectar_intencion(mensaje)

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
                f"Resumen de {periodo}: "
                f"ingresos ${resumen['total_ingresos']}, "
                f"gastos ${resumen['total_gastos']} y "
                f"saldo ${resumen['saldo']}."
            ),
            "intencion": "consulta",
            "periodo": periodo,
            "resumen": resumen,
        }

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