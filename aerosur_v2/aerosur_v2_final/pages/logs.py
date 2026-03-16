import streamlit as st
import pandas as pd
from utils.supabase_client import get_client

def render():
    sb = get_client()
    st.markdown('<div class="section-title">📋 Log de Accesos</div>', unsafe_allow_html=True)

    try:
        rows = (
            sb.table("tblogacceso")
            .select("*, tbusuario(correo_login, rol)")
            .order("fecha_acceso", desc=True)
            .limit(100)
            .execute()
            .data
        )

        if not rows:
            st.info("No hay registros de acceso.")
            return

        # Métricas rápidas
        exitosos = sum(1 for r in rows if r["resultado"] == "Exitoso")
        fallidos  = len(rows) - exitosos

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"""<div class="aerosur-card"><h3>TOTAL REGISTROS</h3><div class="value">{len(rows)}</div></div>""", unsafe_allow_html=True)
        c2.markdown(f"""<div class="aerosur-card"><h3>EXITOSOS</h3><div class="value" style="color:#00FF9F">{exitosos}</div></div>""", unsafe_allow_html=True)
        c3.markdown(f"""<div class="aerosur-card"><h3>FALLIDOS</h3><div class="value" style="color:#FF3B5C">{fallidos}</div></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Tabla de logs
        data = []
        for r in rows:
            u = r.get("tbusuario") or {}
            resultado_icon = "✅" if r["resultado"] == "Exitoso" else "❌"
            data.append({
                "Fecha":    r["fecha_acceso"][:19].replace("T", " "),
                "Usuario":  u.get("correo_login", "—"),
                "Rol":      u.get("rol", "—"),
                "IP":       r.get("ip", "—"),
                "Resultado": f"{resultado_icon} {r['resultado']}",
            })

        df = pd.DataFrame(data)

        # Filtro por resultado
        filtro = st.selectbox("Filtrar por resultado", ["Todos", "Exitoso", "Fallido"])
        if filtro != "Todos":
            df = df[df["Resultado"].str.contains(filtro)]

        st.dataframe(df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(str(e))
