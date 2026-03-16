import streamlit as st
from utils.auth import check_login

def render():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)

        # Logo / Header
        st.markdown("""
        <div style='text-align:center; margin-bottom:2.5rem;'>
            <div style='font-size:3rem; margin-bottom:0.5rem;'>✈</div>
            <div style='font-family:Space Mono,monospace; font-size:1.6rem; font-weight:700;
                        color:#00D4FF; letter-spacing:0.15em;'>AEROSUR</div>
            <div style='font-family:Syne,sans-serif; font-size:0.75rem; color:#5A6A8A;
                        letter-spacing:0.2em; text-transform:uppercase; margin-top:0.25rem;'>
                Sistema de Gestión de Vuelos
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Card de login — sin el div HTML que causaba el recuadro vacío
        st.markdown('<div style="font-family:Syne,sans-serif;font-size:0.7rem;letter-spacing:0.15em;color:#5A6A8A;text-transform:uppercase;margin-bottom:0.5rem;">CORREO</div>', unsafe_allow_html=True)
        correo = st.text_input("Correo", placeholder="usuario@aerosur.com", label_visibility="collapsed")

        st.markdown('<div style="font-family:Syne,sans-serif;font-size:0.7rem;letter-spacing:0.15em;color:#5A6A8A;text-transform:uppercase;margin-top:0.75rem;margin-bottom:0.5rem;">CONTRASEÑA</div>', unsafe_allow_html=True)
        contrasena = st.text_input("Contraseña", type="password", placeholder="••••••••", label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("INGRESAR →", use_container_width=True):
            if not correo or not contrasena:
                st.error("Ingresa correo y contraseña.")
            else:
                usuario = check_login(correo, contrasena)
                if usuario:
                    st.session_state.logged_in = True
                    st.session_state.usuario = usuario
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas o usuario inactivo.")
