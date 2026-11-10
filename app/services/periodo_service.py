from datetime import datetime, timedelta
import unicodedata


MESES = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}


def normalizar_texto(texto: str) -> str:
    texto = texto.lower().strip()

    return "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", texto)
        if unicodedata.category(caracter) != "Mn"
    )


def detectar_periodo(
    mensaje: str,
) -> tuple[datetime, datetime, str]:

    texto = normalizar_texto(mensaje)
    ahora = datetime.now()

    # HOY
    if "hoy" in texto:
        desde = ahora.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        hasta = desde + timedelta(days=1)

        return desde, hasta, "hoy"

    # AYER
    if "ayer" in texto:
        hoy = ahora.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        desde = hoy - timedelta(days=1)
        hasta = hoy

        return desde, hasta, "ayer"

    # ESTA SEMANA
    if "esta semana" in texto:
        inicio_hoy = ahora.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        desde = inicio_hoy - timedelta(
            days=ahora.weekday()
        )

        hasta = ahora

        return desde, hasta, "esta semana"

    # MES PASADO
    if "mes pasado" in texto:
        if ahora.month == 1:
            anio_anterior = ahora.year - 1
            mes_anterior = 12
        else:
            anio_anterior = ahora.year
            mes_anterior = ahora.month - 1

        desde = datetime(
            anio_anterior,
            mes_anterior,
            1,
        )

        hasta = datetime(
            ahora.year,
            ahora.month,
            1,
        )

        return desde, hasta, "el mes pasado"

    # ESTE MES
    if "este mes" in texto:
        desde = datetime(
            ahora.year,
            ahora.month,
            1,
        )

        if ahora.month == 12:
            hasta = datetime(
                ahora.year + 1,
                1,
                1,
            )
        else:
            hasta = datetime(
                ahora.year,
                ahora.month + 1,
                1,
            )

        return desde, hasta, "este mes"

    # MESES POR NOMBRE
    for nombre_mes, numero_mes in MESES.items():
        if nombre_mes in texto:
            anio = ahora.year

            desde = datetime(
                anio,
                numero_mes,
                1,
            )

            if numero_mes == 12:
                hasta = datetime(
                    anio + 1,
                    1,
                    1,
                )
            else:
                hasta = datetime(
                    anio,
                    numero_mes + 1,
                    1,
                )

            return (
                desde,
                hasta,
                f"{nombre_mes} {anio}",
            )

    # DEFAULT: MES ACTUAL
    desde = datetime(
        ahora.year,
        ahora.month,
        1,
    )

    if ahora.month == 12:
        hasta = datetime(
            ahora.year + 1,
            1,
            1,
        )
    else:
        hasta = datetime(
            ahora.year,
            ahora.month + 1,
            1,
        )

    return desde, hasta, "este mes"