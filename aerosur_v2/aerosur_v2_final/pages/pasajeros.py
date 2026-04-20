import streamlit as st
import pandas as pd
from datetime import date
from utils.supabase_client import get_client

def render():
    sb = get_client()
    st.markdown('<div class="section-title">👥 Gestión de Pasajeros</div>', unsafe_allow_html=True)

    # Mensaje de éxito persistente
    if st.session_state.get("mensaje_exito"):
        st.success(st.session_state.mensaje_exito)
        st.session_state.mensaje_exito = ""

    tab1, tab2 = st.tabs(["📋 Listado y Edición", "➕ Nuevo pasajero"])

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

            st.markdown("---")
            st.subheader("🛠️ Acciones sobre pasajero")
            
            # Crear un diccionario para identificar al pasajero por ID fácilmente
            dict_pasajeros = {r["id_pasajero"]: r for r in rows}
            ids = list(dict_pasajeros.keys())
            
            col_sel, col_del = st.columns([2, 1])
            with col_sel:
                id_sel = st.selectbox("Seleccionar pasajero para Editar o Eliminar", ids)
            
            with col_del:
                st.write("") # Espaciador
                if st.button("🗑️ Eliminar Pasajero", use_container_width=True):
                    sb.table("tbpasajero").delete().eq("id_pasajero", id_sel).execute()
                    st.session_state.mensaje_exito = "✅ Pasajero eliminado correctamente."
                    st.rerun()

            # --- SECCIÓN DE EDICIÓN ---
            if id_sel:
                pasajero_actual = dict_pasajeros[id_sel]
                st.info(f"Editando a: **{pasajero_actual['nombre']} {pasajero_actual['apellido']}**")
                
                with st.form("form_edicion"):
                    c1, c2 = st.columns(2)
                    with c1:
                        new_nombre = st.text_input("Nombre", value=pasajero_actual["nombre"])
                        new_pasaporte = st.text_input("Pasaporte", value=pasajero_actual["pasaporte"], max_chars=9)
                        # Conversión de fecha de string a objeto date de Python
                        fecha_val = datetime.strptime(pasajero_actual["fecha_nacimiento"], '%Y-%m-%d').date()
                        new_nacimiento = st.date_input("Fecha de nacimiento", value=fecha_val)
                    with c2:
                        new_apellido = st.text_input("Apellido", value=pasajero_actual["apellido"])
                        new_nacionalidad = st.text_input("Nacionalidad", value=pasajero_actual["nacionalidad"])
                    
                    if st.form_submit_button("💾 GUARDAR CAMBIOS"):
                        if len(new_pasaporte) != 9:
                            st.error("El pasaporte debe tener 9 caracteres.")
                        else:
                            update_data = {
                                "nombre": new_nombre,
                                "apellido": new_apellido,
                                "pasaporte": new_pasaporte,
                                "nacionalidad": new_nacionalidad,
                                "fecha_nacimiento": str(new_nacimiento)
                            }
                            sb.table("tbpasajero").update(update_data).eq("id_pasajero", id_sel).execute()
                            st.session_state.mensaje_exito = "✅ Datos actualizados correctamente."
                            st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")
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
            elif largo ==9:
                st.success("✅ Longitud de pasaporte correcta (9/9).")
            else:
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
                            "nombre": nombre, "apellido": apellido,
                            "pasaporte": pasaporte, "nacionalidad": nacionalidad,
                            "fecha_nacimiento": str(nacimiento)
                        }).execute()
                        st.session_state.mensaje_exito = f"✅ Pasajero {nombre} {apellido} registrado exitosamente."
                        st.rerun()
                except Exception as e:
                    st.error(str(e))
