from io import BytesIO
from decimal import Decimal

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import BarChart, Reference


def generar_excel_movimientos(movimientos):
    workbook = Workbook()

    # ==================================================
    # HOJA 1: MOVIMIENTOS
    # ==================================================

    hoja_movimientos = workbook.active
    hoja_movimientos.title = "Movimientos"

    encabezados = [
        "ID",
        "Tipo",
        "Monto",
        "Categoría",
        "Descripción",
        "Medio de pago",
        "Fecha",
    ]

    hoja_movimientos.append(encabezados)

    # Estilo de encabezados
    relleno_encabezado = PatternFill(
        fill_type="solid",
        fgColor="1F4E78",
    )

    fuente_encabezado = Font(
        bold=True,
        color="FFFFFF",
    )

    for celda in hoja_movimientos[1]:
        celda.font = fuente_encabezado
        celda.fill = relleno_encabezado
        celda.alignment = Alignment(
            horizontal="center"
        )

    for movimiento in movimientos:
        hoja_movimientos.append([
            movimiento.id,
            movimiento.tipo,
            float(movimiento.monto),
            movimiento.categoria,
            movimiento.descripcion,
            movimiento.medio_pago,
            movimiento.fecha,
        ])

    # Colores para ingresos y gastos
    relleno_ingreso = PatternFill(
        fill_type="solid",
        fgColor="E2F0D9",
    )

    relleno_gasto = PatternFill(
        fill_type="solid",
        fgColor="FCE4D6",
    )

    for fila in hoja_movimientos.iter_rows(
        min_row=2,
        max_row=hoja_movimientos.max_row,
    ):
        tipo = fila[1].value

        if tipo == "ingreso":
            for celda in fila:
                celda.fill = relleno_ingreso

        elif tipo == "gasto":
            for celda in fila:
                celda.fill = relleno_gasto

    # Formato moneda
    for celda in hoja_movimientos["C"][1:]:
        celda.number_format = '$#,##0.00'

    # Formato fecha
    for celda in hoja_movimientos["G"][1:]:
        celda.number_format = "dd/mm/yyyy hh:mm"

    # Anchos
    hoja_movimientos.column_dimensions["A"].width = 8
    hoja_movimientos.column_dimensions["B"].width = 15
    hoja_movimientos.column_dimensions["C"].width = 15
    hoja_movimientos.column_dimensions["D"].width = 20
    hoja_movimientos.column_dimensions["E"].width = 35
    hoja_movimientos.column_dimensions["F"].width = 20
    hoja_movimientos.column_dimensions["G"].width = 20

    # Mantener encabezado visible al desplazarse
    hoja_movimientos.freeze_panes = "A2"

    # Filtros automáticos
    hoja_movimientos.auto_filter.ref = (
        hoja_movimientos.dimensions
    )


    # ==================================================
    # CÁLCULOS DEL RESUMEN
    # ==================================================

    total_ingresos = sum(
        (
            movimiento.monto
            for movimiento in movimientos
            if movimiento.tipo == "ingreso"
        ),
        Decimal("0"),
    )

    total_gastos = sum(
        (
            movimiento.monto
            for movimiento in movimientos
            if movimiento.tipo == "gasto"
        ),
        Decimal("0"),
    )

    saldo = total_ingresos - total_gastos

    categorias = {}

    for movimiento in movimientos:
        if movimiento.tipo != "gasto":
            continue

        categoria = movimiento.categoria

        if categoria not in categorias:
            categorias[categoria] = Decimal("0")

        categorias[categoria] += movimiento.monto

    categorias_ordenadas = sorted(
        categorias.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    # ==================================================
    # HOJA 2: RESUMEN
    # ==================================================

    hoja_resumen = workbook.create_sheet(
        title="Resumen"
    )

    hoja_resumen["A1"] = "Resumen de movimientos"
    hoja_resumen["A1"].font = Font(
        bold=True,
        size=16,
        color="1F4E78",
    )

    hoja_resumen["A3"] = "Total ingresos"
    hoja_resumen["B3"] = float(total_ingresos)

    hoja_resumen["A4"] = "Total gastos"
    hoja_resumen["B4"] = float(total_gastos)

    hoja_resumen["A5"] = "Saldo"
    hoja_resumen["B5"] = float(saldo)

    hoja_resumen["A6"] = "Cantidad de movimientos"
    hoja_resumen["B6"] = len(movimientos)

    for fila in range(3, 7):
        hoja_resumen[f"A{fila}"].font = Font(
            bold=True
        )

    # Formato moneda
    for fila in [3, 4, 5]:
        hoja_resumen[f"B{fila}"].number_format = '$#,##0.00'

    # Resaltar saldo
    if saldo >= 0:
        hoja_resumen["B5"].fill = PatternFill(
            fill_type="solid",
            fgColor="E2F0D9",
        )
    else:
        hoja_resumen["B5"].fill = PatternFill(
            fill_type="solid",
            fgColor="FCE4D6",
        )

    # ==================================================
    # GASTOS POR CATEGORÍA
    # ==================================================

    hoja_resumen["A9"] = "Gastos por categoría"
    hoja_resumen["A9"].font = Font(
        bold=True,
        size=14,
    )

    hoja_resumen["A10"] = "Categoría"
    hoja_resumen["B10"] = "Total"

    hoja_resumen["A10"].font = Font(bold=True)
    hoja_resumen["B10"].font = Font(bold=True)

    fila = 11

    for categoria, total in categorias_ordenadas:
        hoja_resumen[f"A{fila}"] = categoria.capitalize()
        hoja_resumen[f"B{fila}"] = float(total)

        hoja_resumen[f"B{fila}"].number_format = '$#,##0.00'

        fila += 1

    # ==================================================
    # GRÁFICO DE GASTOS POR CATEGORÍA
    # ==================================================

    if categorias_ordenadas:
        grafico = BarChart()

        grafico.type = "bar"
        grafico.style = 10

        grafico.title = "Gastos por categoría"
        grafico.x_axis.title = "Monto"
        grafico.y_axis.title = "Categoría"

        datos = Reference(
            hoja_resumen,
            min_col=2,
            min_row=10,
            max_row=fila - 1,
        )

        categorias_grafico = Reference(
            hoja_resumen,
            min_col=1,
            min_row=11,
            max_row=fila - 1,
        )

        grafico.add_data(
            datos,
            titles_from_data=True,
        )

        grafico.set_categories(
            categorias_grafico
        )

        grafico.height = 8
        grafico.width = 14

        hoja_resumen.add_chart(
            grafico,
            "D3",
        )

    hoja_resumen.column_dimensions["A"].width = 30
    hoja_resumen.column_dimensions["B"].width = 20

    hoja_resumen.freeze_panes = "A3"

    # ==================================================
    # GENERAR ARCHIVO
    # ==================================================

    archivo = BytesIO()

    workbook.save(archivo)
    archivo.seek(0)

    return archivo