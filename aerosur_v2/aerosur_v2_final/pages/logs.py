import streamlit as st
import pandas as pd
import io
from datetime import date
from utils.supabase_client import get_client

# PDF
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

def generar_pdf(df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Título
    story.append(Paragraph("AEROSUR - LOG DE ACCESOS", styles["Title"]))
    story.append(Spacer(1, 12))

    # Convertir dataframe a tabla
    data = [df.columns.tolist()] + df.values.tolist()

    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.grey),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),0.5,colors.black),
        ("FONTSIZE",(0,0),(-1,-1),8),
    ]))

    story.append(table)
    doc.build(story)

    buffer.seek(0)
    return buffer


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

        # Métricas
        exitosos = sum(1 for r in rows if r["resultado"] == "Exitoso")
        fallidos  = len(rows) - exitosos

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"""<div class="aerosur-card"><h3>TOTAL REGISTROS</h3><div class="value">{len(rows)}</div></div>""", unsafe_allow_html=True)
        c2.markdown(f"""<div class="aerosur-card"><h3>EXITOSOS</h3><div class="value" style="color:#00FF9F">{exitosos}</div></div>""", unsafe_allow_html=True)
        c3.markdown(f"""<div class="aerosur-card"><h3>FALLIDOS</h3><div class="value" style="color:#FF3B5C">{fallidos}</div></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Tabla
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

        # =========================
        # 📅 FILTRO POR FECHAS
        # =========================
        st.markdown("### 📅 Filtrar por rango de fechas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fecha_inicio = st.date_input("Fecha inicio", value=None)
        
        with col2:
            fecha_fin = st.date_input("Fecha fin", value=None)
        
        # Convertir columna Fecha a datetime
        df["Fecha_dt"] = pd.to_datetime(df["Fecha"], errors="coerce")
        
        # Aplicar filtros
        if fecha_inicio:
            df = df[df["Fecha_dt"] >= pd.to_datetime(fecha_inicio)]
        
        if fecha_fin:
            df = df[df["Fecha_dt"] <= pd.to_datetime(fecha_fin)]
        
        # Eliminar columna auxiliar
        df = df.drop(columns=["Fecha_dt"])

        st.dataframe(df, use_container_width=True, hide_index=True)

        # =========================
        # 📄 BOTÓN PDF
        # =========================
        pdf = generar_pdf(df)

        st.download_button(
            label="📄 Descargar PDF",
            data=pdf,
            file_name=f"log_accesos_{date.today()}.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(str(e))
