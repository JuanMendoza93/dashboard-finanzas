import pandas as pd
import io

def generar_reporte_excel(df_movimientos, mes, año):
    df_filtrado = df_movimientos[
        (df_movimientos["fecha"].str.startswith(f"{año}-{mes:02d}"))
    ]

    ingresos = df_filtrado[df_filtrado["tipo"] == "Ingreso"]["monto"].sum()
    gastos = df_filtrado[df_filtrado["tipo"] == "Gasto"]["monto"].sum()
    ahorro = ingresos - gastos

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        pd.DataFrame({
            "Concepto": ["Ingresos", "Gastos", "Ahorro"],
            "Monto": [ingresos, gastos, ahorro]
        }).to_excel(writer, sheet_name="Resumen", index=False)

    return output.getvalue(), f"Reporte_{mes}_{año}.xlsx"
