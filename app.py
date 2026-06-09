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
# Datos de Broilers (días)
# ------------------------------------------------------------
cobb500_data = {
    0: (42, 0), 1: (55, 0), 2: (71, 0), 3: (90, 0), 4: (112, 0), 5: (138, 0), 6: (168, 0),
    7: (202, 180), 8: (240, 40), 9: (283, 44), 10: (330, 50), 11: (382, 57), 12: (440, 64),
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
    0: (44, 0), 1: (62, 12), 2: (81, 16), 3: (102, 20), 4: (125, 24), 5: (151, 27), 6: (181, 31), 
    7: (213, 35), 8: (249, 39), 9: (288, 44), 10: (330, 48), 11: (376, 52), 12: (425, 57), 
    13: (477, 62), 14: (532, 67), 15: (592, 72), 16: (655, 77), 17: (720, 83), 18: (789, 88), 
    19: (860, 94), 20: (935, 100), 21: (1012, 105), 22: (1092, 111), 23: (1174, 117), 
    24: (1258, 122), 25: (1345, 128), 26: (1434, 134), 27: (1524, 139), 28: (1616, 145), 
    29: (1710, 150), 30: (1805, 156), 31: (1901, 161), 32: (1999, 166), 33: (2097, 171), 
    34: (2196, 176), 35: (2296, 180), 36: (2396, 185), 37: (2496, 189), 38: (2597, 193), 
    39: (2697, 197), 40: (2798, 201), 41: (2898, 204), 42: (2998, 207), 43: (3097, 211), 
    44: (3197, 213), 45: (3295, 216), 46: (3393, 219), 47: (3490, 221), 48: (3586, 223), 
    49: (3681, 225), 50: (3776, 227), 51: (3869, 229), 52: (3961, 230), 53: (4052, 231), 
    54: (4142, 233), 55: (4230, 233), 56: (4318, 234)
}

def generar_tabla_broiler(linea, dia_inicio, dia_fin):
    data = cobb500_data if linea == "Cobb500" else ross308_data
    if dia_inicio == 0:
        dia_inicio = 1
    dias = list(range(dia_inicio, dia_fin+1))
    pesos_kg, consumos_diarios_kg = [], []
    for d in dias:
        if d in data:
            peso_g, consumo_g = data[d]
        else:
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

# ------------------------------------------------------------
# Datos de Ponedoras: Hy-Line W-80 (semanas)
# ------------------------------------------------------------
hyline_w80_data = {
    1: (71.0, 14.5), 2: (131.0, 19.0), 3: (196.5, 22.5), 4: (268.0, 26.5), 5: (346.0, 31.5),
    6: (432.0, 36.0), 7: (525.0, 40.5), 8: (621.5, 44.0), 9: (718.0, 47.0), 10: (811.5, 50.0),
    11: (897.0, 53.0), 12: (973.0, 56.0), 13: (1039.0, 60.0), 14: (1096.5, 63.0), 15: (1146.5, 66.0),
    16: (1193.5, 70.0), 17: (1240.5, 73.0), 18: (1286.5, 77.25), 19: (1329.5, 80.7), 20: (1368.0, 84.55),
    21: (1401.5, 88.15), 22: (1432.5, 91.15), 23: (1460.5, 93.6), 24: (1486.5, 95.7), 25: (1511.0, 97.5),
    26: (1532.5, 99.0), 27: (1551.5, 100.25), 28: (1568.5, 101.35), 29: (1583.0, 102.2), 30: (1595.0, 103.05),
    31: (1606.0, 103.9), 32: (1615.0, 104.9), 33: (1623.0, 105.6), 34: (1629.0, 106.3), 35: (1634.0, 107.05),
    36: (1638.5, 107.55), 37: (1642.0, 107.95), 38: (1645.5, 108.35), 39: (1648.0, 108.6), 40: (1650.5, 108.75),
    41: (1653.0, 108.85), 42: (1654.0, 108.9), 43: (1655.5, 108.9), 44: (1657.5, 108.9),
}
# Extrapolación Hy-Line semanas 45-100
last_weight = hyline_w80_data[44][0]
last_consumo = hyline_w80_data[44][1]
for semana in range(45, 101):
    peso = last_weight + (semana - 44) * (1750 - last_weight) / (100 - 44)
    hyline_w80_data[semana] = (round(peso, 1), last_consumo)

def generar_tabla_ponedora_hyline(semana_inicio, semana_fin):
    semanas = list(range(semana_inicio, semana_fin+1))
    pesos_kg, consumos_semanales_kg = [], []
    for w in semanas:
        peso_g, consumo_diario_g = hyline_w80_data.get(w, (hyline_w80_data[100][0], hyline_w80_data[100][1]))
        pesos_kg.append(round(peso_g / 1000.0, 3))
        consumo_semanal_kg = (consumo_diario_g * 7) / 1000.0
        consumos_semanales_kg.append(round(consumo_semanal_kg, 3))
    df = pd.DataFrame({
        'Semana': semanas,
        'Peso (kg)': pesos_kg,
        'Consumo semanal de alimento (kg)': consumos_semanales_kg
    })
    df['Consumo acumulado de alimento (kg)'] = df['Consumo semanal de alimento (kg)'].cumsum().round(3)
    return df

# ------------------------------------------------------------
# Datos de Ponedoras: Lohmann LSL-Classic (semanas)
# ------------------------------------------------------------
lohmann_pesos = {
    1: 75, 2: 125, 3: 187, 4: 257, 5: 338, 6: 432, 7: 530, 8: 627, 9: 722, 10: 814,
    11: 901, 12: 976, 13: 1041, 14: 1102, 15: 1159, 16: 1215, 17: 1268, 18: 1320, 19: 1371, 20: 1422,
    21: 1472, 22: 1520, 23: 1562, 24: 1598, 25: 1628, 26: 1648, 27: 1665, 28: 1680, 29: 1690, 30: 1700,
    31: 1707, 32: 1710, 33: 1713, 34: 1715, 35: 1718, 36: 1720, 37: 1723, 38: 1725, 39: 1728, 40: 1730,
    41: 1733, 42: 1735, 43: 1738, 44: 1740, 45: 1743, 46: 1745, 47: 1747, 48: 1749, 49: 1751, 50: 1752,
}
# Extrapolación hasta semana 100 (aumento de 1-2 g por semana)
for w in range(51, 101):
    lohmann_pesos[w] = lohmann_pesos[w-1] + 1

def generar_tabla_ponedora_lohmann(semana_inicio, semana_fin):
    semanas = list(range(semana_inicio, semana_fin+1))
    pesos_kg, consumos_semanales_kg = [], []
    for w in semanas:
        peso_g = lohmann_pesos.get(w, lohmann_pesos[100])
        # Consumo: hasta semana 20 usa Hy-Line, luego 110 g/día
        if w <= 20:
            consumo_diario_g = hyline_w80_data[w][1]
        else:
            consumo_diario_g = 110.0
        pesos_kg.append(round(peso_g / 1000.0, 3))
        consumo_semanal_kg = (consumo_diario_g * 7) / 1000.0
        consumos_semanales_kg.append(round(consumo_semanal_kg, 3))
    df = pd.DataFrame({
        'Semana': semanas,
        'Peso (kg)': pesos_kg,
        'Consumo semanal de alimento (kg)': consumos_semanales_kg
    })
    df['Consumo acumulado de alimento (kg)'] = df['Consumo semanal de alimento (kg)'].cumsum().round(3)
    return df

# ------------------------------------------------------------
# Datos de Cerdos (días)
# ------------------------------------------------------------
def generar_tabla_cerdo(dia_inicio, dia_fin):
    if dia_inicio == 0:
        dia_inicio = 1
    referencia = {0: (20.0, 0.0), 30: (40.0, 1.5), 60: (70.0, 2.5), 90: (95.0, 3.2), 120: (110.0, 3.5)}
    dias = list(range(dia_inicio, dia_fin+1))
    pesos, consumos = [], []
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
# Cálculo de producto por periodo (día o semana)
# ------------------------------------------------------------
def calcular_producto_periodo(producto, especie, dosis_elegida, peso_kg, consumo_periodo_kg, num_animales):
    if producto.tipo_producto == "Premezcla":
        consumo_total_ton = (consumo_periodo_kg * num_animales) / 1000.0
        return dosis_elegida * consumo_total_ton
    else:
        tipo_dosis, _, _ = (producto.dosis_aves if especie == "Aves" else producto.dosis_cerdos)
        if tipo_dosis == "feed":
            consumo_total_ton = (consumo_periodo_kg * num_animales) / 1000.0
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
    st.set_page_config(page_title="Calculador de Dosis Veterinarias", layout="wide", page_icon="🐔")
    st.title("💊 Cálculo de Dosis Veterinarias con Tabla Dinámica")
    
    # Logo en la barra lateral
    st.sidebar.image("/JDVT2000/Calculador-dosis/logo_promune.png", use_container_width=True)
    
    st.markdown("Selecciona especie, línea genética, producto y dosis. Edita la tabla directamente.")

    st.sidebar.header("Parámetros generales")
    especie = st.sidebar.selectbox("Especie", ["Aves", "Cerdos"])

    if especie == "Aves":
        subespecie = st.sidebar.selectbox("Tipo de ave", ["Broilers", "Ponedoras"])
        if subespecie == "Broilers":
            linea = st.sidebar.selectbox("Línea genética", ["Cobb500", "Ross308"])
        else:
            linea = st.sidebar.selectbox("Línea genética", ["Hy-Line W-80", "Lohmann LSL-Classic"])
    else:
        subespecie = None
        linea = None

    num_animales = st.sidebar.number_input("Número de animales", min_value=1, value=1000, step=100)

    # Producto
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

    # Duración
    st.sidebar.subheader("Duración del tratamiento")
    if subespecie == "Ponedoras":
        periodo_label = "semana"
        inicio = st.sidebar.number_input("Semana de inicio", min_value=1, value=1, step=1)
        fin = st.sidebar.number_input("Semana de fin", min_value=inicio+1, value=80, step=1)
        es_semanal = True
    else:
        periodo_label = "día"
        inicio = st.sidebar.number_input("Día de inicio", min_value=0, value=1, step=1)
        if inicio == 0:
            st.sidebar.warning("El día de inicio no puede ser 0. Se usará día 1.")
            inicio = 1
        if especie == "Aves" and subespecie == "Broilers":
            fin_default = 42
        elif especie == "Cerdos":
            fin_default = 90
        else:
            fin_default = 30
        fin = st.sidebar.number_input("Día de fin", min_value=inicio+1, value=fin_default, step=1)
        es_semanal = False

    # Generar tabla base
    if especie == "Aves":
        if subespecie == "Broilers":
            df_base = generar_tabla_broiler(linea, inicio, fin)
            col_periodo = "Día"
            col_consumo = "Consumo diario de alimento (kg)"
            col_consumo_acum = "Consumo acumulado de alimento (kg)"
        else:  # Ponedoras
            if linea == "Hy-Line W-80":
                df_base = generar_tabla_ponedora_hyline(inicio, fin)
            else:
                df_base = generar_tabla_ponedora_lohmann(inicio, fin)
            col_periodo = "Semana"
            col_consumo = "Consumo semanal de alimento (kg)"
            col_consumo_acum = "Consumo acumulado de alimento (kg)"
    else:  # Cerdos
        df_base = generar_tabla_cerdo(inicio, fin)
        col_periodo = "Día"
        col_consumo = "Consumo diario de alimento (kg)"
        col_consumo_acum = "Consumo acumulado de alimento (kg)"

    # Renombrar para la interfaz
    df_base.rename(columns={col_periodo: 'Periodo'}, inplace=True)
    df_base.rename(columns={col_consumo: 'Consumo periodo (kg)'}, inplace=True)
    df_base.rename(columns={col_consumo_acum: 'Consumo acumulado (kg)'}, inplace=True)

    # Calcular producto por periodo
    df_base['Producto periodo (kg/L)'] = df_base.apply(
        lambda row: calcular_producto_periodo(producto, especie, dosis_elegida,
                                              row['Peso (kg)'], row['Consumo periodo (kg)'], num_animales), axis=1)
    df_base['Precio periodo ($)'] = df_base['Producto periodo (kg/L)'] * producto.precio
    df_base['Producto acumulado (kg/L)'] = df_base['Producto periodo (kg/L)'].cumsum()
    df_base['Precio acumulado ($)'] = df_base['Precio periodo ($)'].cumsum()

    # Redondear
    df_base['Producto periodo (kg/L)'] = df_base['Producto periodo (kg/L)'].round(3)
    df_base['Precio periodo ($)'] = df_base['Precio periodo ($)'].round(2)
    df_base['Producto acumulado (kg/L)'] = df_base['Producto acumulado (kg/L)'].round(3)
    df_base['Precio acumulado ($)'] = df_base['Precio acumulado ($)'].round(2)

    # Tabla editable
    st.subheader("📊 Tabla de tratamiento")
    st.markdown(f"**Edita las celdas de 'Peso (kg)' y 'Consumo periodo (kg)'** – el resto se recalcula automáticamente.")

    column_config = {
        "Periodo": st.column_config.NumberColumn(periodo_label.capitalize(), disabled=True),
        "Peso (kg)": st.column_config.NumberColumn("Peso (kg)", min_value=0.0, step=0.001, format="%.3f"),
        "Consumo periodo (kg)": st.column_config.NumberColumn(f"Consumo {periodo_label} (kg)", min_value=0.0, step=0.001, format="%.3f"),
        "Consumo acumulado (kg)": st.column_config.NumberColumn("Consumo acumulado (kg)", disabled=True, format="%.3f"),
        "Producto periodo (kg/L)": st.column_config.NumberColumn(f"Producto {periodo_label} ({producto.unidad})", disabled=True, format="%.3f"),
        "Precio periodo ($)": st.column_config.NumberColumn(f"Precio {periodo_label} ($)", disabled=True, format="%.2f"),
        "Producto acumulado (kg/L)": st.column_config.NumberColumn(f"Producto acumulado ({producto.unidad})", disabled=True, format="%.3f"),
        "Precio acumulado ($)": st.column_config.NumberColumn("Precio acumulado ($)", disabled=True, format="%.2f"),
    }

    edited_df = st.data_editor(df_base, column_config=column_config, use_container_width=True, num_rows="fixed")

    # Recalcular si hubo cambios
    if not edited_df[['Peso (kg)', 'Consumo periodo (kg)']].equals(df_base[['Peso (kg)', 'Consumo periodo (kg)']]):
        edited_df['Consumo acumulado (kg)'] = edited_df['Consumo periodo (kg)'].cumsum().round(3)
        edited_df['Producto periodo (kg/L)'] = edited_df.apply(
            lambda row: calcular_producto_periodo(producto, especie, dosis_elegida,
                                                  row['Peso (kg)'], row['Consumo periodo (kg)'], num_animales), axis=1).round(3)
        edited_df['Precio periodo ($)'] = (edited_df['Producto periodo (kg/L)'] * producto.precio).round(2)
        edited_df['Producto acumulado (kg/L)'] = edited_df['Producto periodo (kg/L)'].cumsum().round(3)
        edited_df['Precio acumulado ($)'] = edited_df['Precio periodo ($)'].cumsum().round(2)
        st.rerun()

    # Totales finales
    total_alimento_kg = (edited_df['Consumo periodo (kg)'] * num_animales).sum()
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
