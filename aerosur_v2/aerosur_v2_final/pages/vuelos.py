import streamlit as st
from utils.supabase_client import get_client

def render():
    sb = get_client()
    st.markdown('<div class="section-title">✈️ Gestión de Vuelos</div>', unsafe_allow_html=True)

    if st.session_state.get("mensaje_exito"):
        st.success(st.session_state.mensaje_exito)
        st.session_state.mensaje_exito = ""

    tab1, tab2, tab3 = st.tabs(["📋  Listado", "➕  Nuevo vuelo", "🔍  Detalle por vuelo"])

    with tab1:
        try:
            rows = (
                sb.table("tbvuelo")
                .select("*, tbavion(matricula, tbtipoavion(nombre))")
                .order("fecha_salida")
                .execute()
                .data
            )
            if not rows:
                st.info("No hay vuelos registrados.")
                return

            for v in rows:
                avion = v.get("tbavion") or {}
                tipo  = (avion.get("tbtipoavion") or {}).get("nombre","—")
                mat   = avion.get("matricula","—")
                sal   = v["fecha_salida"][:16].replace("T"," ")
                lle   = v["fecha_llegada"][:16].replace("T"," ")

                with st.expander(f"🛫  {v['numero_vuelo']}  |  {v['origen']} → {v['destino']}  |  {sal}"):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Origen", v["origen"])
                    c2.metric("Destino", v["destino"])
                    c3.metric("Avión", mat)
                    c1.metric("Salida", sal)
                    c2.metric("Llegada", lle)
                    c3.metric("Tipo", tipo)

                    trip = (
                        sb.table("tbvuelotripulacion")
                        .select("tbtripulacion(nombre, apellido, rol)")
                        .eq("id_vuelo", v["id_vuelo"])
                        .execute()
                        .data
                    )
                    if trip:
                        st.markdown('<div style="font-family:Space Mono,monospace;font-size:0.7rem;color:#5A6A8A;margin-top:1rem;margin-bottom:0.5rem;">TRIPULACIÓN</div>', unsafe_allow_html=True)
                        cols = st.columns(min(len(trip), 4))
                        for i, t in enumerate(trip):
                            tr = t.get("tbtripulacion") or {}
                            cols[i % 4].markdown(f"""
                            <div style='background:#04060F;border:1px solid #1A2540;border-radius:6px;padding:0.5rem 0.75rem;text-align:center;margin-bottom:0.5rem;'>
                                <div style='font-family:Syne,sans-serif;font-size:0.85rem;color:#E8EDF5;'>{tr.get('nombre','')} {tr.get('apellido','')}</div>
                                <div style='font-family:Space Mono,monospace;font-size:0.7rem;color:#FF6B35;'>{tr.get('rol','')}</div>
                            </div>
                            """, unsafe_allow_html=True)

                    res = (
                        sb.table("tbreserva")
                        .select("id_asiento, tbpasajero(nombre, apellido, pasaporte, nacionalidad)")
                        .eq("id_vuelo", v["id_vuelo"])
                        .execute()
                        .data
                    )
                    st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:0.7rem;color:#5A6A8A;margin-top:1rem;margin-bottom:0.5rem;">PASAJEROS ({len(res)})</div>', unsafe_allow_html=True)
                    if res:
                        import pandas as pd
                        data = []
                        for r in res:
                            p = r.get("tbpasajero") or {}
                            num_asiento = ""
                            if r.get("id_asiento"):
                                try:
                                    ad = sb.table("tbasiento").select("numero_asiento").eq("id_asiento", r["id_asiento"]).single().execute().data
                                    num_asiento = ad.get("numero_asiento","") if ad else ""
                                except:
                                    pass
                            data.append({
                                "Nombre": f"{p.get('nombre','')} {p.get('apellido','')}",
                                "Pasaporte": p.get("pasaporte",""),
                                "Nacionalidad": p.get("nacionalidad",""),
                                "Asiento": num_asiento,
                            })
                        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
                    else:
                        st.info("No hay pasajeros reservados en este vuelo.")

                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🗑️  Eliminar vuelo", key=f"del_vuelo_{v['id_vuelo']}"):
                        id_v = v["id_vuelo"]
                        sb.table("tbreserva").delete().eq("id_vuelo", id_v).execute()
                        sb.table("tbasiento").delete().eq("id_vuelo", id_v).execute()
                        sb.table("tbvuelotripulacion").delete().eq("id_vuelo", id_v).execute()
                        sb.table("tbvuelo").delete().eq("id_vuelo", id_v).execute()
                        st.session_state.mensaje_exito = "✅ Vuelo eliminado correctamente."
                        st.rerun()

        except Exception as e:
            st.error(str(e))

    with tab2:
        st.markdown('<div style="font-family:Syne,sans-serif;font-size:0.7rem;letter-spacing:0.15em;color:#5A6A8A;text-transform:uppercase;margin-bottom:1rem;">Registrar nuevo vuelo</div>', unsafe_allow_html=True)

        try:
            aviones    = sb.table("tbavion").select("id_avion, matricula").eq("estado","Activo").execute().data
            avion_opts = {a["matricula"]: a["id_avion"] for a in aviones}
        except:
            avion_opts = {}

        col1, col2 = st.columns(2)
        with col1:
            num_vuelo = st.text_input("Número de vuelo", placeholder="AS101")
            origen    = st.text_input("Origen", placeholder="Guatemala")
            fecha_sal = st.date_input("Fecha de salida")
            hora_sal  = st.time_input("Hora de salida")
        with col2:
            matricula_sel = st.selectbox("Avión", list(avion_opts.keys()) if avion_opts else ["Sin aviones activos"])
            destino   = st.text_input("Destino", placeholder="México")
            fecha_lle = st.date_input("Fecha de llegada")
            hora_lle  = st.time_input("Hora de llegada")

        if st.button("REGISTRAR VUELO →", use_container_width=True):
            if not all([num_vuelo, origen, destino]):
                st.error("❌ Completa todos los campos.")
            elif not avion_opts:
                st.error("❌ No hay aviones activos disponibles.")
            else:
                try:
                    existe = sb.table("tbvuelo").select("id_vuelo").eq("numero_vuelo", num_vuelo).execute().data
                    if existe:
                        st.error(f"❌ Ya existe un vuelo con el número {num_vuelo}.")
                    else:
                        sal_dt = f"{fecha_sal}T{hora_sal}"
                        lle_dt = f"{fecha_lle}T{hora_lle}"
                        sb.table("tbvuelo").insert({
                            "numero_vuelo": num_vuelo, "origen": origen,
                            "destino": destino, "fecha_salida": sal_dt,
                            "fecha_llegada": lle_dt, "id_avion": avion_opts[matricula_sel]
                        }).execute()
                        st.session_state.mensaje_exito = f"✅ Vuelo {num_vuelo} registrado exitosamente ({origen} → {destino})."
                        st.rerun()
                except Exception as e:
                    st.error(str(e))

    with tab3:
        num_buscar = st.text_input("Número de vuelo a buscar", placeholder="AS101")
        if st.button("BUSCAR"):
            try:
                result = sb.table("tbvuelo").select("*").eq("numero_vuelo", num_buscar.upper()).execute().data
                if result:
                    v = result[0]
                    st.success(f"✅ Vuelo encontrado: {v['origen']} → {v['destino']}")
                    st.json(v)
                else:
                    st.warning("No se encontró ningún vuelo con ese número.")
            except Exception as e:
                st.error(str(e))
