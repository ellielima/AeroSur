import streamlit as st
from utils.supabase_client import get_client

def render():
    sb = get_client()
    st.markdown('<div class="section-title">🛩️ Gestión de Aviones</div>', unsafe_allow_html=True)

    if st.session_state.get("mensaje_exito"):
        st.success(st.session_state.mensaje_exito)
        st.session_state.mensaje_exito = ""

    tab1, tab2, tab3 = st.tabs(["🛩️  Flota", "➕  Nuevo avión", "💺  Configuración de asientos"])

    with tab1:
        try:
            rows = sb.table("tbavion").select("*, tbtipoavion(nombre, descripcion)").execute().data
            if not rows:
                st.info("No hay aviones registrados.")
                return
            for a in rows:
                tipo  = a.get("tbtipoavion") or {}
                color = "#00FF9F" if a["estado"] == "Activo" else "#FF3B5C"
                st.markdown(f"""
                <div style='background:#0C1020;border:1px solid #1A2540;border-radius:8px;
                            padding:1.25rem 1.5rem;margin-bottom:0.75rem;
                            display:flex;justify-content:space-between;align-items:center;'>
                    <div>
                        <div style='font-family:Space Mono,monospace;font-size:1rem;color:#E8EDF5;font-weight:700;'>{a['matricula']}</div>
                        <div style='font-family:Syne,sans-serif;font-size:0.8rem;color:#5A6A8A;margin-top:0.2rem;'>
                            {tipo.get('nombre','—')} · {tipo.get('descripcion','—')}
                        </div>
                    </div>
                    <div style='font-family:Space Mono,monospace;font-size:0.8rem;color:{color};'>● {a['estado']}</div>
                </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.error(str(e))

    with tab2:
        try:
            tipos     = sb.table("tbtipoavion").select("*").execute().data
            tipo_opts = {t["nombre"]: t["id_tipo_avion"] for t in tipos}
        except:
            tipo_opts = {}

        matricula = st.text_input("Matrícula del avión", placeholder="TG-A320-02")
        tipo_sel  = st.selectbox("Tipo de avión", list(tipo_opts.keys()))
        estado    = st.selectbox("Estado", ["Activo", "Inactivo", "En mantenimiento"])

        if st.button("REGISTRAR AVIÓN →", use_container_width=True):
            if not matricula:
                st.error("❌ Ingresa la matrícula.")
            else:
                try:
                    existe = sb.table("tbavion").select("id_avion").eq("matricula", matricula).execute().data
                    if existe:
                        st.error(f"❌ Ya existe un avión con la matrícula {matricula}.")
                    else:
                        sb.table("tbavion").insert({
                            "matricula": matricula,
                            "id_tipo_avion": tipo_opts[tipo_sel],
                            "estado": estado
                        }).execute()
                        st.session_state.mensaje_exito = f"✅ Avión {matricula} registrado exitosamente."
                        st.rerun()
                except Exception as e:
                    st.error(str(e))

    with tab3:
        st.markdown('<div style="font-family:Syne,sans-serif;font-size:0.7rem;letter-spacing:0.15em;color:#5A6A8A;text-transform:uppercase;margin-bottom:1rem;">Ver distribución de asientos por tipo</div>', unsafe_allow_html=True)
        try:
            tipos      = sb.table("tbtipoavion").select("*").execute().data
            tipo_opts2 = {t["nombre"]: t["id_tipo_avion"] for t in tipos}
            tipo_sel2  = st.selectbox("Tipo de avión", list(tipo_opts2.keys()), key="tipo_asiento_sel")

            asientos = (
                sb.table("tbasientoavion")
                .select("numero_asiento, id_tipo_asiento")
                .eq("id_tipo_avion", tipo_opts2[tipo_sel2])
                .execute()
                .data
            )

            if asientos:
                tipos_asiento    = sb.table("tbtipoasiento").select("id_tipo_asiento, nombre").execute().data
                tipo_asiento_map = {t["id_tipo_asiento"]: t["nombre"] for t in tipos_asiento}

                clases = {}
                for a in asientos:
                    clase = tipo_asiento_map.get(a["id_tipo_asiento"], "Otro")
                    clases.setdefault(clase, []).append(a["numero_asiento"])

                todos      = [a["numero_asiento"] for a in asientos]
                duplicados = [n for n in todos if todos.count(n) > 1]
                if duplicados:
                    st.warning(f"⚠️ Se encontraron asientos duplicados: {list(set(duplicados))}")

                colores_clase = {"Economica":"#00D4FF","Ejecutiva":"#FF6B35","Primera Clase":"#A78BFA"}
                cols = st.columns(len(clases))
                for i, (clase, seats) in enumerate(clases.items()):
                    color = colores_clase.get(clase, "#E8EDF5")
                    with cols[i]:
                        st.markdown(f"""
                        <div style='background:#0C1020;border:1px solid #1A2540;border-radius:8px;padding:1rem;text-align:center;'>
                            <div style='font-family:Space Mono,monospace;font-size:0.7rem;color:{color};text-transform:uppercase;margin-bottom:0.5rem;'>{clase}</div>
                            <div style='font-family:Syne,sans-serif;font-size:2rem;font-weight:800;color:{color};'>{len(seats)}</div>
                            <div style='font-family:Space Mono,monospace;font-size:0.65rem;color:#5A6A8A;'>asientos</div>
                        </div>
                        """, unsafe_allow_html=True)

                total = sum(len(s) for s in clases.values())
                st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:0.75rem;color:#5A6A8A;margin-top:0.75rem;text-align:center;">Total capacidad: <span style="color:#E8EDF5">{total} asientos</span></div>', unsafe_allow_html=True)
            else:
                st.info("No hay asientos configurados para este tipo de avión.")

        except Exception as e:
            st.error(str(e))
