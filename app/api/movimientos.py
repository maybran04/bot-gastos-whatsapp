from app.services import movimiento_service

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas.movimiento import MovimientoCreate

from pydantic import BaseModel

from app.services.interpretador_service import interpretar_mensaje
from app.services.bot_service import procesar_mensaje

class MensajeRequest(BaseModel):
    mensaje: str

router = APIRouter(
    prefix="/movimientos",
    tags=["Movimientos"],
)


@router.post("/")
def crear_movimiento(
    movimiento: MovimientoCreate,
    db: Session = Depends(get_db),
):
    nuevo_movimiento = movimiento_service.crear_movimiento(
        db=db,
        movimiento=movimiento,
    )

    return {
        "mensaje": "Movimiento registrado correctamente",
        "movimiento": nuevo_movimiento,
    }

@router.get("/")
def listar_movimientos(
    tipo: str | None = None,
    categoria: str | None = None,
    mes: int | None = None,
    anio: int | None = None,
    db: Session = Depends(get_db),
):
    movimientos = movimiento_service.listar_movimientos(
        db=db,
        tipo=tipo,
        categoria=categoria,
        mes=mes,
        anio=anio,
    )

    return {
        "cantidad": len(movimientos),
        "movimientos": movimientos,
    }



@router.delete("/{movimiento_id}")
def eliminar_movimiento(
    movimiento_id: int,
    db: Session = Depends(get_db),
):
    id_eliminado = movimiento_service.eliminar_movimiento(
        db=db,
        movimiento_id=movimiento_id,
    )

    return {
        "mensaje": "Movimiento eliminado correctamente",
        "id": id_eliminado,
    }

@router.get("/resumen/general")
def obtener_resumen(
    mes: int | None = None,
    anio: int | None = None,
    db: Session = Depends(get_db),
):
    return movimiento_service.obtener_resumen_general(
        db=db,
        mes=mes,
        anio=anio,
    )

@router.get("/resumen/categorias")
def obtener_resumen_por_categoria(
    mes: int | None = None,
    anio: int | None = None,
    db: Session = Depends(get_db),
):
    return movimiento_service.obtener_resumen_categorias(
        db=db,
        mes=mes,
        anio=anio,
    )

@router.get("/{movimiento_id}")
def obtener_movimiento(
    movimiento_id: int,
    db: Session = Depends(get_db),
):
    return movimiento_service.obtener_movimiento(
        db=db,
        movimiento_id=movimiento_id,
    )

@router.post("/interpretar")
def interpretar(
    request: MensajeRequest,
):
    try:
        resultado = interpretar_mensaje(
            request.mensaje
        )

        return {
            "mensaje_original": request.mensaje,
            "interpretacion": resultado,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

@router.post("/mensaje")
def recibir_mensaje(
    request: MensajeRequest,
    db: Session = Depends(get_db),
):
    try:
        return procesar_mensaje(
            db=db,
            mensaje=request.mensaje,
        )

    except ValueError:
        return {
            "respuesta":"No pude determinar si es un gasto o un ingreso",
            "intencion":"no_reconocida",
        }