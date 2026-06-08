import streamlit as st
import pandas as pd
import numpy as np
import math
from typing import Dict, Tuple, Optional

# Configuración de la página (DEBE ser el primer comando de Streamlit)
st.set_page_config(page_title="Calculador de Dosis Veterinarias", layout="wide")

# ------------------------------------------------------------
# Definición de productos (igual que antes, con pequeñas correcciones)
# ------------------------------------------------------------

class Producto:
    def __init__(self, codigo, nombre, unidad, presentacion_kg, precio, tipo_producto, concentracion,
                 dosis_aves=None, dosis_cerdos=None):
        self.codigo = codigo
        self.nombre = nombre
        self.unidad = unidad          # 'kg' o 'L'
        self.presentacion_kg = presentacion_kg
        self.precio = precio
        self.tipo_producto = tipo_producto
        self.concentracion = concentracion  # mg/g o mg/ml
        self.dosis_aves = dosis_aves        # (tipo, min, max)
        self.dosis_cerdos = dosis_cerdos

def dosis(tipo, min_dosis, max_dosis):
    return (tipo, min_dosis, max_dosis)

PRODUCTOS = {
    "EC0001": Producto("EC0001", "Vitablend - Pro Gallinas/Postura Px", "kg", 25, 3.95, "Premezcla", None,
                       dosis_aves=dosis("feed", 1.0, 1.0), dosis_cerdos=None),
    "EC0002": Producto("EC0002", "Vitablend - Pro Broilers Inicio-Crecimiento-Engorde", "kg", 25, 4.40, "Premezcla", None,
                       dosis_aves=dosis("feed", 1.0, 1.0), dosis_cerdos=None),
    "EC0003": Producto("EC0003", "Vitablend - Pro Cerdos Inicio y Reproductores", "kg", 25, 4.95, "Premezcla", None,
                       dosis_aves=None, dosis_cerdos=dosis("feed", 1.0, 1.0)),
    "EC0004": Producto("EC0004", "Tilvamune 5% Premix", "kg", 25, 20.80, "Polvo Soluble", 50.0,
                       dosis_aves=dosis("pv", 500.0, 500.0), dosis_cerdos=dosis("pv", 1.0, 2.0)),
    "EC0005": Producto("EC0005", "Neomicin 50", "kg", 25, 21.90, "Polvo Soluble", 500.0,
                       dosis_aves=dosis("feed", 0.14, 0.28), dosis_cerdos=dosis("feed", 0.14, 0.28)),
    "EC0006": Producto("EC0006", "Tiamulin Premix 100", "kg", 25, 14.25, "Polvo Soluble", 100.0,
                       dosis_aves=dosis("feed", 1.0, 5.0), dosis_cerdos=dosis("feed", 1.0, 2.0)),
    "EC0007": Producto("EC0007", "Florfen 20", "L", 1, 24.80, "Antibiótico Oral", 200.0,
                       dosis_aves=dosis("pv", 20.0, 30.0), dosis_cerdos=dosis("pv", 10.0, 20.0)),
    "EC0008": Producto("EC0008", "Lincospect 11", "kg", 25, 46.10, "Polvo Soluble", 110.0,
                       dosis_aves=dosis("feed", 1.0, 1.0), dosis_cerdos=dosis("feed", 0.2, 0.4)),
    "EC0009": Producto("EC0009", "Enromune 20", "L", 1, 22.00, "Antibiótico Oral", 200.0,
                       dosis_aves=dosis("pv", 10.0, 10.0), dosis_cerdos=dosis("pv", 2.5, 5.0)),
    "EC0010": Producto("EC0010", "Clortiamune", "kg", 25, 12.50, "Polvo Soluble", 110.0,
                       dosis_aves=dosis("feed", 1.8, 4.5), dosis_cerdos=dosis("feed", 0.5, 3.6)),
    "EC0011": Producto("EC0011", "Pro-Amox", "kg", 1, 38.00, "Polvo Soluble", 500.0,
                       dosis_aves=dosis("pv", 10.0, 10.0), dosis_cerdos=dosis("pv", 10.0, 20.0)),
    "EC0012": Producto("EC0012", "Vitablend - Pro Cerdos Crecimiento Engorde", "kg", 25, 3.95, "Premezcla", None,
                       dosis_aves=None, dosis_cerdos=dosis("feed", 1.0, 1.0)),
}

# ------------------------------------------------------------
# Funciones para generar tablas de crecimiento (peso y consumo)
# ------------------------------------------------------------

def generar_tabla_broiler(dias_inicio, dias_fin):
    """Genera dataframe con pesos (kg) y consumo diario (kg) para broiler, interpolado entre días estándar."""
    # Datos de referencia: día -> peso (kg) y consumo acumulado (kg)
    # Basado en curvas típicas (Cobb 500)
    referencia = {
        0: (0.040, 0.000),    # día 0: peso 40g, consumo 0
        7: (0.180, 0.150),    # día 7: peso 180g, consumo 0.150kg
        14: (0.450, 0.550),
        21: (0.850, 1.200),
        28: (1.400, 2.000),
        35: (2.000, 2.900),
        42: (2.600, 3.900)
    }
    dias = list(range(dias_inicio, dias_fin+1))
    pesos = []
    consumos_diarios = []
    for d in dias:
        # Interpolación lineal entre los puntos de referencia
        if d in referencia:
            peso, cons_acum = referencia[d]
        else:
            # Encontrar el intervalo
            dias_ref = sorted(referencia.keys())
            for i in range(len(dias_ref)-1):
                if dias_ref[i] <= d <= dias_ref[i+1]:
                    d1, d2 = dias_ref[i], dias_ref[i+1]
                    p1, c1 = referencia[d1]
                    p2, c2 = referencia[d2]
                    peso = p1 + (p2 - p1) * (d - d1) / (d2 - d1)
                    cons_acum = c1 + (c2 - c1) * (d - d1) / (d2 - d1)
                    break
        # Consumo diario = consumo acumulado - consumo acumulado día anterior
        if d == dias_inicio:
            consumo_diario = cons_acum  # primer día
        else:
            # Buscar consumo acumulado del día anterior
            d_ant = d-1
            if d_ant in referencia:
                cons_ant = referencia[d_ant][1]
            else:
                # Interpolar también para día anterior (simplificado)
                cons_ant = None
                for i in range(len(dias_ref)-1):
                    if dias_ref[i] <= d_ant <= dias_ref[i+1]:
                        d1, d2 = dias_ref[i], dias_ref[i+1]
                        p1, c1 = referencia[d1]
                        p2, c2 = referencia[d2]
                        cons_ant = c1 + (c2 - c1) * (d_ant - d1) / (d2 - d1)
                        break
            consumo_diario = cons_acum - cons_ant if cons_ant is not None else cons_acum
        pesos.append(peso)
        consumos_diarios.append(consumo_diario)
    return pd.DataFrame({
        "Día": dias,
        "Peso (kg)": pesos,
        "Consumo (kg/día)": consumos_diarios
    })

def generar_tabla_ponedora(dias_inicio, dias_fin):
    """Ponedora adulta (peso constante ~1.5 kg, consumo 0.12 kg/día)."""
    dias = list(range(dias_inicio, dias_fin+1))
    df = pd.DataFrame({
        "Día": dias,
        "Peso (kg)": [1.5] * len(dias),
        "Consumo (kg/día)": [0.12] * len(dias)
    })
    return df

def generar_tabla_cerdo(dias_inicio, dias_fin):
    """Curva de crecimiento de cerdo de engorde (desde 20 kg hasta 110 kg en ~100 días)."""
    referencia = {
        0: (20.0, 0.00),
        30: (40.0, 60.0),
        60: (70.0, 150.0),
        90: (95.0, 240.0),
        120: (110.0, 320.0)
    }
    dias = list(range(dias_inicio, dias_fin+1))
    pesos = []
    consumos_diarios = []
    for d in dias:
        # Encontrar intervalo
        dias_ref = sorted(referencia.keys())
        for i in range(len(dias_ref)-1):
            if dias_ref[i] <= d <= dias_ref[i+1]:
                d1, d2 = dias_ref[i], dias_ref[i+1]
                p1, c1 = referencia[d1]
                p2, c2 = referencia[d2]
                peso = p1 + (p2 - p1) * (d - d1) / (d2 - d1)
                cons_acum = c1 + (c2 - c1) * (d - d1) / (d2 - d1)
                break
        if d == dias_inicio:
            consumo_diario = cons_acum
        else:
            # Obtener consumo acumulado día anterior
            d_ant = d-1
            for i in range(len(dias_ref)-1):
                if dias_ref[i] <= d_ant <= dias_ref[i+1]:
                    d1, d2 = dias_ref[i], dias_ref[i+1]
                    p1, c1 = referencia[d1]
                    p2, c2 = referencia[d2]
                    cons_ant = c1 + (c2 - c1) * (d_ant - d1) / (d2 - d1)
                    break
            consumo_diario = cons_acum - cons_ant
        pesos.append(peso)
        consumos_diarios.append(consumo_diario)
    return pd.DataFrame({
        "Día": dias,
        "Peso (kg)": pesos,
        "Consumo (kg/día)": consumos_diarios
    })

# ------------------------------------------------------------
# Funciones de cálculo de producto diario
# ------------------------------------------------------------

def calcular_producto_diario(producto, especie, dosis_elegida, peso_kg, consumo_kg, num_animales):
    """Calcula la cantidad de producto (kg o L) para un día y un animal promedio."""
    if producto.tipo_producto == "Premezcla":
        # Dosis en kg/ton de alimento -> producto diario = (dosis * consumo_total_ton)
        consumo_total_ton = (consumo_kg * num_animales) / 1000.0
        return dosis_elegida * consumo_total_ton
    else:
        tipo_dosis, _, _ = (producto.dosis_aves if especie == "Aves" else producto.dosis_cerdos)
        if tipo_dosis == "feed":
            # Dosis en kg/ton -> producto diario (kg) = dosis * (consumo_total_kg/1000)
            consumo_total_ton = (consumo_kg * num_animales) / 1000.0
            return dosis_elegida * consumo_total_ton
        elif tipo_dosis == "pv":
            # Dosis en mg/kg PV
            mg_necesarios = dosis_elegida * peso_kg * num_animales
            if producto.unidad == "kg":
                mg_por_kg = producto.concentracion * 1000
                return mg_necesarios / mg_por_kg
            else:  # Litros
                mg_por_L = producto.concentracion * 1000
                return mg_necesarios / mg_por_L
        else:
            return 0.0

# ------------------------------------------------------------
# Interfaz principal
# ------------------------------------------------------------
def main():
    st.title("💊 Cálculo de Dosis Veterinarias con Tabla Dinámica")
    st.markdown("Ajusta los valores de **peso** y **consumo diario** directamente en la tabla interactiva.")

    # Sidebar: parámetros generales
    st.sidebar.header("Parámetros generales")
    especie = st.sidebar.selectbox("Especie", ["Aves", "Cerdos"])

    if especie == "Aves":
        subespecie = st.sidebar.selectbox("Tipo de ave", ["Broilers", "Ponedoras"])
    else:
        subespecie = None

    num_animales = st.sidebar.number_input("Número de animales", min_value=1, value=1000, step=100)

    # Selección de producto
    productos_disponibles = []
    for cod, prod in PRODUCTOS.items():
        if especie == "Aves" and prod.dosis_aves is not None:
            productos_disponibles.append(cod)
        elif especie == "Cerdos" and prod.dosis_cerdos is not None:
            productos_disponibles.append(cod)

    if not productos_disponibles:
        st.error("No hay productos para la especie seleccionada.")
        return

    codigo_seleccionado = st.selectbox("Código de producto", productos_disponibles,
                                        format_func=lambda x: f"{x} - {PRODUCTOS[x].nombre}")
    producto = PRODUCTOS[codigo_seleccionado]

    # Mostrar info producto
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Nombre:** {producto.nombre}")
        st.write(f"**Tipo:** {producto.tipo_producto}")
    with col2:
        st.write(f"**Presentación:** {producto.presentacion_kg} {producto.unidad}")
        st.write(f"**PVP por {producto.unidad}:** ${producto.precio:.2f}")

    # Selección de dosis
    if especie == "Aves":
        dosis_info = producto.dosis_aves
    else:
        dosis_info = producto.dosis_cerdos
    tipo_dosis, dosis_min, dosis_max = dosis_info

    unidad_dosis = "kg/ton de alimento" if tipo_dosis == "feed" else "mg/kg de peso vivo"
    st.subheader("⚙️ Dosis")
    opcion_dosis = st.radio("Seleccionar dosis", ["Mínima", "Máxima", "Otra"], index=0, horizontal=True)
    if opcion_dosis == "Mínima":
        dosis_elegida = dosis_min
    elif opcion_dosis == "Máxima":
        dosis_elegida = dosis_max
    else:
        dosis_elegida = st.number_input(f"Ingrese dosis ({unidad_dosis})", min_value=0.0, value=dosis_min, step=0.1)

    st.info(f"Dosis seleccionada: {dosis_elegida} {unidad_dosis}")

    # Definir duración del tratamiento (días)
    st.sidebar.subheader("Duración del tratamiento")
    dia_inicio = st.sidebar.number_input("Día de inicio (edad en días)", min_value=0, value=1, step=1)
    if especie == "Aves" and subespecie == "Broilers":
        dia_fin_default = 42
    elif especie == "Aves" and subespecie == "Ponedoras":
        dia_fin_default = 30   # ejemplo
    else:
        dia_fin_default = 90
    dia_fin = st.sidebar.number_input("Día de fin (edad en días)", min_value=dia_inicio+1, value=dia_fin_default, step=1)

    # Generar tabla base según especie/subespecie
    if especie == "Aves":
        if subespecie == "Broilers":
            df_base = generar_tabla_broiler(dia_inicio, dia_fin)
        else:
            df_base = generar_tabla_ponedora(dia_inicio, dia_fin)
    else:
        df_base = generar_tabla_cerdo(dia_inicio, dia_fin)

    # Crear copia para editar
    df_edit = df_base.copy()

    # Calcular producto diario para cada fila según los valores actuales
    producto_diario_list = []
    for idx, row in df_edit.iterrows():
        prod_dia = calcular_producto_diario(
            producto, especie, dosis_elegida,
            row["Peso (kg)"], row["Consumo (kg/día)"], num_animales
        )
        producto_diario_list.append(prod_dia)
    df_edit["Producto diario (kg o L)"] = producto_diario_list

    # Mostrar tabla editable
    st.subheader("📊 Tabla de tratamiento diario")
    st.markdown("**Edita las celdas de 'Peso (kg)' y 'Consumo (kg/día)' directamente.** Los cálculos se actualizarán.")

    # Configurar columnas para edición
    column_config = {
        "Día": st.column_config.NumberColumn("Día", disabled=True),
        "Peso (kg)": st.column_config.NumberColumn("Peso (kg)", min_value=0.01, step=0.01),
        "Consumo (kg/día)": st.column_config.NumberColumn("Consumo (kg/día)", min_value=0.0, step=0.01),
        "Producto diario (kg o L)": st.column_config.NumberColumn(f"Producto diario ({producto.unidad})", disabled=True, format="%.3f")
    }

    # Usar data_editor para permitir edición
    edited_df = st.data_editor(
        df_edit,
        column_config=column_config,
        use_container_width=True,
        num_rows="fixed"
    )

    # Recalcular producto diario si se editaron peso o consumo
    if not edited_df.equals(df_edit):
        for idx, row in edited_df.iterrows():
            prod_dia = calcular_producto_diario(
                producto, especie, dosis_elegida,
                row["Peso (kg)"], row["Consumo (kg/día)"], num_animales
            )
            edited_df.at[idx, "Producto diario (kg o L)"] = prod_dia
        # Actualizar df_edit para evitar bucle infinito
        st.rerun()

    # Totales a partir de la tabla
    total_alimento_kg = (edited_df["Consumo (kg/día)"] * num_animales).sum()
    total_alimento_ton = total_alimento_kg / 1000.0
    total_producto = edited_df["Producto diario (kg o L)"].sum()
    precio_total = math.ceil(total_producto) * producto.precio

    # Mostrar resultados globales
    st.header("📊 Resultados finales")
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        st.metric("Alimento total", f"{total_alimento_ton:.2f} toneladas")
    with col_r2:
        st.metric(f"Producto total necesario", f"{total_producto:.2f} {producto.unidad}")
    with col_r3:
        st.metric("Precio estimado", f"${precio_total:.2f}")

    # Detalle del redondeo
    unidades_comprar = math.ceil(total_producto)
    if unidades_comprar != total_producto:
        st.caption(f"* Precio calculado redondeando al entero superior: {unidades_comprar} {producto.unidad} × ${producto.precio:.2f} = ${precio_total:.2f}")

    # Opcional: descargar tabla como CSV
    csv = edited_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar tabla (CSV)", data=csv, file_name="tabla_tratamiento.csv", mime="text/csv")

if __name__ == "__main__":
    main()
