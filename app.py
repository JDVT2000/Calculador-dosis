import streamlit as st

# Configuración de la página (DEBE ser el primer comando de Streamlit)
st.set_page_config(page_title="Calculador de Dosis Veterinarias", layout="wide")

import streamlit as st
import math
from typing import Dict, Tuple, Optional

# ------------------------------------------------------------
# Definición de productos basada en la tabla proporcionada
# ------------------------------------------------------------

# Estructura para almacenar información de cada producto
class Producto:
    def __init__(self, codigo, nombre, unidad, presentacion_kg, precio, tipo_producto, concentracion,
                 dosis_aves=None, dosis_cerdos=None):
        self.codigo = codigo
        self.nombre = nombre
        self.unidad = unidad  # 'kg' o 'L'
        self.presentacion_kg = presentacion_kg  # kg o L por envase (no usado directamente)
        self.precio = precio
        self.tipo_producto = tipo_producto  # 'Premezcla', 'Polvo Soluble', 'Antibiótico Oral'
        self.concentracion = concentracion  # en mg/g para polvos, mg/ml para líquidos
        self.dosis_aves = dosis_aves  # tuple: (tipo, min, max) tipo = 'pv' o 'feed'
        self.dosis_cerdos = dosis_cerdos

# Función auxiliar para crear dosis
def dosis(tipo, min_dosis, max_dosis):
    return (tipo, min_dosis, max_dosis)

# Catálogo de productos
PRODUCTOS = {
    "EC0001": Producto(
        "EC0001", "Vitabland - Pro Gallinas/Postura Px", "kg", 25, 3.95, "Premezcla", None,
        dosis_aves=dosis("feed", 1.0, 1.0), dosis_cerdos=None
    ),
    "EC0002": Producto(
        "EC0002", "Vitabland - Pro Broilers Inicio-Crecimiento-Engorde", "kg", 25, 4.40, "Premezcla", None,
        dosis_aves=dosis("feed", 1.0, 1.0), dosis_cerdos=None
    ),
    "EC0003": Producto(
        "EC0003", "Vitabland - Pro Cerdos Inicio y Reproductores", "kg", 25, 4.95, "Premezcla", None,
        dosis_aves=None, dosis_cerdos=dosis("feed", 1.0, 1.0)
    ),
    "EC0004": Producto(
        "EC0004", "Tilvamune 5% Premix", "kg", 25, 20.80, "Polvo Soluble", 50.0,  # mg/g
        dosis_aves=dosis("pv", 500.0, 500.0),   # 100 g / 200 kg PV = 500 mg/kg
        dosis_cerdos=dosis("feed", 1.0, 2.0)    # 1-2 kg/ton
    ),
    "EC0005": Producto(
        "EC0005", "Neomicin 50", "kg", 25, 21.90, "Polvo Soluble", 500.0,
        dosis_aves=dosis("feed", 0.14, 0.28), dosis_cerdos=dosis("feed", 0.14, 0.28)
    ),
    "EC0006": Producto(
        "EC0006", "Tiamulin Premix 100", "kg", 25, 14.25, "Polvo Soluble", 100.0,
        dosis_aves=dosis("feed", 1.0, 5.0), dosis_cerdos=dosis("feed", 1.0, 5.0)
    ),
    "EC0007": Producto(
        "EC0007", "Florfen 20", "L", 1, 24.80, "Antibiótico Oral", 200.0,  # mg/ml
        dosis_aves=dosis("pv", 20.0, 30.0), dosis_cerdos=dosis("pv", 10.0, 20.0)
    ),
    "EC0008": Producto(
        "EC0008", "Lincospect 11", "kg", 25, 46.10, "Polvo Soluble", 110.0,
        dosis_aves=dosis("feed", 1.0, 1.0), dosis_cerdos=dosis("feed", 1.0, 1.0)
    ),
    "EC0009": Producto(
        "EC0009", "Enromune 20", "L", 1, 22.00, "Antibiótico Oral", 200.0,
        dosis_aves=dosis("pv", 10.0, 10.0), dosis_cerdos=dosis("pv", 10.0, 10.0)
    ),
    "EC0010": Producto(
        "EC0010", "Clortiamune", "kg", 25, 12.50, "Polvo Soluble", 110.0,
        dosis_aves=dosis("feed", 1.8, 4.5), dosis_cerdos=dosis("feed", 1.8, 4.5)
    ),
    "EC0011": Producto(
        "EC0011", "Pro-Amox", "kg", 1, 38.00, "Polvo Soluble", 500.0,
        dosis_aves=dosis("pv", 10.0, 10.0), dosis_cerdos=dosis("pv", 10.0, 10.0)
    ),
    "EC0012": Producto(
        "EC0012", "Vitabland - Pro Cerdos Crecimiento Engorde", "kg", 25, 3.95, "Premezcla", None,
        dosis_aves=None, dosis_cerdos=dosis("feed", 1.0, 1.0)
    ),
}

# ------------------------------------------------------------
# Funciones de cálculo
# ------------------------------------------------------------

def calcular_alimento_total(num_animales: int, consumo_por_animal_kg: float) -> float:
    """Calcula las toneladas métricas de alimento necesario."""
    return (num_animales * consumo_por_animal_kg) / 1000.0

def calcular_producto_necesario(producto: Producto, especie: str, dosis_elegida: float,
                                peso_animal_kg: float, num_animales: int,
                                alimento_ton: float) -> float:
    """
    Calcula la cantidad de producto necesaria (kg o L) según el tipo de dosis.
    Para premezclas se basa en alimento_ton.
    Para dosis en 'feed' (kg/ton) se multiplica por alimento_ton.
    Para dosis en 'pv' (mg/kg) se usa peso animal, número y concentración.
    """
    # Obtener la dosis correspondiente a la especie
    if especie == "Aves":
        dosis_info = producto.dosis_aves
    else:
        dosis_info = producto.dosis_cerdos

    if dosis_info is None:
        raise ValueError(f"Producto {producto.codigo} no disponible para {especie}")

    tipo_dosis, _, _ = dosis_info

    # Premezclas: siempre dosis en feed (1 kg/ton)
    if producto.tipo_producto == "Premezcla":
        # La dosis es fija 1 kg/ton (asumido)
        return alimento_ton  # kg de premezcla

    if tipo_dosis == "feed":
        # dosis_elegida está en kg/ton
        return dosis_elegida * alimento_ton  # kg

    elif tipo_dosis == "pv":
        # dosis_elegida está en mg/kg PV
        mg_necesarios = dosis_elegida * peso_animal_kg * num_animales
        if producto.unidad == "kg":
            # Concentración en mg/g -> mg por kg = concentracion * 1000
            mg_por_kg = producto.concentracion * 1000
            kg_producto = mg_necesarios / mg_por_kg
            return kg_producto
        elif producto.unidad == "L":
            # Concentración en mg/ml -> mg por L = concentracion * 1000
            mg_por_L = producto.concentracion * 1000
            L_producto = mg_necesarios / mg_por_L
            return L_producto
        else:
            raise ValueError(f"Unidad no soportada: {producto.unidad}")
    else:
        raise ValueError(f"Tipo de dosis desconocido: {tipo_dosis}")

def precio_estimado(cantidad_producto: float, precio_unitario: float) -> float:
    """Redondea al entero superior la cantidad y multiplica por precio unitario."""
    unidades_a_comprar = math.ceil(cantidad_producto)
    return unidades_a_comprar * precio_unitario

# ------------------------------------------------------------
# Interfaz Streamlit
# ------------------------------------------------------------
def main():
    st.set_page_config(page_title="Dosis Veterinarias", layout="wide")
    st.title("💊 Cálculo de Dosis para Aves y Cerdos")
    st.markdown("Aplicación para calcular cantidad de producto y precio según la especie y el consumo.")

    # Sidebar para selección principal
    st.sidebar.header("Parámetros generales")
    especie = st.sidebar.selectbox("Especie", ["Aves", "Cerdos"])

    # Subespecie para aves
    if especie == "Aves":
        subespecie = st.sidebar.selectbox("Tipo de ave", ["Broilers", "Ponedoras"])
    else:
        subespecie = None

    # Número de animales
    num_animales = st.sidebar.number_input("Número de animales", min_value=1, value=100, step=1)

    # Peso animal (con defaults según especie/subespecie)
    if especie == "Aves":
        if subespecie == "Broilers":
            peso_default = 0.04
            peso_help = "Peso promedio de un pollito BB (0.04 kg)"
        else:  # Ponedoras
            peso_default = 1.5
            peso_help = "Peso promedio de una gallina ponedora (1.5 kg)"
    else:  # Cerdos
        peso_default = 100.0
        peso_help = "Peso promedio de cerdo en engorde (100 kg)"

    peso_animal = st.sidebar.number_input("Peso animal (kg)", min_value=0.01, value=peso_default, step=0.1, help=peso_help)

    # Consumo de alimento por animal (kg)
    if especie == "Aves":
        if subespecie == "Broilers":
            consumo_default = 4.0
            consumo_help = "Consumo total por broiler (aprox 4 kg)"
        else:
            consumo_default = 0.12
            consumo_help = "Consumo diario por ponedora (0.12 kg/día). Ajuste según días de tratamiento."
    else:  # Cerdos
        consumo_default = 200.0
        consumo_help = "Consumo total por cerdo (aprox 200 kg)"

    consumo_manual = st.sidebar.checkbox("Ingresar consumo manual", value=False)
    if consumo_manual:
        consumo_por_animal = st.sidebar.number_input("Consumo de alimento por animal (kg)", min_value=0.0, value=consumo_default, step=0.1)
    else:
        consumo_por_animal = consumo_default
        st.sidebar.info(f"Consumo por defecto: {consumo_default} kg/animal")

    # Filtro de productos según especie
    productos_disponibles = []
    for cod, prod in PRODUCTOS.items():
        if especie == "Aves" and prod.dosis_aves is not None:
            productos_disponibles.append(cod)
        elif especie == "Cerdos" and prod.dosis_cerdos is not None:
            productos_disponibles.append(cod)

    if not productos_disponibles:
        st.error("No hay productos disponibles para la especie seleccionada.")
        return

    # Selector de producto
    codigo_seleccionado = st.selectbox("Código de producto", productos_disponibles, format_func=lambda x: f"{x} - {PRODUCTOS[x].nombre}")
    producto = PRODUCTOS[codigo_seleccionado]

    # Mostrar información del producto
    st.subheader("📦 Información del producto")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Nombre:** {producto.nombre}")
        st.write(f"**Tipo:** {producto.tipo_producto}")
    with col2:
        st.write(f"**Presentación:** {producto.presentacion_kg} {producto.unidad}")
        st.write(f"**PVP por {producto.unidad}:** ${producto.precio:.2f}")

    # Selección de dosis
    # Obtener dosis min y max según especie
    if especie == "Aves":
        dosis_info = producto.dosis_aves
    else:
        dosis_info = producto.dosis_cerdos

    if dosis_info is None:
        st.error("Este producto no tiene dosis definida para la especie seleccionada.")
        return

    tipo_dosis, dosis_min, dosis_max = dosis_info

    # Unidades para mostrar según tipo
    if tipo_dosis == "feed":
        unidad_dosis = "kg/ton de alimento"
    else:
        unidad_dosis = "mg/kg de peso vivo"

    st.subheader("⚙️ Dosis")
    opcion_dosis = st.radio(
        "Seleccionar dosis",
        ["Mínima", "Máxima", "Otra"],
        index=0,
        horizontal=True
    )

    if opcion_dosis == "Mínima":
        dosis_elegida = dosis_min
    elif opcion_dosis == "Máxima":
        dosis_elegida = dosis_max
    else:
        dosis_elegida = st.number_input(f"Ingrese dosis ({unidad_dosis})", min_value=0.0, value=dosis_min, step=0.1)

    st.info(f"Dosis seleccionada: {dosis_elegida} {unidad_dosis}")

    # Cálculo del alimento total
    alimento_ton = calcular_alimento_total(num_animales, consumo_por_animal)

    # Cálculo del producto necesario
    try:
        cantidad_producto = calcular_producto_necesario(
            producto, especie, dosis_elegida,
            peso_animal, num_animales, alimento_ton
        )
    except Exception as e:
        st.error(f"Error en el cálculo: {e}")
        return

    # Precio estimado
    precio_total = precio_estimado(cantidad_producto, producto.precio)

    # Resultados
    st.header("📊 Resultados")
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric("Cantidad total de alimento", f"{alimento_ton:.2f} toneladas")
    with col_res2:
        unidad = producto.unidad
        st.metric(f"Cantidad total de producto necesario", f"{cantidad_producto:.3f} {unidad}")
    with col_res3:
        st.metric("Precio estimado", f"${precio_total:.2f}")

    # Explicación del redondeo
    unidades_comprar = math.ceil(cantidad_producto)
    if cantidad_producto != unidades_comprar:
        st.caption(f"* El precio se calcula redondeando al entero superior: {unidades_comprar} {unidad} × ${producto.precio:.2f} = ${precio_total:.2f}")

    # Mostrar detalles del cálculo
    with st.expander("Ver detalles del cálculo"):
        st.write(f"**Número de animales:** {num_animales}")
        st.write(f"**Consumo por animal:** {consumo_por_animal} kg")
        st.write(f"**Peso animal promedio:** {peso_animal} kg")
        if tipo_dosis == "feed":
            st.write(f"**Dosis aplicada:** {dosis_elegida} kg de producto por tonelada de alimento")
            st.write(f"**Alimento total:** {alimento_ton} ton → Producto = {dosis_elegida} × {alimento_ton:.3f} = {cantidad_producto:.3f} {unidad}")
        else:
            st.write(f"**Dosis aplicada:** {dosis_elegida} mg de principio activo por kg de peso vivo")
            st.write(f"**Requerimiento diario de principio activo:** {dosis_elegida} mg/kg × {peso_animal} kg × {num_animales} = {dosis_elegida * peso_animal * num_animales:.0f} mg")
            if producto.unidad == "kg":
                st.write(f"**Concentración:** {producto.concentracion} mg/g → {producto.concentracion * 1000} mg/kg")
                st.write(f"**Producto necesario:** {cantidad_producto:.3f} kg")
            else:
                st.write(f"**Concentración:** {producto.concentracion} mg/ml → {producto.concentracion * 1000} mg/L")
                st.write(f"**Producto necesario:** {cantidad_producto:.3f} L")

if __name__ == "__main__":
    main()