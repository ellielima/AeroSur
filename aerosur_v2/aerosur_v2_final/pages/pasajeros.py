import streamlit as st
import pandas as pd
from datetime import date, datetime #
from utils.supabase_client import get_client

def render():
    sb = get_client()
    st.markdown('<div class="section-title">👥 Gestión de Pasajeros</div>', unsafe_allow_html=True)

    # Mensaje de éxito persistente
    if st.session_state.get("mensaje_exito"):
        st.success(st.session_state.mensaje_exito)
        st.session_state.mensaje_exito = ""

    tab1, tab2 = st.tabs(["📋 Listado", "➕ Nuevo pasajero"])

    # =========================
    # 📋 TAB 1: LISTADO
    # =========================
    with tab1:
        busqueda = st.text_input("🔍 Buscar por nombre, apellido o pasaporte", placeholder="Ingresa texto...")
        try:
            rows = sb.table("tbpasajero").select("*").order("apellido").execute().data

            if busqueda:
                b = busqueda.lower()
                rows = [r for r in rows if b in r["nombre"].lower()
                        or b in r["apellido"].lower()
                        or b in r.get("pasaporte","").lower()]

            if not rows:
                st.info("No se encontraron pasajeros.")
                return

            df = pd.DataFrame(rows)[["id_pasajero","nombre","apellido","pasaporte","nacionalidad","fecha_nacimiento"]]
            df.columns = ["ID","Nombre","Apellido","Pasaporte","Nacionalidad","Nacimiento"]
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)

            with col1:
                ids = [r["id_pasajero"] for r in rows]
                id_sel = st.selectbox("Seleccionar pasajero (ID)", ids)

            with col2:
                st.markdown("<br>", unsafe_allow_html=True)

                if st.button("🗑️ Eliminar pasajero seleccionado"):
                    sb.table("tbpasajero").delete().eq("id_pasajero", id_sel).execute()
                    st.session_state.mensaje_exito = "✅ Pasajero eliminado correctamente."
                    st.rerun()

                if st.button("✏️ Editar pasajero"):
                    st.session_state["editar_id"] = id_sel

            # =========================
            # ✏️ FORMULARIO DE EDICIÓN
            # =========================
            if "editar_id" in st.session_state and st.session_state["editar_id"]:
                pasajero = next((r for r in rows if r["id_pasajero"] == st.session_state["editar_id"]), None)

                if pasajero:
                    st.markdown("### ✏️ Editar pasajero")

                    col1, col2 = st.columns(2)

                    with col1:
                        nombre_edit = st.text_input("Nombre", value=pasajero["nombre"], key="edit_nombre")
                        pasaporte_edit = st.text_input("Pasaporte", value=pasajero["pasaporte"], max_chars=9, key="edit_pasaporte")
                        nacimiento_edit = st.date_input(
                            "Fecha de nacimiento",
                            value=pd.to_datetime(pasajero["fecha_nacimiento"]),
                            key="edit_fecha"
                        )

                    with col2:
                        apellido_edit = st.text_input("Apellido", value=pasajero["apellido"], key="edit_apellido")
                        nacionalidad_edit = st.text_input("Nacionalidad", value=pasajero["nacionalidad"], key="edit_nacionalidad")

                    if st.button("💾 Guardar cambios"):
                        if not all([nombre_edit, apellido_edit, pasaporte_edit, nacionalidad_edit]):
                            st.error("❌ Completa todos los campos.")
                        elif len(pasaporte_edit) != 9:
                            st.error("❌ El pasaporte debe tener exactamente 9 caracteres.")
                        else:
                            try:
                                # Validar duplicados de pasaporte
                                existe = sb.table("tbpasajero") \
                                    .select("id_pasajero") \
                                    .eq("pasaporte", pasaporte_edit) \
                                    .neq("id_pasajero", st.session_state["editar_id"]) \
                                    .execute().data

                                if existe:
                                    st.error("❌ Ya existe otro pasajero con ese pasaporte.")
                                else:
                                    sb.table("tbpasajero").update({
                                        "nombre": nombre_edit,
                                        "apellido": apellido_edit,
                                        "pasaporte": pasaporte_edit,
                                        "nacionalidad": nacionalidad_edit,
                                        "fecha_nacimiento": str(nacimiento_edit)
                                    }).eq("id_pasajero", st.session_state["editar_id"]).execute()

                                    st.session_state.mensaje_exito = "✅ Pasajero actualizado correctamente."
                                    st.session_state["editar_id"] = None
                                    st.rerun()

                            except Exception as e:
                                st.error(str(e))

        except Exception as e:
            st.error(str(e))

    # =========================
    # ➕ TAB 2: NUEVO PASAJERO
    # =========================
    with tab2:
        st.markdown('<div style="font-family:Syne,sans-serif;font-size:0.7rem;letter-spacing:0.15em;color:#5A6A8A;text-transform:uppercase;margin-bottom:1rem;">Registrar nuevo pasajero</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            nombre    = st.text_input("Nombre")
            pasaporte = st.text_input("Número de pasaporte (exactamente 9 caracteres)", max_chars=9).strip()
            nacimiento = st.date_input("Fecha de nacimiento",
                value=date(1990, 1, 1),
                min_value=date(1900, 1, 1),
                max_value=date.today())

        with col2:
            apellido     = st.text_input("Apellido")
            nacionalidad = st.text_input("Nacionalidad")

        largo = len(pasaporte)
        if largo > 0:
            if largo < 9:
                st.warning(f"⚠️ El pasaporte debe tener exactamente 9 caracteres. Llevas {largo}/9.")
            elif largo == 9:
                st.success("✅ Longitud de pasaporte correcta (9/9).")

        if st.button("REGISTRAR PASAJERO →", use_container_width=True):
            if not all([nombre, apellido, pasaporte, nacionalidad]):
                st.error("❌ Completa todos los campos.")
            elif len(pasaporte) != 9:
                st.error(f"❌ El pasaporte debe tener exactamente 9 caracteres. Actualmente tiene {len(pasaporte)}.")
            else:
                try:
                    existe = sb.table("tbpasajero").select("id_pasajero").eq("pasaporte", pasaporte).execute().data
                    if existe:
                        st.error("❌ Ya existe un pasajero con ese número de pasaporte.")
                    else:
                        sb.table("tbpasajero").insert({
                            "nombre": nombre,
                            "apellido": apellido,
                            "pasaporte": pasaporte,
                            "nacionalidad": nacionalidad,
                            "fecha_nacimiento": str(nacimiento)
                        }).execute()

                        st.session_state.mensaje_exito = f"✅ Pasajero {nombre} {apellido} registrado exitosamente."
                        st.rerun()

                except Exception as e:
                    st.error(str(e))
