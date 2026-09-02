from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.movimiento import Movimiento
from app.schemas.movimiento import MovimientoCreate


def crear_movimiento(
    db: Session,
    movimiento: MovimientoCreate,
) -> Movimiento:
    nuevo_movimiento = Movimiento(
        tipo=movimiento.tipo.value,
        monto=movimiento.monto,
        categoria=movimiento.categoria.value,
        descripcion=movimiento.descripcion,
        medio_pago=(
            movimiento.medio_pago.value
            if movimiento.medio_pago
            else None
        ),
        fecha=movimiento.fecha or datetime.now(),
    )

    db.add(nuevo_movimiento)
    db.commit()
    db.refresh(nuevo_movimiento)

    return nuevo_movimiento

def obtener_movimiento(
    db: Session,
    movimiento_id: int,
) -> Movimiento:
    movimiento = (
        db.query(Movimiento)
        .filter(Movimiento.id == movimiento_id)
        .first()
    )

    if movimiento is None:
        raise HTTPException(
            status_code=404,
            detail="Movimiento no encontrado",
        )

    return movimiento

def eliminar_movimiento(
    db: Session,
    movimiento_id: int,
) -> int:
    movimiento = obtener_movimiento(
        db=db,
        movimiento_id=movimiento_id,
    )

    db.delete(movimiento)
    db.commit()

    return movimiento_id

def listar_movimientos(
    db: Session,
    tipo: str | None = None,
    categoria: str | None = None,
    mes: int | None = None,
    anio: int | None = None,
) -> list[Movimiento]:
    query = db.query(Movimiento)

    if tipo:
        query = query.filter(
            Movimiento.tipo == tipo
        )

    if categoria:
        query = query.filter(
            Movimiento.categoria == categoria
        )

    if mes is not None:
        if mes < 1 or mes > 12:
            raise HTTPException(
                status_code=400,
                detail="El mes debe estar entre 1 y 12",
            )

        anio_consulta = anio or datetime.now().year

        fecha_inicio = datetime(
            anio_consulta,
            mes,
            1,
        )

        if mes == 12:
            fecha_fin = datetime(
                anio_consulta + 1,
                1,
                1,
            )
        else:
            fecha_fin = datetime(
                anio_consulta,
                mes + 1,
                1,
            )

        query = query.filter(
            Movimiento.fecha >= fecha_inicio,
            Movimiento.fecha < fecha_fin,
        )

    elif anio is not None:
        fecha_inicio = datetime(anio, 1, 1)
        fecha_fin = datetime(anio + 1, 1, 1)

        query = query.filter(
            Movimiento.fecha >= fecha_inicio,
            Movimiento.fecha < fecha_fin,
        )

    return query.all()

def obtener_resumen_general(
    db: Session,
    mes: int | None = None,
    anio: int | None = None,
) -> dict:
    movimientos = listar_movimientos(
        db=db,
        mes=mes,
        anio=anio,
    )

    total_ingresos = sum(
        movimiento.monto
        for movimiento in movimientos
        if movimiento.tipo == "ingreso"
    )

    total_gastos = sum(
        movimiento.monto
        for movimiento in movimientos
        if movimiento.tipo == "gasto"
    )

    saldo = total_ingresos - total_gastos

    return {
        "mes": mes,
        "anio": anio,
        "total_ingresos": total_ingresos,
        "total_gastos": total_gastos,
        "saldo": saldo,
        "cantidad_movimientos": len(movimientos),
    }

def obtener_resumen_categorias(
    db: Session,
    mes: int | None = None,
    anio: int | None = None,
) -> dict:
    movimientos = listar_movimientos(
        db=db,
        tipo="gasto",
        mes=mes,
        anio=anio,
    )

    resumen: dict[str, Decimal] = {}

    for movimiento in movimientos:
        categoria = movimiento.categoria

        if categoria not in resumen:
            resumen[categoria] = Decimal("0")

        resumen[categoria] += movimiento.monto

    categorias_ordenadas = sorted(
        resumen.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return {
        "mes": mes,
        "anio": anio,
        "categorias": [
            {
                "categoria": categoria,
                "total": total,
            }
            for categoria, total in categorias_ordenadas
        ],
    }
