from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Movimiento(Base):
    __tablename__ = "movimientos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    tipo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    monto: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    categoria: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    descripcion: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    medio_pago: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    fecha: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )