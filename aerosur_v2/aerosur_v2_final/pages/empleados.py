import streamlit as st
from utils.supabase_client import get_client

def render():
    sb = get_client()
    st.markdown('<div class="section-title">👔 Gestión de Empleados</div>', unsafe_allow_html=True)

    if st.session_state.get("mensaje_exito"):
        st.success(st.session_state.mensaje_exito)
        st.session_state.mensaje_exito = ""

    tab1, tab2, tab3 = st.tabs(["📋  Empleados", "➕  Nuevo empleado", "🔐  Usuarios del sistema"])

    with tab1:
        try:
            rows = sb.table("tbempleado").select("*").order("apellido").execute().data
            if not rows:
                st.info("No hay empleados registrados.")
                return
            for e in rows:
                color = "#00FF9F" if e["estado"] == "Activo" else "#FF3B5C"
                st.markdown(f"""
                <div style='background:#0C1020;border:1px solid #1A2540;border-radius:8px;
                            padding:1rem 1.5rem;margin-bottom:0.5rem;
                            display:flex;justify-content:space-between;align-items:center;'>
                    <div>
                        <div style='font-family:Syne,sans-serif;font-size:0.95rem;color:#E8EDF5;font-weight:600;'>
                            {e['nombre']} {e['apellido']}
                        </div>
                        <div style='font-family:Space Mono,monospace;font-size:0.7rem;color:#5A6A8A;'>
                            {e['puesto']} · {e['correo']} · {e.get('telefono','—')}
                        </div>
                    </div>
                    <div style='font-family:Space Mono,monospace;font-size:0.75rem;color:{color};'>● {e['estado']}</div>
                </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.error(str(e))

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            nombre   = st.text_input("Nombre")
            puesto   = st.text_input("Puesto")
            telefono = st.text_input("Teléfono")
        with col2:
            apellido = st.text_input("Apellido")
            correo   = st.text_input("Correo laboral")
            estado   = st.selectbox("Estado", ["Activo", "Inactivo"])

        if st.button("REGISTRAR EMPLEADO →", use_container_width=True):
            if not all([nombre, apellido, puesto, correo]):
                st.error("❌ Completa los campos obligatorios.")
            else:
                try:
                    existe = sb.table("tbempleado").select("id_empleado").eq("correo", correo).execute().data
                    if existe:
                        st.error(f"❌ Ya existe un empleado con el correo {correo}.")
                    else:
                        sb.table("tbempleado").insert({
                            "nombre": nombre, "apellido": apellido,
                            "puesto": puesto,  "correo": correo,
                            "telefono": telefono, "estado": estado
                        }).execute()
                        st.session_state.mensaje_exito = f"✅ Empleado {nombre} {apellido} registrado exitosamente."
                        st.rerun()
                except Exception as e:
                    st.error(str(e))

    with tab3:
        st.markdown('<div style="font-family:Syne,sans-serif;font-size:0.7rem;letter-spacing:0.15em;color:#5A6A8A;text-transform:uppercase;margin-bottom:1rem;">Usuarios con acceso al sistema</div>', unsafe_allow_html=True)
        try:
            usuarios = (
                sb.table("tbusuario")
                .select("id_usuario, correo_login, rol, estado, fecha_creacion, tbempleado(nombre, apellido)")
                .execute()
                .data
            )
            for u in usuarios:
                emp       = u.get("tbempleado") or {}
                color     = "#00FF9F" if u["estado"] == "Activo" else "#FF3B5C"
                rol_color = {"Administrador":"#A78BFA","Operador":"#00D4FF","Supervisor":"#FF6B35"}.get(u["rol"],"#E8EDF5")
                st.markdown(f"""
                <div style='background:#0C1020;border:1px solid #1A2540;border-radius:8px;
                            padding:1rem 1.5rem;margin-bottom:0.5rem;
                            display:flex;justify-content:space-between;align-items:center;'>
                    <div>
                        <div style='font-family:Space Mono,monospace;font-size:0.85rem;color:#E8EDF5;'>{u['correo_login']}</div>
                        <div style='font-family:Syne,sans-serif;font-size:0.75rem;color:#5A6A8A;'>
                            {emp.get('nombre','')} {emp.get('apellido','')}
                        </div>
                    </div>
                    <div style='text-align:right;'>
                        <div style='font-family:Space Mono,monospace;font-size:0.75rem;color:{rol_color};'>{u['rol']}</div>
                        <div style='font-family:Space Mono,monospace;font-size:0.7rem;color:{color};'>● {u['estado']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div style="font-family:Syne,sans-serif;font-size:0.7rem;letter-spacing:0.15em;color:#5A6A8A;text-transform:uppercase;margin-bottom:0.5rem;">Crear nuevo usuario</div>', unsafe_allow_html=True)

            empleados = sb.table("tbempleado").select("id_empleado, nombre, apellido").eq("estado","Activo").execute().data
            emp_opts  = {f"{e['nombre']} {e['apellido']}": e["id_empleado"] for e in empleados}

            c1, c2 = st.columns(2)
            with c1:
                emp_sel    = st.selectbox("Empleado", list(emp_opts.keys()))
                correo_usr = st.text_input("Correo de acceso")
            with c2:
                rol_usr  = st.selectbox("Rol del sistema", ["Administrador","Operador","Supervisor"])
                pass_usr = st.text_input("Contraseña", type="password")

            if st.button("CREAR USUARIO →", use_container_width=True):
                if not all([correo_usr, pass_usr]):
                    st.error("❌ Ingresa correo y contraseña.")
                else:
                    existe_usr = sb.table("tbusuario").select("id_usuario").eq("correo_login", correo_usr).execute().data
                    if existe_usr:
                        st.error(f"❌ Ya existe un usuario con el correo {correo_usr}.")
                    else:
                        sb.table("tbusuario").insert({
                            "id_empleado":  emp_opts[emp_sel],
                            "correo_login": correo_usr,
                            "contrasena":   pass_usr,
                            "rol":          rol_usr,
                            "estado":       "Activo"
                        }).execute()
                        st.session_state.mensaje_exito = "✅ Usuario creado exitosamente. Ya puede iniciar sesión."
                        st.rerun()

        except Exception as e:
            st.error(str(e))
