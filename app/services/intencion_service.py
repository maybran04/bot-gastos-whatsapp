import unicodedata


def normalizar_texto(texto: str) -> str:
    texto = texto.lower().strip()

    return "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", texto)
        if unicodedata.category(caracter) != "Mn"
    )


def detectar_intencion(mensaje: str) -> str:
    texto = normalizar_texto(mensaje)

    palabras_consulta = [
        "cuanto gaste",
        "cuanto cobre",
        "cuanto tengo",
        "mi saldo",
        "saldo",
        "resumen",
        "en que gaste",
        "gaste mas",
    ]

    for expresion in palabras_consulta:
        if expresion in texto:
            return "consulta"

    return "registrar"