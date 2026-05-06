import streamlit as st
import pandas as pd

# ==============================================================================
# CONFIGURACIÓN Y DISEÑO CSS
# ==============================================================================
st.set_page_config(layout="wide", page_title="CERO Compras", page_icon="🛒")

smoked_glass = "background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.1); padding: 15px;"

st.markdown(f"""
<style>
    .stApp {{ background: #0b132b; color: white; }}
    h1, h2, h3, p {{ color: white !important; }}
    /* Ajuste para que los selectores se vean bien en fondo oscuro */
    .stSelectbox label, .stNumberInput label {{ font-size: 12px !important; color: #cbd5e1 !important; }}
</style>
""", unsafe_allow_html=True)

# Diccionario de iconos
ICONOS = {"Frutas": "🍎", "Verduras": "🥦", "Lacteos": "🥛", "Despensa": "🥫", "Carnes": "🥩", "Limpieza": "🧼", "Todas": "🔍"}

# Inicializar memoria rápida (Carrito)
if "carrito" not in st.session_state:
    st.session_state.carrito = []

# Función para saber si una variante exacta ya está en el carrito
def producto_en_carrito(id_prod):
    return any(item.get('ID') == id_prod for item in st.session_state.carrito)

# ==============================================================================
# UI PRINCIPAL
# ==============================================================================
st.title("🛒 CERO Compras - Optimizador")

tab_busca, tab_lista, tab_compara, tab_ticket = st.tabs(["🔍 Buscador", "📋 Mi Lista", "⚡ Comparador", "🧾 Subir Ticket"])

# ------------------------------------------------------------------------------
# TAB 1: BUSCADOR (Tarjetas Híbridas con Selectores)
# ------------------------------------------------------------------------------
with tab_busca:
    # DATOS DE PRUEBA
    df_cat = pd.DataFrame({
        "ID": ["001", "002", "003", "004", "005", "006", "007"],
        "Producto": ["Manzana", "Leche Lala", "Leche Lala", "Leche Lala", "Pan Bimbo", "Huevo San Juan", "Tomate"],
        "Variante": ["Roja", "Deslactosada", "Light", "Entera", "Blanco Grande", "Blanco 18 pz", "Bola"],
        "Categoria": ["Frutas", "Lacteos", "Lacteos", "Lacteos", "Despensa", "Lacteos", "Verduras"]
    })

    # Buscador superior
    c1, c2 = st.columns([2, 1])
    busqueda = c1.text_input("Buscar producto...", placeholder="Ej. Lala, Manzana, Jabón...")
    categoria = c2.selectbox("Categoría", ["Todas"] + list(df_cat['Categoria'].unique()))

    # Lógica de filtrado
    df_filt = df_cat.copy()
    if busqueda:
        df_filt = df_filt[df_filt['Producto'].str.contains(busqueda, case=False) | df_filt['Variante'].str.contains(busqueda, case=False)]
    if categoria != "Todas":
        df_filt = df_filt[df_filt['Categoria'] == categoria]

    # Agrupamos por Producto Base para hacer las tarjetas
    productos_base = df_filt['Producto'].unique()
    st.write(f"Mostrando {len(productos_base)} productos base...")

    # GRID DE 3 COLUMNAS PARA LAS TARJETAS
    cols = st.columns(3)
    
    for i, prod in enumerate(productos_base):
        with cols[i % 3]:
            # Obtenemos todas las variantes de este producto
            variantes_df = df_filt[df_filt['Producto'] == prod]
            cat_actual = variantes_df.iloc[0]['Categoria']
            icono = ICONOS.get(cat_actual, "📦")
            
            # 1. ENCABEZADO DE LA TARJETA (Estilo Smoked Glass)
            st.markdown(f"""
            <div style="{smoked_glass} margin-bottom: 10px; text-align: center;">
                <div style="font-size:35px;">{icono}</div>
                <b style="font-size:18px; color:#38BDF8;">{prod}</b>
            </div>
            """, unsafe_allow_html=True)
            
            # 2. SELECTOR DE VARIANTE
            lista_variantes = variantes_df['Variante'].tolist()
            var_seleccionada = st.selectbox("Elige el tipo:", lista_variantes, key=f"var_{prod}")
            
            # Encontramos el ID de la variante exacta que seleccionó
            id_seleccionado = variantes_df[variantes_df['Variante'] == var_seleccionada]['ID'].values[0]
            
            # 3. CANTIDAD Y UNIDAD DE MEDIDA
            col_q, col_u = st.columns([1, 1])
            cant = col_q.number_input("Cantidad", min_value=0.5, value=1.0, step=0.5, key=f"cant_{prod}")
            uni = col_u.selectbox("Medida", ["pz", "kg", "L", "g", "paquete"], key=f"uni_{prod}")
            
            # 4. BOTÓN DE AÑADIR (Lógica de bloque)
            ya_agregado = producto_en_carrito(id_seleccionado)
            
            if ya_agregado:
                st.button("✅ En Lista", key=f"btn_{prod}", disabled=True, use_container_width=True)
            else:
                if st.button("🛒 Añadir", key=f"btn_{prod}", use_container_width=True):
                    st.session_state.carrito.append({
                        "ID": id_seleccionado,
                        "Producto": prod,
                        "Variante": var_seleccionada,
                        "Cantidad": cant,
                        "Unidad": uni
                    })
                    st.rerun()
            
            # Separador visual entre tarjetas si hay muchas hacia abajo
            st.write("---")

# ------------------------------------------------------------------------------
# TAB 2: MI LISTA
# ------------------------------------------------------------------------------
with tab_lista:
    st.subheader("Tu Lista para la Semana")
    
    if not st.session_state.carrito:
        st.info("No hay productos en tu carrito. ¡Ve al buscador!")
    else:
        for item in st.session_state.carrito:
            c1, c2, c3 = st.columns([4, 2, 1])
            # Detalles del producto
            c1.write(f"🔹 **{item['Producto']}** - {item.get('Variante', '')}")
            
            # Cantidad y Unidad rescatada de forma segura
            cantidad_segura = item.get('Cantidad', 1)
            unidad_segura = item.get('Unidad', 'pz')
            c2.write(f"**{cantidad_segura} {unidad_segura}**") 
            
            # Botón de eliminar
            if c3.button("🗑️", key=f"del_{item['ID']}"):
                st.session_state.carrito = [p for p in st.session_state.carrito if p['ID'] != item['ID']]
                st.rerun()
        
        st.divider()
        if st.button("☁️ Guardar Lista en la Nube", type="primary"):
            st.success("¡Lista guardada en Google Sheets (Simulado)!")

# ------------------------------------------------------------------------------
# TAB 3: COMPARADOR EN VIVO
# ------------------------------------------------------------------------------
with tab_compara:
    st.subheader("Cotización Inteligente")
    if not st.session_state.carrito:
        st.warning("Agrega productos primero en el Buscador.")
    else:
        st.info("💡 Aquí irá la integración con ScraperAPI y Walmart/Sams/Alsuper.")

# ------------------------------------------------------------------------------
# TAB 4: SUBIR TICKET
# ------------------------------------------------------------------------------
with tab_ticket:
    st.subheader("Registrar Compra Final")
    st.write("Sube la foto de tu ticket para registrar precios reales y gastos extra.")
    st.file_uploader("Tomar foto o subir archivo", type=['jpg', 'jpeg', 'png'])
