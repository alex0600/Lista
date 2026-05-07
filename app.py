import streamlit as st
import pandas as pd

# ==============================================================================
# CONFIGURACIÓN Y DISEÑO CSS
# ==============================================================================
st.set_page_config(layout="wide", page_title="CERO Compras", page_icon="🛒")

smoked_glass = (
    "background: rgba(255,255,255,0.033); "
    "backdrop-filter: blur(10px); "
    "-webkit-backdrop-filter: blur(10px); "
    "border-radius: 14px; "
    "border: 1px solid rgba(255,255,255,0.07); "
    "border-top: 1px solid rgba(255,255,255,0.11); "
    "padding: 15px;"
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

  /* ── Fondo principal con rayas diagonales ember ── */
  .stApp {
    background-color: #0c0c0e;
    background-image:
      repeating-linear-gradient(
        135deg,
        transparent,
        transparent 28px,
        rgba(234,88,12,0.10) 28px,
        rgba(234,88,12,0.10) 30px
      ),
      radial-gradient(ellipse at 75% 85%, rgba(234,88,12,0.13) 0%, transparent 58%),
      radial-gradient(ellipse at 18% 18%, rgba(180,60,0,0.08) 0%, transparent 52%);
    font-family: 'DM Sans', sans-serif;
    color: #F5EDE4;
  }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: #111114 !important;
    border-right: 1px solid rgba(255,255,255,0.05);
  }
  [data-testid="stSidebar"] * { color: #F5EDE4 !important; font-family: 'DM Sans', sans-serif !important; }

  /* ── Tipografía global ── */
  h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    color: #F5EDE4 !important;
    letter-spacing: -0.5px;
  }
  h1 { font-size: 1.9rem !important; }
  p, span, label, div, li { color: #F5EDE4 !important; font-family: 'DM Sans', sans-serif !important; }

  /* ── Tabs ── */
  [data-testid="stTabs"] [role="tablist"] {
    background: rgba(255,255,255,0.025);
    border-radius: 10px;
    padding: 3px;
    border: 1px solid rgba(255,255,255,0.06);
    gap: 2px;
  }
  [data-testid="stTabs"] button[role="tab"] {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    color: rgba(245,237,228,0.45) !important;
    border-radius: 8px !important;
    border: none !important;
    background: transparent !important;
    padding: 6px 14px !important;
    transition: all 0.15s;
  }
  [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background: rgba(234,88,12,0.18) !important;
    color: #EA580C !important;
    border: 1px solid rgba(234,88,12,0.35) !important;
  }
  [data-testid="stTabs"] button[role="tab"]:hover {
    color: #F5EDE4 !important;
    background: rgba(255,255,255,0.04) !important;
  }

  /* ── Inputs y selects ── */
  input, textarea,
  [data-testid="stNumberInput"] input,
  [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
  [data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
    color: #F5EDE4 !important;
    font-family: 'DM Sans', sans-serif !important;
  }
  [data-testid="stNumberInput"] input:focus,
  [data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within,
  [data-testid="stTextInput"] input:focus {
    border-color: rgba(234,88,12,0.50) !important;
    box-shadow: 0 0 0 2px rgba(234,88,12,0.08) !important;
  }
  .stSelectbox label, .stNumberInput label, .stTextInput label {
    font-size: 12px !important;
    color: rgba(245,237,228,0.45) !important;
    font-family: 'DM Sans', sans-serif !important;
  }

  /* ── Botones ── */
  .stButton > button {
    background: rgba(234,88,12,0.14) !important;
    border: 1px solid rgba(234,88,12,0.38) !important;
    border-radius: 9px !important;
    color: #EA580C !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 12.5px !important;
    font-weight: 600 !important;
    letter-spacing: 0.2px;
    transition: background 0.15s, box-shadow 0.15s;
  }
  .stButton > button:hover {
    background: rgba(234,88,12,0.26) !important;
    box-shadow: 0 0 14px rgba(234,88,12,0.14) !important;
  }
  .stButton > button:disabled {
    background: rgba(255,255,255,0.04) !important;
    border-color: rgba(255,255,255,0.10) !important;
    color: rgba(245,237,228,0.30) !important;
  }

  /* ── Botón primary ── */
  .stButton > button[kind="primary"] {
    background: rgba(234,88,12,0.28) !important;
    border-color: rgba(234,88,12,0.65) !important;
    box-shadow: 0 0 18px rgba(234,88,12,0.18) !important;
  }

  /* ── Divisores ── */
  hr, [data-testid="stDivider"] { border-color: rgba(255,255,255,0.06) !important; }

  /* ── Info / Warning / Success ── */
  [data-testid="stAlert"] {
    background: rgba(234,88,12,0.08) !important;
    border: 1px solid rgba(234,88,12,0.22) !important;
    border-radius: 12px !important;
    color: #F5EDE4 !important;
  }
  [data-testid="stAlert"][data-baseweb="notification"][kind="warning"] {
    background: rgba(217,119,6,0.10) !important;
    border-color: rgba(217,119,6,0.28) !important;
  }
  [data-testid="stAlert"][data-baseweb="notification"][kind="success"] {
    background: rgba(16,185,129,0.09) !important;
    border-color: rgba(16,185,129,0.28) !important;
  }

  /* ── File uploader ── */
  [data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px dashed rgba(234,88,12,0.30) !important;
    border-radius: 12px !important;
  }

  /* ── Metric / write boxes ── */
  [data-testid="stMetric"] {
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
    padding: 8px 12px;
    border: 1px solid rgba(255,255,255,0.06);
  }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 5px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: rgba(234,88,12,0.30); border-radius: 4px; }
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
st.title("🛒 CERO Compras — Optimizador")

tab_busca, tab_lista, tab_compara, tab_ticket = st.tabs(
    ["🔍 Buscador", "📋 Mi Lista", "⚡ Comparador", "🧾 Subir Ticket"]
)

# ------------------------------------------------------------------------------
# TAB 1: BUSCADOR
# ------------------------------------------------------------------------------
with tab_busca:
    df_cat = pd.DataFrame({
        "ID": ["001", "002", "003", "004", "005", "006", "007"],
        "Producto": ["Manzana", "Leche Lala", "Leche Lala", "Leche Lala", "Pan Bimbo", "Huevo San Juan", "Tomate"],
        "Variante": ["Roja", "Deslactosada", "Light", "Entera", "Blanco Grande", "Blanco 18 pz", "Bola"],
        "Categoria": ["Frutas", "Lacteos", "Lacteos", "Lacteos", "Despensa", "Lacteos", "Verduras"]
    })

    c1, c2 = st.columns([2, 1])
    busqueda = c1.text_input("Buscar producto...", placeholder="Ej. Lala, Manzana, Jabón...")
    categoria = c2.selectbox("Categoría", ["Todas"] + list(df_cat['Categoria'].unique()))

    df_filt = df_cat.copy()
    if busqueda:
        df_filt = df_filt[
            df_filt['Producto'].str.contains(busqueda, case=False) |
            df_filt['Variante'].str.contains(busqueda, case=False)
        ]
    if categoria != "Todas":
        df_filt = df_filt[df_filt['Categoria'] == categoria]

    productos_base = df_filt['Producto'].unique()
    st.markdown(
        f"<p style='font-size:12px; color:rgba(245,237,228,0.40); margin-bottom:12px;'>"
        f"Mostrando {len(productos_base)} productos base</p>",
        unsafe_allow_html=True
    )

    cols = st.columns(3)

    for i, prod in enumerate(productos_base):
        with cols[i % 3]:
            variantes_df = df_filt[df_filt['Producto'] == prod]
            cat_actual = variantes_df.iloc[0]['Categoria']
            icono = ICONOS.get(cat_actual, "📦")

            st.markdown(f"""
            <div style="{smoked_glass} margin-bottom: 10px; text-align: center;
                         position: relative; overflow: hidden;">
                <div style="
                    position: absolute; top:0; left:0; right:0; height:2px;
                    background: linear-gradient(90deg, transparent, rgba(234,88,12,0.7), transparent);
                "></div>
                <div style="font-size:34px; line-height:1; margin-bottom:6px;">{icono}</div>
                <b style="font-size:17px; color:#EA580C;
                   font-family:'Syne',sans-serif; letter-spacing:0.2px;">{prod}</b>
            </div>
            """, unsafe_allow_html=True)

            lista_variantes = variantes_df['Variante'].tolist()
            var_seleccionada = st.selectbox("Elige el tipo:", lista_variantes, key=f"var_{prod}")
            id_seleccionado = variantes_df[variantes_df['Variante'] == var_seleccionada]['ID'].values[0]

            col_q, col_u = st.columns([1, 1])
            cant = col_q.number_input("Cantidad", min_value=0.5, value=1.0, step=0.5, key=f"cant_{prod}")
            uni = col_u.selectbox("Medida", ["pz", "kg", "L", "g", "paquete"], key=f"uni_{prod}")

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
            c1.write(f"🔹 **{item['Producto']}** — {item.get('Variante', '')}")
            cantidad_segura = item.get('Cantidad', 1)
            unidad_segura = item.get('Unidad', 'pz')
            c2.write(f"**{cantidad_segura} {unidad_segura}**")
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
