import streamlit as st
import pandas as pd
import numpy as np
import math

st.set_page_config(page_title="Calculador de Dosis Veterinarias", layout="wide")

# ------------------------------------------------------------
# Definición de productos (sin cambios)
# ------------------------------------------------------------
class Producto:
    def __init__(self, codigo, nombre, unidad, presentacion_kg, precio, tipo_producto, concentracion,
                 dosis_aves=None, dosis_cerdos=None):
        self.codigo = codigo
        self.nombre = nombre
        self.unidad = unidad
        self.presentacion_kg = presentacion_kg
        self.precio = precio
        self.tipo_producto = tipo_producto
        self.concentracion = concentracion
        self.dosis_aves = dosis_aves
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
# Datos de líneas genéticas para Broilers
# ------------------------------------------------------------
cobb500_data = {
    0: (42, 0), 1: (55, 0), 2: (71, 0), 3: (90, 0), 4: (112, 0), 5: (138, 0), 6: (168, 0),
    7: (202, 18), 8: (240, 40), 9: (283, 44), 10: (330, 50), 11: (382, 57), 12: (440, 64),
    13: (503, 73), 14: (570, 80), 15: (639, 84), 16: (711, 91), 17: (786, 98), 18: (864, 105),
    19: (945, 111), 20: (1029, 118), 21: (1116, 125), 22: (1205, 131), 23: (1296, 137),
    24: (1390, 143), 25: (1486, 149), 26: (1583, 154), 27: (1682, 160), 28: (1783, 165),
    29: (1886, 169), 30: (1989, 174), 31: (2094, 178), 32: (2200, 183), 33: (2306, 187),
    34: (2413, 191), 35: (2521, 194), 36: (2629, 198), 37: (2738, 202), 38: (2846, 206),
    39: (2954, 209), 40: (3062, 213), 41: (3170, 217), 42: (3278, 220), 43: (3384, 224),
    44: (3490, 228), 45: (3595, 232), 46: (3699, 236), 47: (3801, 239), 48: (3902, 243),
    49: (4001, 247), 50: (4099, 250), 51: (4195, 253), 52: (4289, 256), 53: (4380, 258),
    54: (4470, 260), 55: (4557, 261), 56: (4641, 262)
}

ross308_data = {
    1: (62, 12), 2: (81, 28), 3: (102, 48), 4: (125, 72), 5: (151, 100),
    6: (181, 131), 7: (213, 166), 8: (249, 206), 9: (288, 249), 10: (330, 297),
    11: (376, 349), 12: (425, 406), 13: (477, 468), 14: (532, 535), 15: (592, 608),
    16: (655, 685), 17: (720, 768), 18: (789, 856), 19: (860, 950), 20: (935, 1050),
    21: (1012, 1155), 22: (1092, 1266), 23: (1174, 1383), 24: (1258, 1505), 25: (1345, 1633),
    26: (1434, 1767), 27: (1524, 1907), 28: (1616, 2051), 29: (1710, 2202), 30: (1805, 2357),
    31: (1901, 2518), 32: (1999, 2684), 33: (2097, 2855), 34: (2196, 3031), 35: (2296, 3211),
    36: (2396, 3396), 37: (2496, 3584), 38: (2597, 3777), 39: (2697, 3974), 40: (2798, 4175),
    41: (2898, 4379), 42: (2998, 4586), 43: (3097, 4797), 44: (3197, 5010), 45: (3295, 5226),
    46: (3393, 5445), 47: (3490, 5666), 48: (3586, 5890), 49: (3681, 6115), 50: (3776, 6342),
    51: (3869, 6571), 52: (3961, 6801), 53: (4052, 7032), 54: (4142, 7265), 55: (4230, 7498)
}
# Nota: Ross308 no incluye día 0, empezamos en 1.

def generar_tabla_broiler(linea, dia_inicio, dia_fin):
    """Genera dataframe para la línea genética seleccionada, excluyendo día 0."""
    data = cobb500_data if linea == "Cobb500" else ross308_data
    # Asegurar que no se incluya día 0
    if dia_inicio == 0:
        dia_inicio = 1
    dias = list(range(dia_inicio, dia_fin+1))
    pesos_kg = []
    consumos_diarios_kg = []
    for d in dias:
        if d in data:
            peso_g, consumo_g = data[d]
        else:
            # Interpolación o último valor
            max_dia = max(data.keys())
            if d > max_dia:
                peso_g, consumo_g = data[max_dia]
            else:
                dias_conocidos = sorted(data.keys())
                for i in range(len(dias_conocidos)-1):
                    if dias_conocidos[i] <= d <= dias_conocidos[i+1]:
                        d1, d2 = dias_conocidos[i], dias_conocidos[i+1]
                        p1, c1 = data[d1]
                        p2, c2 = data[d2]
                        peso_g = p1 + (p2-p1)*(d-d1)/(d2-d1)
                        consumo_g = c1 + (c2-c1)*(d-d1)/(d2-d1)
                        break
        pesos_kg.append(round(peso_g/1000.0, 3))
        consumos_diarios_kg.append(round(consumo_g/1000.0, 3))
    df = pd.DataFrame({'Día': dias, 'Peso (kg)': pesos_kg, 'Consumo diario de alimento (kg)': consumos_diarios_kg})
    df['Consumo acumulado de alimento (kg)'] = df['Consumo diario de alimento (kg)'].cumsum().round(3)
    return df

def generar_tabla_ponedora(dia_inicio, dia_fin):
    if dia_inicio == 0:
        dia_inicio = 1
    dias = list(range(dia_inicio, dia_fin+1))
    df = pd.DataFrame({'Día': dias})
    df['Peso (kg)'] = 1.5
    df['Consumo diario de alimento (kg)'] = 0.12
    df['Consumo acumulado de alimento (kg)'] = (df['Consumo diario de alimento (kg)'].cumsum()).round(3)
    return df

def generar_tabla_cerdo(dia_inicio, dia_fin):
    if dia_inicio == 0:
        dia_inicio = 1
    referencia = {0: (20.0, 0.0), 30: (40.0, 1.5), 60: (70.0, 2.5), 90: (95.0, 3.2), 120: (110.0, 3.5)}
    dias = list(range(dia_inicio, dia_fin+1))
    pesos = []
    consumos = []
    for d in dias:
        if d <= 0:
            peso = 20.0
            cons = 0.0
        else:
            dias_ref = sorted(referencia.keys())
            for i in range(len(dias_ref)-1):
                if dias_ref[i] <= d <= dias_ref[i+1]:
                    d1, d2 = dias_ref[i], dias_ref[i+1]
                    p1, c1 = referencia[d1]
                    p2, c2 = referencia[d2]
                    peso = p1 + (p2-p1)*(d-d1)/(d2-d1)
                    cons = c1 + (c2-c1)*(d-d1)/(d2-d1)
                    break
        pesos.append(round(peso, 3))
        consumos.append(round(cons, 3))
    df = pd.DataFrame({'Día': dias, 'Peso (kg)': pesos, 'Consumo diario de alimento (kg)': consumos})
    df['Consumo acumulado de alimento (kg)'] = df['Consumo diario de alimento (kg)'].cumsum().round(3)
    return df

# ------------------------------------------------------------
# Cálculo de producto diario
# ------------------------------------------------------------
def calcular_producto_diario(producto, especie, dosis_elegida, peso_kg, consumo_kg, num_animales):
    if producto.tipo_producto == "Premezcla":
        consumo_total_ton = (consumo_kg * num_animales) / 1000.0
        return dosis_elegida * consumo_total_ton
    else:
        tipo_dosis, _, _ = (producto.dosis_aves if especie == "Aves" else producto.dosis_cerdos)
        if tipo_dosis == "feed":
            consumo_total_ton = (consumo_kg * num_animales) / 1000.0
            return dosis_elegida * consumo_total_ton
        else:  # pv
            mg_necesarios = dosis_elegida * peso_kg * num_animales
            if producto.unidad == "kg":
                mg_por_kg = producto.concentracion * 1000
                return mg_necesarios / mg_por_kg
            else:  # Litros
                mg_por_L = producto.concentracion * 1000
                return mg_necesarios / mg_por_L

# ------------------------------------------------------------
# Interfaz principal
# ------------------------------------------------------------
def main():
    st.title("💊 Cálculo de Dosis Veterinarias con Tabla Dinámica")
    st.markdown("Selecciona especie, línea genética (para Broilers), producto y dosis. Edita la tabla directamente.")

    st.sidebar.header("Parámetros generales")
    especie = st.sidebar.selectbox("Especie", ["Aves", "Cerdos"])

    if especie == "Aves":
        subespecie = st.sidebar.selectbox("Tipo de ave", ["Broilers", "Ponedoras"])
        if subespecie == "Broilers":
            linea = st.sidebar.selectbox("Línea genética", ["Cobb500", "Ross308"])
        else:
            linea = None
    else:
        subespecie = None
        linea = None

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

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Nombre:** {producto.nombre}")
        st.write(f"**Tipo:** {producto.tipo_producto}")
    with col2:
        st.write(f"**Presentación:** {producto.presentacion_kg} {producto.unidad}")
        st.write(f"**PVP por {producto.unidad}:** ${producto.precio:.2f}")

    # Dosis
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

    # Duración del tratamiento
    st.sidebar.subheader("Duración del tratamiento")
    dia_inicio = st.sidebar.number_input("Día de inicio (edad en días)", min_value=0, value=1, step=1)
    # Forzar inicio al menos 1 para evitar día 0
    if dia_inicio == 0:
        st.sidebar.warning("El día de inicio no puede ser 0. Se usará día 1.")
        dia_inicio = 1
    if especie == "Aves" and subespecie == "Broilers":
        dia_fin_default = 42
    elif especie == "Aves" and subespecie == "Ponedoras":
        dia_fin_default = 30
    else:
        dia_fin_default = 90
    dia_fin = st.sidebar.number_input("Día de fin", min_value=dia_inicio+1, value=dia_fin_default, step=1)

    # Generar tabla base
    if especie == "Aves":
        if subespecie == "Broilers":
            df_base = generar_tabla_broiler(linea, dia_inicio, dia_fin)
        else:  # Ponedoras
            df_base = generar_tabla_ponedora(dia_inicio, dia_fin)
    else:  # Cerdos
        df_base = generar_tabla_cerdo(dia_inicio, dia_fin)

    # Calcular producto diario y precio diario
    df_base['Producto diario (kg/L)'] = df_base.apply(
        lambda row: calcular_producto_diario(producto, especie, dosis_elegida,
                                             row['Peso (kg)'], row['Consumo diario de alimento (kg)'], num_animales), axis=1)
    df_base['Precio diario ($)'] = df_base['Producto diario (kg/L)'] * producto.precio
    df_base['Producto acumulado (kg/L)'] = df_base['Producto diario (kg/L)'].cumsum()
    df_base['Precio acumulado ($)'] = df_base['Precio diario ($)'].cumsum()

    # Redondear
    for col in ['Producto diario (kg/L)', 'Producto acumulado (kg/L)']:
        df_base[col] = df_base[col].round(3)
    df_base['Precio diario ($)'] = df_base['Precio diario ($)'].round(2)
    df_base['Precio acumulado ($)'] = df_base['Precio acumulado ($)'].round(2)

    # Mostrar tabla editable
    st.subheader("📊 Tabla de tratamiento diario")
    st.markdown("**Edita las celdas de 'Peso (kg)' y 'Consumo diario de alimento (kg)'** – el resto se recalcula automáticamente.")

    column_config = {
        "Día": st.column_config.NumberColumn("Día", disabled=True),
        "Peso (kg)": st.column_config.NumberColumn("Peso (kg)", min_value=0.0, step=0.001, format="%.3f"),
        "Consumo diario de alimento (kg)": st.column_config.NumberColumn("Consumo diario de alimento (kg)", min_value=0.0, step=0.001, format="%.3f"),
        "Consumo acumulado de alimento (kg)": st.column_config.NumberColumn("Consumo acumulado de alimento (kg)", disabled=True, format="%.3f"),
        "Producto diario (kg/L)": st.column_config.NumberColumn(f"Producto diario ({producto.unidad})", disabled=True, format="%.3f"),
        "Precio diario ($)": st.column_config.NumberColumn("Precio diario ($)", disabled=True, format="%.2f"),
        "Producto acumulado (kg/L)": st.column_config.NumberColumn(f"Producto acumulado ({producto.unidad})", disabled=True, format="%.3f"),
        "Precio acumulado ($)": st.column_config.NumberColumn("Precio acumulado ($)", disabled=True, format="%.2f"),
    }

    edited_df = st.data_editor(df_base, column_config=column_config, use_container_width=True, num_rows="fixed")

    # Recalcular si se editaron peso o consumo
    if not edited_df[['Peso (kg)', 'Consumo diario de alimento (kg)']].equals(df_base[['Peso (kg)', 'Consumo diario de alimento (kg)']]):
        edited_df['Consumo acumulado de alimento (kg)'] = edited_df['Consumo diario de alimento (kg)'].cumsum().round(3)
        edited_df['Producto diario (kg/L)'] = edited_df.apply(
            lambda row: calcular_producto_diario(producto, especie, dosis_elegida,
                                                 row['Peso (kg)'], row['Consumo diario de alimento (kg)'], num_animales), axis=1).round(3)
        edited_df['Precio diario ($)'] = (edited_df['Producto diario (kg/L)'] * producto.precio).round(2)
        edited_df['Producto acumulado (kg/L)'] = edited_df['Producto diario (kg/L)'].cumsum().round(3)
        edited_df['Precio acumulado ($)'] = edited_df['Precio diario ($)'].cumsum().round(2)
        st.rerun()

    # Totales finales
    total_alimento_kg = (edited_df['Consumo diario de alimento (kg)'] * num_animales).sum()
    total_alimento_ton = total_alimento_kg / 1000.0
    total_producto = edited_df['Producto acumulado (kg/L)'].iloc[-1]
    precio_redondeado = math.ceil(total_producto) * producto.precio

    st.header("📊 Resultados finales")
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        st.metric("Alimento total", f"{total_alimento_ton:.2f} toneladas")
    with col_r2:
        st.metric(f"Producto total necesario", f"{total_producto:.3f} {producto.unidad}")
    with col_r3:
        st.metric("Precio estimado (redondeado)", f"${precio_redondeado:.2f}")

    if total_producto != math.ceil(total_producto):
        st.caption(f"* Precio calculado redondeando al entero superior: {math.ceil(total_producto)} {producto.unidad} × ${producto.precio:.2f} = ${precio_redondeado:.2f}")

    # Descargar CSV
    csv = edited_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar tabla (CSV)", data=csv, file_name="tabla_tratamiento.csv", mime="text/csv")

if __name__ == "__main__":
    main()
