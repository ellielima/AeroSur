import streamlit as st
from utils.supabase_client import get_client

def render():
    sb = get_client()

    st.markdown('<div class="section-title">Dashboard</div>', unsafe_allow_html=True)

    # ── KPIs ──────────────────────────────────────────────────────────────────
    try:
        vuelos      = sb.table("tbvuelo").select("id_vuelo", count="exact").execute().count or 0
        pasajeros   = sb.table("tbpasajero").select("id_pasajero", count="exact").execute().count or 0
        reservas    = sb.table("tbreserva").select("id_reserva", count="exact").execute().count or 0
        tripulantes = sb.table("tbtripulacion").select("id_tripulante", count="exact").execute().count or 0
    except Exception as e:
        st.error(f"Error al conectar con Supabase: {e}")
        return

    c1, c2, c3, c4 = st.columns(4)
    for col, label, value, color in [
        (c1, "VUELOS PROGRAMADOS", vuelos,      "#00D4FF"),
        (c2, "PASAJEROS REGISTRADOS", pasajeros, "#00FF9F"),
        (c3, "RESERVAS ACTIVAS", reservas,       "#FF6B35"),
        (c4, "TRIPULANTES", tripulantes,         "#A78BFA"),
    ]:
        with col:
            st.markdown(f"""
            <div class="aerosur-card">
                <h3>{label}</h3>
                <div class="value" style="color:{color}">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Últimos vuelos ────────────────────────────────────────────────────────
    col_a, col_b = st.columns([1.6, 1])

    with col_a:
        st.markdown('<div style="font-family:Syne,sans-serif;font-size:0.7rem;letter-spacing:0.15em;color:#5A6A8A;text-transform:uppercase;margin-bottom:0.75rem;">Próximos vuelos</div>', unsafe_allow_html=True)
        try:
            rows = (
                sb.table("tbvuelo")
                .select("numero_vuelo, origen, destino, fecha_salida, tbavion(matricula)")
                .order("fecha_salida")
                .limit(10)
                .execute()
                .data
            )
            if rows:
                for v in rows:
                    matricula = v.get("tbavion", {}).get("matricula", "—") if v.get("tbavion") else "—"
                    salida = v["fecha_salida"][:16].replace("T", " ")
                    st.markdown(f"""
                    <div style='background:#0C1020;border:1px solid #1A2540;border-radius:6px;
                                padding:0.75rem 1rem;margin-bottom:0.5rem;display:flex;
                                justify-content:space-between;align-items:center;'>
                        <div>
                            <span style='font-family:Space Mono,monospace;font-size:0.85rem;
                                        color:#00D4FF;font-weight:700;'>{v['numero_vuelo']}</span>
                            <span style='font-family:Syne,sans-serif;color:#E8EDF5;margin:0 0.5rem;'>
                                {v['origen']} → {v['destino']}
                            </span>
                        </div>
                        <div style='text-align:right;'>
                            <div style='font-family:Space Mono,monospace;font-size:0.7rem;color:#5A6A8A;'>{salida}</div>
                            <div style='font-family:Space Mono,monospace;font-size:0.7rem;color:#FF6B35;'>{matricula}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No hay vuelos registrados.")
        except Exception as e:
            st.error(str(e))

    with col_b:
        st.markdown('<div style="font-family:Syne,sans-serif;font-size:0.7rem;letter-spacing:0.15em;color:#5A6A8A;text-transform:uppercase;margin-bottom:0.75rem;">Destinos</div>', unsafe_allow_html=True)
        try:
            destinos_raw = sb.table("tbvuelo").select("destino").execute().data
            from collections import Counter
            conteo = Counter(r["destino"] for r in destinos_raw)
            colores = ["#00D4FF", "#00FF9F", "#FF6B35", "#A78BFA", "#FFD166"]
            for i, (dest, cnt) in enumerate(conteo.most_common(5)):
                color = colores[i % len(colores)]
                st.markdown(f"""
                <div style='background:#0C1020;border:1px solid #1A2540;border-radius:6px;
                            padding:0.6rem 1rem;margin-bottom:0.4rem;
                            display:flex;justify-content:space-between;align-items:center;'>
                    <span style='font-family:Syne,sans-serif;color:#E8EDF5;'>{dest}</span>
                    <span style='font-family:Space Mono,monospace;font-size:0.85rem;
                                color:{color};font-weight:700;'>{cnt} vuelo{"s" if cnt>1 else ""}</span>
                </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.error(str(e))
