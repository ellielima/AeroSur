import streamlit as st
from utils.supabase_client import get_client

def render():
    sb = get_client()
    st.markdown('<div class="section-title">👨‍✈️ Gestión de Tripulación</div>', unsafe_allow_html=True)

    if st.session_state.get("mensaje_exito"):
        st.success(st.session_state.mensaje_exito)
        st.session_state.mensaje_exito = ""

    tab1, tab2, tab3 = st.tabs(["📋  Tripulantes", "➕  Nuevo tripulante", "✈️  Asignar a vuelo"])

    # =========================
    # 📋 TAB 1: LISTADO + EDITAR
    # =========================
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

                        colA, colB = st.columns(2)

                        # 🗑 ELIMINAR
                        with colA:
                            if st.button("🗑", key=f"del_trip_{m['id_tripulante']}"):
                                sb.table("tbvuelotripulacion").delete().eq("id_tripulante", m["id_tripulante"]).execute()
                                sb.table("tbtripulacion").delete().eq("id_tripulante", m["id_tripulante"]).execute()
                                st.session_state.mensaje_exito = "✅ Tripulante eliminado correctamente."
                                st.rerun()

                        # ✏️ EDITAR
                        with colB:
                            if st.button("✏️", key=f"edit_trip_{m['id_tripulante']}"):
                                st.session_state["editar_trip_id"] = m["id_tripulante"]

            # =========================
            # ✏️ FORMULARIO DE EDICIÓN
            # =========================
            if "editar_trip_id" in st.session_state and st.session_state["editar_trip_id"]:
                trip = next((r for r in rows if r["id_tripulante"] == st.session_state["editar_trip_id"]), None)

                if trip:
                    st.markdown("### ✏️ Editar tripulante")

                    col1, col2 = st.columns(2)

                    with col1:
                        nombre_edit = st.text_input("Nombre", value=trip["nombre"], key="edit_nombre_trip")
                        pasaporte_edit = st.text_input(
                            "Pasaporte",
                            value=trip.get("Pasaporte") or trip.get("pasaporte"),
                            max_chars=9,
                            key="edit_pasaporte_trip"
                        )

                    with col2:
                        apellido_edit = st.text_input("Apellido", value=trip["apellido"], key="edit_apellido_trip")
                        nacionalidad_edit = st.text_input(
                            "Nacionalidad",
                            value=trip.get("Nacionalidad") or trip.get("nacionalidad"),
                            key="edit_nacionalidad_trip"
                        )

                    rol_opts = ["Piloto","Copiloto","Azafata","Azafato","Ingeniero de vuelo","Jefe de cabina"]
                    rol_edit = st.selectbox("Rol", rol_opts, index=rol_opts.index(trip["rol"]), key="edit_rol_trip")

                    if st.button("💾 Guardar cambios"):
                        if not all([nombre_edit, apellido_edit, rol_edit, pasaporte_edit, nacionalidad_edit]):
                            st.error("❌ Completa todos los campos.")
                        elif len(pasaporte_edit) != 9:
                            st.error("❌ El pasaporte debe tener exactamente 9 caracteres.")
                        else:
                            try:
                                sb.table("tbtripulacion").update({
                                    "nombre": nombre_edit,
                                    "apellido": apellido_edit,
                                    "rol": rol_edit,
                                    "Pasaporte": pasaporte_edit,
                                    "Nacionalidad": nacionalidad_edit
                                }).eq("id_tripulante", st.session_state["editar_trip_id"]).execute()

                                st.session_state.mensaje_exito = "✅ Tripulante actualizado correctamente."
                                st.session_state["editar_trip_id"] = None
                                st.rerun()

                            except Exception as e:
                                st.error(str(e))

        except Exception as e:
            st.error(str(e))

    # =========================
    # ➕ TAB 2: NUEVO TRIPULANTE
    # =========================
    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            nombre     = st.text_input("Nombre")
            pasaporte  = st.text_input("Pasaporte (exactamente 9 caracteres)", max_chars=9).strip()

        with col2:
            apellido     = st.text_input("Apellido")
            nacionalidad = st.text_input("Nacionalidad")

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
            elif len(pasaporte) != 9:
                st.error(f"❌ El pasaporte debe tener exactamente 9 caracteres. Actualmente tiene {len(pasaporte)}.")
            else:
                try:
                    existe = sb.table("tbtripulacion")\
                        .select("id_tripulante")\
                        .eq("nombre", nombre)\
                        .eq("apellido", apellido)\
                        .execute().data

                    if existe:
                        st.error(f"❌ Ya existe un tripulante con el nombre {nombre} {apellido}.")
                    else:
                        sb.table("tbtripulacion").insert({
                            "nombre": nombre,
                            "apellido": apellido,
                            "rol": rol,
                            "Pasaporte": pasaporte,
                            "Nacionalidad": nacionalidad
                        }).execute()

                        st.session_state.mensaje_exito = f"✅ {nombre} {apellido} registrado como {rol} exitosamente."
                        st.rerun()

                except Exception as e:
                    st.error(str(e))

    # =========================
    # ✈️ TAB 3 (SIN CAMBIOS)
    # =========================
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

                existe = sb.table("tbvuelotripulacion")\
                    .select("id")\
                    .eq("id_vuelo", id_vuelo)\
                    .eq("id_tripulante", id_trip)\
                    .execute().data

                if existe:
                    st.warning("⚠️ Este tripulante ya está asignado a ese vuelo.")
                else:
                    sb.table("tbvuelotripulacion").insert({
                        "id_vuelo": id_vuelo,
                        "id_tripulante": id_trip
                    }).execute()

                    st.session_state.mensaje_exito = "✅ Tripulante asignado al vuelo exitosamente."
                    st.rerun()

        except Exception as e:
            st.error(str(e))
