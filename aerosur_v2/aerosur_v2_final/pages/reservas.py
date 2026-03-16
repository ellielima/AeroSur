import streamlit as st
import pandas as pd
import io
from utils.supabase_client import get_client

def generar_pdf_reserva(reserva: dict) -> bytes:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
    except ImportError:
        raise ImportError("reportlab no está instalado. Ejecuta: pip install reportlab")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            leftMargin=0.75*inch, rightMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story  = []

    azul_oscuro = colors.HexColor("#04060F")
    azul_acento = colors.HexColor("#00D4FF")
    gris_medio  = colors.HexColor("#5A6A8A")

    estilo_titulo    = ParagraphStyle("titulo", parent=styles["Normal"], fontSize=22, fontName="Helvetica-Bold", textColor=azul_oscuro, spaceAfter=4)
    estilo_subtitulo = ParagraphStyle("subtitulo", parent=styles["Normal"], fontSize=10, fontName="Helvetica", textColor=gris_medio, spaceAfter=20)
    estilo_seccion   = ParagraphStyle("seccion", parent=styles["Normal"], fontSize=8, fontName="Helvetica-Bold", textColor=gris_medio, spaceBefore=16, spaceAfter=6)
    estilo_campo     = ParagraphStyle("campo", parent=styles["Normal"], fontSize=10, fontName="Helvetica", textColor=azul_oscuro)
    id_style         = ParagraphStyle("id_box", parent=styles["Normal"], fontSize=11, fontName="Helvetica-Bold", textColor=azul_acento)

    story.append(Paragraph("AEROSUR", estilo_titulo))
    story.append(Paragraph("Comprobante de Reserva de Vuelo", estilo_subtitulo))
    story.append(HRFlowable(width="100%", thickness=2, color=azul_acento, spaceAfter=16))
    story.append(Paragraph(f"RESERVA #{reserva.get('id_reserva','—')}", id_style))
    story.append(Paragraph(f"Fecha de reserva: {reserva.get('fecha_reserva','—')}", estilo_campo))
    story.append(Spacer(1, 16))

    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#1A2540"), spaceAfter=8))
    story.append(Paragraph("DATOS DEL PASAJERO", estilo_seccion))
    tabla_pas = Table([
        ["Nombre completo",    reserva.get("pasajero_nombre","—")],
        ["Numero de pasaporte",reserva.get("pasaporte","—")],
        ["Nacionalidad",       reserva.get("nacionalidad","—")],
    ], colWidths=[2.2*inch, 4.5*inch])
    tabla_pas.setStyle(TableStyle([
        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),("FONTNAME",(1,0),(1,-1),"Helvetica"),
        ("FONTSIZE",(0,0),(-1,-1),10),
        ("TEXTCOLOR",(0,0),(0,-1),gris_medio),("TEXTCOLOR",(1,0),(1,-1),azul_oscuro),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[colors.HexColor("#F7F9FC"),colors.white]),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("LEFTPADDING",(0,0),(-1,-1),10),
        ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#DDE3ED")),
    ]))
    story.append(tabla_pas)
    story.append(Spacer(1,8))

    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#1A2540"), spaceAfter=8))
    story.append(Paragraph("INFORMACION DEL VUELO", estilo_seccion))
    tabla_vuelo = Table([
        ["Numero de vuelo",  reserva.get("numero_vuelo","—")],
        ["Origen",           reserva.get("origen","—")],
        ["Destino",          reserva.get("destino","—")],
        ["Fecha de salida",  reserva.get("fecha_salida","—")],
        ["Fecha de llegada", reserva.get("fecha_llegada","—")],
        ["Asiento asignado", reserva.get("numero_asiento","—")],
    ], colWidths=[2.2*inch, 4.5*inch])
    tabla_vuelo.setStyle(TableStyle([
        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),("FONTNAME",(1,0),(1,-1),"Helvetica"),
        ("FONTSIZE",(0,0),(-1,-1),10),
        ("TEXTCOLOR",(0,0),(0,-1),gris_medio),("TEXTCOLOR",(1,0),(1,-1),azul_oscuro),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[colors.HexColor("#F7F9FC"),colors.white]),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("LEFTPADDING",(0,0),(-1,-1),10),
        ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#DDE3ED")),
    ]))
    story.append(tabla_vuelo)
    story.append(Spacer(1,24))
    story.append(HRFlowable(width="100%", thickness=1, color=azul_acento, spaceAfter=8))
    pie_style = ParagraphStyle("pie", parent=styles["Normal"], fontSize=8, fontName="Helvetica", textColor=gris_medio, alignment=1)
    story.append(Paragraph("AeroSur · Sistema de Gestion de Vuelos · Documento generado automaticamente", pie_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def render():
    sb = get_client()
    st.markdown('<div class="section-title">🧳 Gestión de Reservas</div>', unsafe_allow_html=True)

    if st.session_state.get("mensaje_exito"):
        st.success(st.session_state.mensaje_exito)
        st.session_state.mensaje_exito = ""

    tab1, tab2 = st.tabs(["📋  Listado", "➕  Nueva reserva"])

    with tab1:
        try:
            rows = (
                sb.table("tbreserva")
                .select("id_reserva, fecha_reserva, id_asiento, id_vuelo, tbpasajero(nombre, apellido, pasaporte, nacionalidad), tbvuelo(numero_vuelo, origen, destino, fecha_salida, fecha_llegada)")
                .order("fecha_reserva", desc=True)
                .execute()
                .data
            )

            if not rows:
                st.info("No hay reservas registradas.")
            else:
                data = []
                for r in rows:
                    p = r.get("tbpasajero") or {}
                    v = r.get("tbvuelo") or {}
                    num_asiento = ""
                    if r.get("id_asiento"):
                        try:
                            ad = sb.table("tbasiento").select("numero_asiento").eq("id_asiento", r["id_asiento"]).single().execute().data
                            num_asiento = ad.get("numero_asiento","") if ad else ""
                        except:
                            pass
                    data.append({
                        "ID":               r["id_reserva"],
                        "Pasajero":         f"{p.get('nombre','')} {p.get('apellido','')}",
                        "Pasaporte":        p.get("pasaporte",""),
                        "Vuelo":            v.get("numero_vuelo",""),
                        "Ruta":             f"{v.get('origen','')} → {v.get('destino','')}",
                        "Asiento":          num_asiento,
                        "Fecha":            (r.get("fecha_reserva") or "")[:16].replace("T"," "),
                        "_pasajero_nombre": f"{p.get('nombre','')} {p.get('apellido','')}",
                        "_pasaporte":       p.get("pasaporte",""),
                        "_nacionalidad":    p.get("nacionalidad",""),
                        "_numero_vuelo":    v.get("numero_vuelo",""),
                        "_origen":          v.get("origen",""),
                        "_destino":         v.get("destino",""),
                        "_fecha_salida":    (v.get("fecha_salida") or "")[:16].replace("T"," "),
                        "_fecha_llegada":   (v.get("fecha_llegada") or "")[:16].replace("T"," "),
                        "_num_asiento":     num_asiento,
                        "_fecha_reserva":   (r.get("fecha_reserva") or "")[:16].replace("T"," "),
                    })

                cols_visibles = ["ID","Pasajero","Pasaporte","Vuelo","Ruta","Asiento","Fecha"]
                st.dataframe(pd.DataFrame(data)[cols_visibles], use_container_width=True, hide_index=True)

                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    id_sel = st.selectbox("Seleccionar reserva (ID)", [r["ID"] for r in data])

                reserva_sel = next((r for r in data if r["ID"] == id_sel), None)

                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🗑️  Cancelar reserva", use_container_width=True):
                        sb.table("tbreserva").delete().eq("id_reserva", id_sel).execute()
                        st.session_state.mensaje_exito = "✅ Reserva cancelada correctamente."
                        st.rerun()

                with col3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if reserva_sel:
                        try:
                            pdf_data = generar_pdf_reserva({
                                "id_reserva":      reserva_sel["ID"],
                                "fecha_reserva":   reserva_sel["_fecha_reserva"],
                                "pasajero_nombre": reserva_sel["_pasajero_nombre"],
                                "pasaporte":       reserva_sel["_pasaporte"],
                                "nacionalidad":    reserva_sel["_nacionalidad"],
                                "numero_vuelo":    reserva_sel["_numero_vuelo"],
                                "origen":          reserva_sel["_origen"],
                                "destino":         reserva_sel["_destino"],
                                "fecha_salida":    reserva_sel["_fecha_salida"],
                                "fecha_llegada":   reserva_sel["_fecha_llegada"],
                                "numero_asiento":  reserva_sel["_num_asiento"],
                            })
                            st.download_button(
                                label="📄  Descargar PDF",
                                data=pdf_data,
                                file_name=f"reserva_{id_sel}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        except ImportError:
                            st.warning("⚠️ Para descargar PDF instala reportlab: pip install reportlab")
                        except Exception as pdf_err:
                            st.error(f"Error al generar PDF: {pdf_err}")

        except Exception as e:
            st.error(f"Error al cargar reservas: {e}")

    with tab2:
        st.markdown('<div style="font-family:Syne,sans-serif;font-size:0.7rem;letter-spacing:0.15em;color:#5A6A8A;text-transform:uppercase;margin-bottom:1rem;">Nueva reserva</div>', unsafe_allow_html=True)

        try:
            pasajeros = sb.table("tbpasajero").select("id_pasajero, nombre, apellido, pasaporte").execute().data
            vuelos    = sb.table("tbvuelo").select("id_vuelo, numero_vuelo, origen, destino, id_avion").execute().data

            if not pasajeros:
                st.warning("No hay pasajeros registrados. Ve a la sección de Pasajeros para agregar uno.")
                return
            if not vuelos:
                st.warning("No hay vuelos registrados.")
                return

            pas_opts   = {f"{p['nombre']} {p['apellido']} ({p['pasaporte']})": p["id_pasajero"] for p in pasajeros}
            vuelo_opts = {f"{v['numero_vuelo']}: {v['origen']} → {v['destino']}": v for v in vuelos}

            pas_sel   = st.selectbox("Pasajero", list(pas_opts.keys()))
            vuelo_sel = st.selectbox("Vuelo", list(vuelo_opts.keys()))

            vuelo_data      = vuelo_opts[vuelo_sel]
            id_vuelo        = vuelo_data["id_vuelo"]
            id_pasajero_sel = pas_opts[pas_sel]

            ya_reservado = (
                sb.table("tbreserva")
                .select("id_reserva")
                .eq("id_vuelo", id_vuelo)
                .eq("id_pasajero", id_pasajero_sel)
                .execute()
                .data
            )
            if ya_reservado:
                st.warning("⚠️ Este pasajero ya tiene una reserva en este vuelo.")

            reservados     = sb.table("tbreserva").select("id_asiento").eq("id_vuelo", id_vuelo).execute().data
            ids_reservados = [r["id_asiento"] for r in reservados if r.get("id_asiento")]
            asientos_vuelo = sb.table("tbasiento").select("id_asiento, numero_asiento, id_tipo_asiento").eq("id_vuelo", id_vuelo).execute().data
            disponibles    = [a for a in asientos_vuelo if a["id_asiento"] not in ids_reservados]

            if not asientos_vuelo:
                st.warning("⚠️ Este vuelo no tiene asientos cargados todavía.")
                st.markdown(f"""
                <div style='background:#0C1020;border:1px solid #FF6B35;border-radius:8px;padding:1rem;
                            font-family:Space Mono,monospace;font-size:0.75rem;color:#FF6B35;margin-top:0.5rem;'>
                    <b>Solución:</b> Ve a Supabase → SQL Editor y ejecuta:<br><br>
                    <span style='color:#E8EDF5;'>
                    INSERT INTO tbAsiento (id_vuelo, numero_asiento, id_tipo_asiento)<br>
                    SELECT {id_vuelo}, numero_asiento, id_tipo_asiento<br>
                    FROM tbAsientoAvion<br>
                    WHERE id_tipo_avion = (SELECT id_tipo_avion FROM tbAvion WHERE id_avion = {vuelo_data.get('id_avion','?')});
                    </span>
                </div>
                """, unsafe_allow_html=True)
            elif not disponibles:
                st.warning("⚠️ No hay asientos disponibles. Todos están reservados.")
            else:
                tipos_raw = sb.table("tbtipoasiento").select("id_tipo_asiento, nombre").execute().data
                tipo_map  = {t["id_tipo_asiento"]: t["nombre"] for t in tipos_raw}

                clases_disponibles = {}
                for a in disponibles:
                    clase = tipo_map.get(a["id_tipo_asiento"], "Sin clase")
                    clases_disponibles.setdefault(clase, []).append(a)

                clase_sel    = st.selectbox("Clase", list(clases_disponibles.keys()))
                asientos_cls = clases_disponibles[clase_sel]
                asiento_opts = {a["numero_asiento"]: a["id_asiento"] for a in asientos_cls}
                asiento_sel  = st.selectbox(f"Asiento ({len(asientos_cls)} disponibles)", list(asiento_opts.keys()))

                st.markdown(f"""
                <div style='background:#0C1020;border:1px solid #1A2540;border-radius:8px;
                            padding:0.75rem 1rem;margin:0.75rem 0;
                            font-family:Space Mono,monospace;font-size:0.75rem;color:#5A6A8A;'>
                    Resumen: <span style='color:#00D4FF;'>{pas_sel.split("(")[0].strip()}</span>
                    · Vuelo <span style='color:#FF6B35;'>{vuelo_data['numero_vuelo']}</span>
                    · Asiento <span style='color:#00FF9F;'>{asiento_sel}</span> ({clase_sel})
                </div>
                """, unsafe_allow_html=True)

                if not ya_reservado:
                    if st.button("CONFIRMAR RESERVA →", use_container_width=True):
                        asiento_ocupado = (
                            sb.table("tbreserva")
                            .select("id_reserva")
                            .eq("id_vuelo", id_vuelo)
                            .eq("id_asiento", asiento_opts[asiento_sel])
                            .execute()
                            .data
                        )
                        if asiento_ocupado:
                            st.error("❌ Ese asiento ya fue reservado. Por favor selecciona otro.")
                        else:
                            sb.table("tbreserva").insert({
                                "id_pasajero": id_pasajero_sel,
                                "id_vuelo":    id_vuelo,
                                "id_asiento":  asiento_opts[asiento_sel],
                            }).execute()
                            st.session_state.mensaje_exito = f"✅ Reserva confirmada. Asiento {asiento_sel} ({clase_sel}) asignado en vuelo {vuelo_data['numero_vuelo']}."
                            st.rerun()
                else:
                    st.error("❌ No se puede confirmar: este pasajero ya tiene una reserva en este vuelo.")

        except Exception as e:
            st.error(f"Error: {e}")
