from enum import Enum


class TipoMovimiento(str, Enum):
    GASTO = "gasto"
    INGRESO = "ingreso"


class Categoria(str, Enum):
    SUPERMERCADO = "supermercado"
    TRANSPORTE = "transporte"
    COMIDA = "comida"
    SERVICIOS = "servicios"
    SALUD = "salud"
    EDUCACION = "educacion"
    ENTRETENIMIENTO = "entretenimiento"
    ROPA = "ropa"
    SUELDO = "sueldo"
    OTROS = "otros"


class MedioPago(str, Enum):
    EFECTIVO = "efectivo"
    DEBITO = "debito"
    CREDITO = "credito"
    TRANSFERENCIA = "transferencia"
    BILLETERA_VIRTUAL = "billetera_virtual"