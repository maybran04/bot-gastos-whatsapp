import re
import unicodedata
from decimal import Decimal, InvalidOperation

from app.core.enums import Categoria, MedioPago, TipoMovimiento


PALABRAS_INGRESO = [
    "ingreso",
    "cobre",
    "cobro",
    "sueldo",
    "salario",
    "me pagaron",
]

PALABRAS_GASTO = [
    "gasto",
    "gaste",
    "pague",
    "compre",
    "compra",
]

CATEGORIAS = {
    Categoria.SUPERMERCADO: [
        "supermercado",
        "super",
        "carrefour",
        "changomas",
        "vea",
    ],
    Categoria.TRANSPORTE: [
        "nafta",
        "combustible",
        "uber",
        "taxi",
        "colectivo",
        "transporte",
    ],
    Categoria.COMIDA: [
        "pizza",
        "hamburguesa",
        "restaurante",
        "comida",
        "delivery",
    ],
    Categoria.SERVICIOS: [
        "internet",
        "luz",
        "gas",
        "agua",
        "telefono",
        "netflix",
    ],
    Categoria.SALUD: [
        "farmacia",
        "medico",
        "remedio",
        "medicamento",
        "salud",
    ],
    Categoria.EDUCACION: [
        "facultad",
        "curso",
        "libro",
        "educacion",
    ],
    Categoria.ENTRETENIMIENTO: [
        "cine",
        "juego",
        "salida",
        "entretenimiento",
    ],
    Categoria.ROPA: [
        "ropa",
        "remera",
        "pantalon",
        "zapatillas",
    ],
    Categoria.SUELDO: [
        "sueldo",
        "salario",
    ],
}


MEDIOS_PAGO = {
    MedioPago.EFECTIVO: [
        "efectivo",
    ],
    MedioPago.DEBITO: [
        "debito",
    ],
    MedioPago.CREDITO: [
        "credito",
        "tarjeta de credito",
    ],
    MedioPago.TRANSFERENCIA: [
        "transferencia",
        "transferi",
    ],
    MedioPago.BILLETERA_VIRTUAL: [
        "mercado pago",
        "mercadopago",
        "mp",
        "uala",
    ],
}


def normalizar_texto(texto: str) -> str:
    texto = texto.lower().strip()

    texto = "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", texto)
        if unicodedata.category(caracter) != "Mn"
    )

    return texto


def detectar_tipo(texto: str) -> TipoMovimiento:
    for palabra in PALABRAS_INGRESO:
        if palabra in texto:
            return TipoMovimiento.INGRESO

    for palabra in PALABRAS_GASTO:
        if palabra in texto:
            return TipoMovimiento.GASTO

    raise ValueError(
        "No pude determinar si es un gasto o un ingreso"
    )


def detectar_monto(texto: str) -> Decimal:
    patron = r"\b(\d+(?:[.,]\d+)?)\s*(mil|lucas|luca|k)?\b"

    coincidencia = re.search(patron, texto)

    if not coincidencia:
        raise ValueError(
            "No pude encontrar un monto válido"
        )

    numero = coincidencia.group(1)
    multiplicador = coincidencia.group(2)

    numero = numero.replace(",", ".")

    try:
        monto = Decimal(numero)
    except InvalidOperation:
        raise ValueError(
            "El monto no es válido"
        )

    if multiplicador in ["mil", "lucas", "luca", "k"]:
        monto *= 1000

    if monto <= 0:
        raise ValueError(
            "El monto debe ser mayor que cero"
        )

    return monto


def detectar_categoria(texto: str) -> Categoria:
    for categoria, palabras in CATEGORIAS.items():
        for palabra in palabras:
            if palabra in texto:
                return categoria

    return Categoria.OTROS


def detectar_medio_pago(
    texto: str,
) -> MedioPago | None:
    for medio, palabras in MEDIOS_PAGO.items():
        for palabra in palabras:
            if palabra in texto:
                return medio

    return None


def interpretar_mensaje(mensaje: str) -> dict:
    texto = normalizar_texto(mensaje)

    tipo = detectar_tipo(texto)
    monto = detectar_monto(texto)
    categoria = detectar_categoria(texto)
    medio_pago = detectar_medio_pago(texto)

    return {
        "tipo": tipo.value,
        "monto": monto,
        "categoria": categoria.value,
        "descripcion": mensaje.strip(),
        "medio_pago": (
            medio_pago.value
            if medio_pago
            else None
        ),
    }