import streamlit as st
import pandas as pd
from datetime import date, datetime #
from utils.supabase_client import get_client

def render():
    sb = get_client()
    st.markdown('<div class="section-title">👥 Gestión de Pasajeros</div>', unsafe_allow_html=True)

    # --- 1. GESTIÓN DE MENSAJES ---
    if st.session_state.get("mensaje_exito"):
        st.success(st.session_state.mensaje_exito)
        st.session_state.mensaje_exito = ""

    # --- 2. TABS PRINCIPALES ---
    tab1, tab2 = st.tabs(["📋 Listado y Edición", "➕ Nuevo pasajero"])

    with tab1:
        busqueda = st.text_input("🔍 Buscar por nombre, apellido o pasaporte", placeholder="Ingresa texto...")
        
        try:
            # Obtener datos de Supabase
            res = sb.table("tbpasajero").select("*").order("apellido").execute()
            rows = res.data
            
            if busqueda:
                b = busqueda.lower()
                rows = [r for r in rows if b in r["nombre"].lower() 
                        or b in r["apellido"].lower() 
                        or b in r.get("pasaporte","").lower()]
            
            if not rows:
                st.info("No se encontraron pasajeros.")
            else:
                # Mostrar Tabla de pasajeros
                df = pd.DataFrame(rows)[["id_pasajero","nombre","apellido","pasaporte","nacionalidad","fecha_nacimiento"]]
                df.columns = ["ID","Nombre","Apellido","Pasaporte","Nacionalidad","Nacimiento"]
                st.dataframe(df, use_container_width=True, hide_index=True)

                st.divider()

                # --- SECCIÓN DE ACCIONES (EDICIÓN / ELIMINACIÓN) ---
                st.subheader("🛠️ Acciones de Pasajero")
                
                # Diccionario para acceder rápido a los datos del pasajero seleccionado
                dict_pasajeros = {r["id_pasajero"]: r for r in rows}
                id_sel = st.selectbox("Seleccione el ID del pasajero para gestionar", list(dict_pasajeros.keys()))

                if id_sel:
                    p = dict_pasajeros[id_sel]
                    
                    # Formulario de Edición
                    # Usamos st.form para agrupar los inputs y un solo botón de envío
                    with st.form(key="form_edicion_pasajero"):
                        st.markdown(f"**Editando datos de:** {p['nombre']} {p['apellido']}")
                        col_ed1, col_ed2 = st.columns(2)
                        
                        with col_ed1:
                            enombre = st.text_input("Nombre", value=p["nombre"])
                            epasaporte = st.text_input("Pasaporte", value=p["pasaporte"], max_chars=9)
                            
                            # Convertir fecha de texto (ISO) a objeto date de Python
                            try:
                                fecha_actual = datetime.strptime(p["fecha_nacimiento"], '%Y-%m-%d').date()
                            except:
                                fecha_actual = date(1990, 1, 1)
                            
                            enacimiento = st.date_input("Fecha de nacimiento", value=fecha_actual)
                        
                        with col_ed2:
                            eapellido = st.text_input("Apellido", value=p["apellido"])
                            enacionalidad = st.text_input("Nacionalidad", value=p["nacionalidad"])

                        # Botón obligatorio dentro de st.form
                        btn_update = st.form_submit_button("💾 GUARDAR CAMBIOS")

                        if btn_update:
                            if len(epasaporte) != 9:
                                st.error("❌ El pasaporte debe tener 9 caracteres.")
                            elif not enombre or not eapellido:
                                st.error("❌ El nombre y apellido no pueden estar vacíos.")
                            else:
                                update_data = {
                                    "nombre": enombre,
                                    "apellido": eapellido,
                                    "pasaporte": epasaporte,
                                    "nacionalidad": enacionalidad,
                                    "fecha_nacimiento": str(enacimiento)
                                }
                                sb.table("tbpasajero").update(update_data).eq("id_pasajero", id_sel).execute()
                                st.session_state.mensaje_exito = "✅ Pasajero actualizado correctamente."
                                st.rerun()

                    # Botón de eliminación (FUERA del st.form)
                    if st.button("🗑️ ELIMINAR PASAJERO SELECCIONADO", use_container_width=True):
                        sb.table("tbpasajero").delete().eq("id_pasajero", id_sel).execute()
                        st.session_state.mensaje_exito = "✅ Pasajero eliminado con éxito."
                        st.rerun()

        except Exception as e:
            st.error(f"Error en la base de datos: {e}")

    with tab2:
        st.markdown('<div style="font-family:Syne,sans-serif;font-size:0.7rem;letter-spacing:0.15em;color:#5A6A8A;text-transform:uppercase;margin-bottom:1rem;">Registrar nuevo pasajero</div>', unsafe_allow_html=True)

        with st.form("form_nuevo_pasajero"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre")
                pasaporte = st.text_input("Número de pasaporte (9 caracteres)", max_chars=9).strip()
                nacimiento = st.date_input("Fecha de nacimiento",
                                         value=date(1990, 1, 1),
                                         min_value=date(1900, 1, 1),
                                         max_value=date.today())
            with col2:
                apellido = st.text_input("Apellido")
                nacionalidad = st.text_input("Nacionalidad")

            btn_registrar = st.form_submit_button("REGISTRAR PASAJERO →")

            if btn_registrar:
                if not all([nombre, apellido, pasaporte, nacionalidad]):
                    st.error("❌ Completa todos los campos.")
                elif len(pasaporte) != 9:
                    st.error(f"❌ El pasaporte debe tener 9 caracteres. (Tienes {len(pasaporte)})")
                else:
                    try:
                        # Verificar si existe
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
                            st.session_state.mensaje_exito = f"✅ Pasajero {nombre} registrado exitosamente."
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error al registrar: {e}")
