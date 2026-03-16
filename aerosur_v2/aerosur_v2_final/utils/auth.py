import streamlit as st
from utils.supabase_client import get_client
from datetime import datetime

def check_login(correo: str, contrasena: str) -> dict | None:
    """Verifica credenciales y registra log de acceso."""
    sb = get_client()
    try:
        result = (
            sb.table("tbusuario")
            .select("*, tbempleado(nombre, apellido)")
            .eq("correo_login", correo)
            .eq("contrasena", contrasena)
            .eq("estado", "Activo")
            .single()
            .execute()
        )
        usuario = result.data
        if usuario:
            _log_acceso(usuario["id_usuario"], "Exitoso")
        return usuario
    except Exception:
        return None

def _log_acceso(id_usuario: int, resultado: str):
    sb = get_client()
    try:
        sb.table("tblogacceso").insert({
            "id_usuario": id_usuario,
            "fecha_acceso": datetime.now().isoformat(),
            "ip": "web-client",
            "resultado": resultado
        }).execute()
    except Exception:
        pass

def logout():
    st.session_state.logged_in = False
    st.session_state.usuario = None
