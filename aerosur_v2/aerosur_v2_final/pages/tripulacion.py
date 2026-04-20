import streamlit as st
from utils.supabase_client import get_client

def render():
    sb = get_client()
    st.markdown('<div class="section-title">👨‍✈️ Gestión de Tripulación</div>', unsafe_allow_html=True)

    if st.session_state.get("mensaje_exito"):
        st.success(st.session_state.mensaje_exito)
        st.session_state.mensaje_exito = ""

    tab1, tab2, tab3 = st.tabs(["📋  Tripulantes", "➕  Nuevo tripulante", "✈️  Asignar a vuelo"])

    with tab1:
        try:
            rows = sb.table("tbtripulacion").select("*").order("rol").execute().data
            if not rows:
                st.info("No hay tripulantes registrados.")
                return
            roles = list(set(r["rol"] for r in rows))
            for rol in sorted(roles):
                st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:0.7rem;color:#FF6B35;margin-top:1rem;margin-bottom:0.5rem;">{rol.upper()}</div>', unsafe_allow_html=True)
                miembros = [r for r in rows if r["rol"] == rol]
                cols = st.columns(min(len(miembros), 4))
                for i, m in enumerate(miembros):
                    with cols[i % 4]:
                        pasaporte_txt    = m.get("Pasaporte") or m.get("pasaporte") or "—"
                        nacionalidad_txt = m.get("Nacionalidad") or m.get("nacionalidad") or "—"
                        st.markdown(f"""
                        <div style='background:#0C1020;border:1px solid #1A2540;border-radius:8px;
                                    padding:1rem;text-align:center;margin-bottom:0.5rem;'>
                            <div style='font-size:1.5rem;'>{"🧑‍✈️" if "Piloto" in rol or "Copiloto" in rol else "🧑‍💼"}</div>
                            <div style='font-family:Syne,sans-serif;font-size:0.9rem;color:#E8EDF5;margin-top:0.25rem;font-weight:600;'>
                                {m["nombre"]} {m["apellido"]}
                            </div>
                            <div style='font-family:Space Mono,monospace;font-size:0.65rem;color:#5A6A8A;margin-top:0.25rem;'>
                                🪪 {pasaporte_txt} · {nacionalidad_txt}
                            </div>
                            <div style='font-family:Space Mono,monospace;font-size:0.65rem;color:#5A6A8A;'>ID: {m["id_tripulante"]}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("🗑", key=f"del_trip_{m['id_tripulante']}"):
                            sb.table("tbtripulacion").delete().eq("id_tripulante", m["id_tripulante"]).execute()
                            st.session_state.mensaje_exito = "✅ Tripulante eliminado correctamente."
                            st.rerun()
        except Exception as e:
            st.error(str(e))

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            nombre     = st.text_input("Nombre")
            pasaporte  = st.text_input("Pasaporte (exactamente 9 caracteres)", max_chars=9)
        with col2:
            apellido     = st.text_input("Apellido")
            nacionalidad = st.text_input("Nacionalidad")

        # Indicador longitud pasaporte
        largo = len(pasaporte)
        if largo > 0:
            if largo < 9:
                st.warning(f"⚠️ El pasaporte debe tener exactamente 9 caracteres. Llevas {largo}/9.")
            else:
                st.success("✅ Longitud de pasaporte correcta (9/9).")

        rol_opts = ["Piloto","Copiloto","Azafata","Azafato","Ingeniero de vuelo","Jefe de cabina"]
        rol = st.selectbox("Rol", rol_opts)

        if st.button("REGISTRAR TRIPULANTE →", use_container_width=True):
            if not all([nombre, apellido, rol, pasaporte, nacionalidad]):
                st.error("❌ Completa todos los campos.")
            elif len(pasaporte) != 15:
                st.error(f"❌ El pasaporte debe tener exactamente 9 caracteres. Actualmente tiene {len(pasaporte)}.")
            else:
                try:
                    existe = (
                        sb.table("tbtripulacion")
                        .select("id_tripulante")
                        .eq("nombre", nombre)
                        .eq("apellido", apellido)
                        .execute()
                        .data
                    )
                    if existe:
                        st.error(f"❌ Ya existe un tripulante con el nombre {nombre} {apellido}.")
                    else:
                        sb.table("tbtripulacion").insert({
                            "nombre":       nombre,
                            "apellido":     apellido,
                            "rol":          rol,
                            "Pasaporte":    pasaporte,
                            "Nacionalidad": nacionalidad
                        }).execute()
                        st.session_state.mensaje_exito = f"✅ {nombre} {apellido} registrado como {rol} exitosamente."
                        st.rerun()
                except Exception as e:
                    st.error(str(e))

    with tab3:
        st.markdown('<div style="font-family:Syne,sans-serif;font-size:0.7rem;letter-spacing:0.15em;color:#5A6A8A;text-transform:uppercase;margin-bottom:1rem;">Asignar tripulante a vuelo</div>', unsafe_allow_html=True)
        try:
            vuelos      = sb.table("tbvuelo").select("id_vuelo, numero_vuelo, origen, destino").execute().data
            tripulantes = sb.table("tbtripulacion").select("*").execute().data
            vuelo_opts  = {f"{v['numero_vuelo']}: {v['origen']} → {v['destino']}": v["id_vuelo"] for v in vuelos}
            trip_opts   = {f"{t['nombre']} {t['apellido']} ({t['rol']})": t["id_tripulante"] for t in tripulantes}

            vuelo_sel = st.selectbox("Vuelo", list(vuelo_opts.keys()))
            trip_sel  = st.selectbox("Tripulante", list(trip_opts.keys()))

            if st.button("ASIGNAR →", use_container_width=True):
                id_vuelo = vuelo_opts[vuelo_sel]
                id_trip  = trip_opts[trip_sel]
                existe = (
                    sb.table("tbvuelotripulacion")
                    .select("id")
                    .eq("id_vuelo", id_vuelo)
                    .eq("id_tripulante", id_trip)
                    .execute()
                    .data
                )
                if existe:
                    st.warning("⚠️ Este tripulante ya está asignado a ese vuelo.")
                else:
                    sb.table("tbvuelotripulacion").insert({
                        "id_vuelo": id_vuelo, "id_tripulante": id_trip
                    }).execute()
                    st.session_state.mensaje_exito = "✅ Tripulante asignado al vuelo exitosamente."
                    st.rerun()

            # Tripulación actual del vuelo seleccionado
            id_v_actual = vuelo_opts[vuelo_sel]
            actual = (
                sb.table("tbvuelotripulacion")
                .select("tbtripulacion(nombre, apellido, rol)")
                .eq("id_vuelo", id_v_actual)
                .execute()
                .data
            )
            if actual:
                st.markdown('<div style="font-family:Space Mono,monospace;font-size:0.7rem;color:#5A6A8A;margin-top:1rem;margin-bottom:0.5rem;">TRIPULACIÓN ACTUAL DEL VUELO</div>', unsafe_allow_html=True)
                for t in actual:
                    tr = t.get("tbtripulacion") or {}
                    st.markdown(f"↳ **{tr.get('nombre','')} {tr.get('apellido','')}** · *{tr.get('rol','')}*")

        except Exception as e:
            st.error(str(e))
