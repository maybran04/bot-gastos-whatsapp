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
    palabras_exportar = [
        "exportar excel",
        "descargar excel",
        "archivo excel",
        "excel",
    ]

    for expresion in palabras_exportar:
        if expresion in texto:
            return "exportar_excel"

    palabras_categorias = [
        "categorias",
        "categoria",
        "en que gaste",
        "gastos por categoria",
        "gastos por categorias",
    ]

    for expresion in palabras_categorias:
        if expresion in texto:
            return "consulta_categorias"

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