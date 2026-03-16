from supabase import create_client, Client
import streamlit as st

# ── CREDENCIALES DE SUPABASE ──────────────────────────────
SUPABASE_URL = "https://fovyfytnhoszeykkqcfz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZvdnlmeXRuaG9zemV5a2txY2Z6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMyOTEzMjMsImV4cCI6MjA4ODg2NzMyM30.-B1rfqGYK0OI3CUV43QfLOMpZBVUx955ATfMKTXg3Qg"

@st.cache_resource
def get_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)
