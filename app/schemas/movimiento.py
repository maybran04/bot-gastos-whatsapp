from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.core.enums import Categoria, MedioPago, TipoMovimiento

class MovimientoCreate(BaseModel):
    tipo: TipoMovimiento
    monto: Decimal = Field(gt=0)
    categoria: Categoria
    descripcion: str | None = Field(
        default=None,
        max_length=200,
    )
    medio_pago: MedioPago | None = None
    fecha: datetime | None = None