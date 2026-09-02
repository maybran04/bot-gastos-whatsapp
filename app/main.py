from fastapi import FastAPI

from app.api.movimientos import router as movimientos_router
from app.database.database import Base, engine
from app.models.movimiento import Movimiento

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bot de gastos",
    description="API para administrar ingresos y gastos personales",
    version="0.1.0",
)


app.include_router(movimientos_router)


@app.get("/")
def inicio() -> dict[str, str]:
    return {
        "mensaje": "El bot de gastos está funcionando"
    }


@app.get("/health")
def verificar_estado() -> dict[str, str]:
    return {
        "estado": "ok"
    }