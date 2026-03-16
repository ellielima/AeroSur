import streamlit as st
from utils.supabase_client import get_client
from utils.auth import check_login, logout

st.set_page_config(
    page_title="AeroSur · Sistema de Gestión",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Estilos globales ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

/* Variables */
:root {
    --bg:       #04060F;
    --surface:  #0C1020;
    --border:   #1A2540;
    --accent:   #00D4FF;
    --accent2:  #FF6B35;
    --text:     #E8EDF5;
    --muted:    #5A6A8A;
    --success:  #00FF9F;
    --danger:   #FF3B5C;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Botones primarios */
.stButton > button {
    background: var(--accent) !important;
    color: #04060F !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #00AACF !important;
    transform: translateY(-1px) !important;
}

/* Inputs */
input, textarea, select, [data-baseweb="input"] input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 4px !important;
    font-family: 'Space Mono', monospace !important;
}
input:focus { border-color: var(--accent) !important; outline: none !important; }

/* Dataframes / Tablas */
[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: 8px !important; }

/* Cards personalizadas */
.aerosur-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.aerosur-card h3 {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    color: var(--muted);
    text-transform: uppercase;
    margin: 0 0 0.25rem 0;
}
.aerosur-card .value {
    font-family: 'Space Mono', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    color: var(--accent);
}

/* Badge de estado */
.badge-activo   { color: var(--success); font-size:0.75rem; font-family:'Space Mono',monospace; }
.badge-inactivo { color: var(--danger);  font-size:0.75rem; font-family:'Space Mono',monospace; }

/* Título de sección */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--text);
    border-left: 3px solid var(--accent);
    padding-left: 0.75rem;
    margin-bottom: 1.5rem;
}

/* Header superior */
.top-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem 0 1.5rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}
.top-header .logo {
    font-family: 'Space Mono', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 0.1em;
}

/* Selectbox */
[data-baseweb="select"] {
    background: var(--surface) !important;
    border-color: var(--border) !important;
}
[data-baseweb="select"] * { color: var(--text) !important; background: var(--surface) !important; }

/* Tabs */
[data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid var(--border) !important; }
[data-baseweb="tab"] { color: var(--muted) !important; font-family: 'Space Mono', monospace !important; }
[aria-selected="true"] { color: var(--accent) !important; border-bottom-color: var(--accent) !important; }

/* Ocultar botón hamburguesa y navegación de páginas */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebarNav"] { display: none !important; }
section[data-testid="stSidebarNav"] { display: none !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Inicializar sesión ────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# ── Routing ───────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    from pages import login
    login.render()
else:
    usuario = st.session_state.usuario

    # Sidebar nav
    with st.sidebar:
        st.markdown("""
        <div style='padding:1rem 0; border-bottom:1px solid #1A2540; margin-bottom:1rem;'>
            <div style='font-family:Space Mono,monospace; font-size:1.1rem; color:#00D4FF; font-weight:700;'>
                ✈ AEROSUR
            </div>
            <div style='font-family:Syne,sans-serif; font-size:0.7rem; color:#5A6A8A; letter-spacing:0.1em; text-transform:uppercase;'>
                Sistema de Gestión
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"<div style='font-family:Space Mono,monospace;font-size:0.75rem;color:#5A6A8A;margin-bottom:1rem;'>👤 {usuario['correo_login']}<br><span style='color:#00D4FF'>{usuario['rol']}</span></div>", unsafe_allow_html=True)

        page = st.radio(
            "Navegación",
            ["🏠  Dashboard", "✈️  Vuelos", "👥  Pasajeros", "🧳  Reservas",
             "👨‍✈️  Tripulación", "🛩️  Aviones", "👔  Empleados", "📋  Logs"],
            label_visibility="collapsed"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⏻  Cerrar sesión", use_container_width=True):
            logout()
            st.rerun()

    # Render página seleccionada
    clean = page.split("  ")[1].strip()

    if clean == "Dashboard":
        from pages import dashboard; dashboard.render()
    elif clean == "Vuelos":
        from pages import vuelos; vuelos.render()
    elif clean == "Pasajeros":
        from pages import pasajeros; pasajeros.render()
    elif clean == "Reservas":
        from pages import reservas; reservas.render()
    elif clean == "Tripulación":
        from pages import tripulacion; tripulacion.render()
    elif clean == "Aviones":
        from pages import aviones; aviones.render()
    elif clean == "Empleados":
        from pages import empleados; empleados.render()
    elif clean == "Logs":
        from pages import logs; logs.render()
