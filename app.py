import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from google import genai
from google.genai import types
from pydantic import BaseModel
import concurrent.futures
import requests
import urllib.parse
from datetime import datetime

# ==============================================================================
# 1. CONFIGURACIÓN E INFRAESTRUCTURA VISUAL (Warm Sand & Discreción)
# ==============================================================================
# Título y favicon discretos para el navegador
st.set_page_config(layout="wide", page_title="Dashboard UI", page_icon="📊")

bg_main   = "#1a1510"
glow_a    = "rgba(217,119,6,0.15)"
glow_b    = "rgba(100,60,10,0.1)"
accent    = "#F59E0B"
accent_rgb= "245,158,11"
text_main = "#FEF3C7"
text_muted= "rgba(254,243,199,0.4)"

# Emojis solo para organización visual de categorías
CAT_EMOJIS = {
    "Frutas": "🍎", "Verduras": "🥦", "Lácteos": "🥛", 
    "Despensa": "🥫", "Carnes": "🥩", "Limpieza": "🧼", 
    "Aseo Personal": "🧴", "Bebidas": "🥤"
}

st.markdown(f"""
<style>
    .stApp {{
        background-color: {bg_main};
        background-image: radial-gradient(ellipse at 20% 25%, {glow_a} 0%, transparent 55%), 
                          radial-gradient(ellipse at 80% 75%, {glow_b} 0%, transparent 50%);
        color: {text_main};
    }}
    h1, h2, h3, p, span, label, div {{ color: {text_main} !important; }}
    
    .glass-card {{
        background: rgba(255,255,255,0.03); 
        border: 1px solid rgba(255,255,255,0.06); 
        border-top: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px; 
        padding: 1.2rem; 
        margin-bottom: 0.75rem; 
        transition: border-color 0.2s;
    }}
    .glass-card.selected {{
        border: 1.5px solid rgba({accent_rgb}, 0.6); 
        background: rgba({accent_rgb}, 0.05);
    }}
    .card-emoji {{ font-size: 32px; text-align: center; margin-bottom: 5px; opacity: 0.9; }}
    .card-title {{ font-size: 17px !important; font-weight: 600; color: {accent} !important; margin: 0 0 2px 0; }}
    .card-sub {{ font-size: 13px !important; color: {text_muted} !important; margin: 0; }}
    .badge {{
        display: inline-block; font-size: 10px !important; padding: 2px 8px; border-radius: 20px;
        background: rgba({accent_rgb}, 0.1); color: {accent} !important; 
        border: 1px solid rgba({accent_rgb}, 0.2); margin-left: 6px;
    }}
    .card-divider {{ border: none; border-top: 1px solid rgba(255,255,255,0.05); margin: 12px 0; }}
    
    [data-testid="stNumberInput"] input, [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        background: rgba(255,255,255,0.04) !important; 
        border: 1px solid rgba(255,255,255,0.08) !important; 
        border-radius: 8px !important; 
        color: {text_main} !important;
    }}
    .stButton > button {{
        background: rgba({accent_rgb}, 0.1) !important; 
        border: 1px solid rgba({accent_rgb}, 0.3) !important;
        border-radius: 8px !important; 
        color: {accent} !important; 
        transition: background 0.2s; 
        width: 100%;
    }}
    .stButton > button:hover {{ background: rgba({accent_rgb}, 0.2) !important; }}
    hr {{ border-color: rgba(255,255,255,0.07) !important; }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. MOTORES DE DATOS Y CONEXIÓN
# ==============================================================================
@st.cache_resource
def conectar_google():
    cred_info = dict(st.secrets["gcp_service_account"])
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(cred_info, scopes=scope)
    return gspread.authorize(creds)

@st.cache_data(ttl=300)
def cargar_datos(_client):
    try:
        sh = _client.open_by_url(st.secrets["sheets"]["spreadsheet_url"])
        df_cat = pd.DataFrame(sh.worksheet("Catalogo").get_all_records())
        df_tickets = pd.DataFrame(sh.worksheet("Tickets").get_all_records())
        return df_cat, df_tickets
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        st.stop()

# Esquemas de IA
class PrecioIA(BaseModel):
    encontrado: bool
    nombre_tienda: str
    precio: float

class TicketIA(BaseModel):
    items: list[dict]

# ==============================================================================
# 3. LÓGICA DE ESTADO
# ==============================================================================
if "carrito" not in st.session_state:
    st.session_state.carrito = []

def en_carrito(id_prod):
    return any(p['ID'] == id_prod for p in st.session_state.carrito)

client_gs = conectar_google()
df_catalogo, df_tickets = cargar_datos(client_gs)

# ==============================================================================
# 4. INTERFAZ Y PESTAÑAS
# ==============================================================================
st.markdown("<h2 style='text-align: center; color: #F59E0B;'>Workspace Analytics</h2>", unsafe_allow_html=True)

tab_busca, tab_lista, tab_compara, tab_ticket = st.tabs(["Directorio", "Selección", "Análisis Web", "Recibos"])

# --- TAB 1: BUSCADOR ---
with tab_busca:
    if df_catalogo.empty:
        st.warning("El directorio está vacío.")
    else:
        c1, c2 = st.columns([2, 1])
        busqueda = c1.text_input("Buscar ítem...", placeholder="Ej. Lácteos...")
        categorias = ["Todas"] + list(df_catalogo['Categoria'].unique())
        categoria = c2.selectbox("Filtro", categorias)

        df_filt = df_catalogo.copy()
        if busqueda:
            df_filt = df_filt[df_filt['Producto'].str.contains(busqueda, case=False) | df_filt['Variante'].str.contains(busqueda, case=False)]
        if categoria != "Todas":
            df_filt = df_filt[df_filt['Categoria'] == categoria]

        productos_base = df_filt['Producto'].unique()
        
        cols = st.columns(3)
        for i, prod in enumerate(productos_base[:30]):
            with cols[i % 3]:
                var_df = df_filt[df_filt['Producto'] == prod]
                cat_actual = var_df.iloc[0]['Categoria']
                emoji = CAT_EMOJIS.get(cat_actual, "📦")
                
                estado_clase = "selected" if any(en_carrito(pid) for pid in var_df['ID'].tolist()) else ""
                
                st.markdown(f"""
                <div class="glass-card {estado_clase}">
                    <div class="card-emoji">{emoji}</div>
                    <p class="card-title">{prod}</p>
                    <p class="card-sub">{cat_actual} <span class="badge">{len(var_df)} var</span></p>
                    <hr class="card-divider">
                </div>
                """, unsafe_allow_html=True)
                
                lista_vars = var_df['Variante'].tolist()
                var_sel = st.selectbox("Variante", lista_vars, key=f"v_{prod}", label_visibility="collapsed")
                id_sel = var_df[var_df['Variante'] == var_sel]['ID'].values[0]
                
                col_q, col_u = st.columns(2)
                cant = col_q.number_input("Cant.", min_value=0.5, value=1.0, step=0.5, key=f"q_{prod}")
                uni = col_u.selectbox("Unidad", ["pz", "kg", "L", "paq"], key=f"u_{prod}")
                
                if en_carrito(id_sel):
                    st.button("✓ En selección", key=f"b_{prod}", disabled=True)
                else:
                    if st.button("＋ Agregar", key=f"b_{prod}"):
                        st.session_state.carrito.append({"ID": id_sel, "Producto": prod, "Variante": var_sel, "Cantidad": cant, "Unidad": uni})
                        st.rerun()

# --- TAB 2: MI LISTA ---
with tab_lista:
    if not st.session_state.carrito:
        st.info("No hay ítems seleccionados.")
    else:
        for item in st.session_state.carrito:
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"**{item['Producto']}** ({item['Variante']})")
            c2.write(f"{item['Cantidad']} {item['Unidad']}")
            if c3.button("Remover", key=f"del_{item['ID']}"):
                st.session_state.carrito = [p for p in st.session_state.carrito if p['ID'] != item['ID']]
                st.rerun()
        
        st.divider()
        if st.button("☁️ Sincronizar Base de Datos", type="primary"):
            try:
                hoja_activa = client_gs.open_by_url(st.secrets["sheets"]["spreadsheet_url"]).worksheet("Carrito_Activo")
                hoja_activa.clear() 
                datos_sync = [["ID", "Producto", "Variante", "Cantidad", "Unidad"]]
                datos_sync.extend([[p['ID'], p['Producto'], p['Variante'], p['Cantidad'], p['Unidad']] for p in st.session_state.carrito])
                hoja_activa.update("A1", datos_sync)
                st.success("¡Sincronización exitosa!")
            except Exception as e:
                st.error(f"Error: {e}")

# --- TAB 3: COMPARADOR ---
with tab_compara:
    if not st.session_state.carrito:
        st.warning("Selecciona ítems primero.")
    else:
        if st.button("🚀 Iniciar Análisis Concurrente"):
            
            def buscar_precio(prod, variante, tienda):
                query = urllib.parse.quote(f"{prod} {variante}")
                url_map = {"Walmart": f"https://super.walmart.com.mx/buscar?q={query}", 
                           "Alsuper": f"https://alsuper.com/search?q={query}"}
                try:
                    r = requests.get('http://api.scraperapi.com', 
                                     params={'api_key': st.secrets["scraperapi"]["api_key"], 
                                             'url': url_map[tienda], 'render': 'true'}, timeout=45)
                    if r.status_code != 200: return {"tienda": tienda, "error": True, "msg": f"Status API: {r.status_code}"}
                    
                    ai_client = genai.Client(api_key=st.secrets["gemini"]["api_key"])
                    prompt = f"HTML de {tienda}. Busca {prod} {variante} en CP 31200. Devuelve el precio."
                    res = ai_client.models.generate_content(
                        model="gemini-2.0-flash", 
                        contents=[r.text[:300000], prompt], 
                        config=types.GenerateContentConfig(response_mime_type="application/json", 
                                                         response_schema=PrecioIA)
                    )
                    return {"tienda": tienda, "data": res.parsed, "error": False}
                except Exception as err:
                    return {"tienda": tienda, "error": True, "msg": str(err)}

            resultados_guardar = []
            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
            
            with st.status("Analizando fuentes web...", expanded=True) as status:
                for item in st.session_state.carrito:
                    st.write(f"Procesando: **{item['Producto']}**")
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        futuros = [executor.submit(buscar_precio, item['Producto'], item['Variante'], t) for t in ["Walmart", "Alsuper"]]
                        
                        cols_res = st.columns(2)
                        for idx, fut in enumerate(concurrent.futures.as_completed(futuros)):
                            res = fut.result()
                            with cols_res[idx]:
                                if not res["error"] and res["data"].encontrado:
                                    st.success(f"{res['tienda']}: ${res['data'].precio}")
                                    resultados_guardar.append([item['ID'], res['tienda'], res['data'].precio, fecha_hoy])
                                else:
                                    # MOSTRAR EL ERROR REAL AQUÍ
                                    mensaje_error = res.get('msg', 'No disponible / No encontrado')
                                    st.error(f"{res['tienda']}: {mensaje_error}")
                    st.divider()
                status.update(label="Análisis completado.", state="complete", expanded=False)

            if resultados_guardar:
                try:
                    hoja_hist = client_gs.open_by_url(st.secrets["sheets"]["spreadsheet_url"]).worksheet("Historial_Precios")
                    hoja_hist.append_rows(resultados_guardar)
                    st.toast("Historial actualizado.")
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

# --- TAB 4: TICKETS ---
with tab_ticket:
    col_t1, col_t2 = st.columns([2, 1])
    
    with col_t2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<p class='card-sub'>Gasto Acumulado</p>", unsafe_allow_html=True)
        try:
            if not df_tickets.empty and 'Precio_Pagado' in df_tickets.columns:
                total_gastado = pd.to_numeric(df_tickets['Precio_Pagado'], errors='coerce').sum()
                st.markdown(f"<h2 style='color:#10B981; margin:0;'>${total_gastado:,.2f}</h2>", unsafe_allow_html=True)
            else:
                st.markdown("<h2 style='color:#10B981; margin:0;'>$0.00</h2>", unsafe_allow_html=True)
        except Exception as e:
            st.markdown("<h2 style='color:#10B981; margin:0;'>$0.00</h2>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_t1:
        foto = st.file_uploader("Documento de respaldo", type=['jpg', 'jpeg', 'png'])
        if foto and st.button("Analizar Documento"):
            with st.spinner("Procesando con IA..."):
                try:
                    ai_client = genai.Client(api_key=st.secrets["gemini"]["api_key"])
                    prompt = "Extrae productos y precios del ticket. Clasifica: Esencial o Extra."
                    imagen_part = types.Part.from_bytes(data=foto.getvalue(), mime_type=foto.type)
                    
                    res = ai_client.models.generate_content(
                        model="gemini-2.0-flash", 
                        contents=[imagen_part, prompt], 
                        config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=TicketIA)
                    )
                    
                    datos_extraidos = res.parsed.items
                    # CORREGIDO EL BUG DE DUPLICIDAD EN LA CLAVE "SECRETS" AQUÍ
                    hoja_tickets = client_gs.open_by_url(st.secrets["sheets"]["spreadsheet_url"]).worksheet("Tickets")
                    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
                    
                    filas_ticket = []
                    for d in datos_extraidos:
                        filas_ticket.append([fecha_hoy, "Local", d.get("item", "Desc"), d.get("precio", 0), d.get("tipo", "ND")])
                        st.write(f"- {d.get('item')}: ${d.get('precio')}")
                    
                    hoja_tickets.append_rows(filas_ticket)
                    st.success("Documento registrado.")
                except Exception as e:
                    st.error(f"Error: {e}")
