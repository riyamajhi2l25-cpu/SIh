import streamlit as st
import numpy as np
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta

st.set_page_config(page_title="Sikkim Nowcast", layout="wide", page_icon="⛈️")

st.markdown("""
<style>
.stApp { background: #0A0E1C; }
.block-container { padding-top: 0.8rem; }
.header { background: linear-gradient(180deg, #111A33 0%, #0D1226 100%); border: 1px solid rgba(255,255,255,0.06); border-radius: 18px; padding: 18px 22px; }
.glass { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 16px; }
.card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); border-radius: 14px; padding: 14px; }
</style>
""", unsafe_allow_html=True)

# CLEAN HEADER - NO EXTRA TEXT
now = datetime.now()
st.markdown(f"""
<div class="header">
<div style="display:flex; justify-content:space-between; align-items:center;">
<div>
<div style="font-size:13px; opacity:0.5; letter-spacing:1px;">SIKKIM • 0-6 HOUR NOWCAST</div>
<div style="font-size:24px; font-weight:700; margin-top:4px;">Convective Weather Nowcasting</div>
</div>
<div style="text-align:right">
<div style="font-size:13px; opacity:0.6;">{now.strftime("%d %b, %H:%M")} IST</div>
<div style="margin-top:6px; background: #1E293B; padding:5px 12px; border-radius:20px; font-size:11px;">LIVE TRACKING</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    district = st.selectbox("District", ["Gangtok", "Mangan", "Gyalshing", "Namchi", "Pakyong", "Soreng"], index=0)

coords = {"Gangtok": [27.3389, 88.6065], "Mangan": [27.5142, 88.5337], "Gyalshing": [27.2926, 88.2667], "Namchi": [27.1658, 88.3630], "Pakyong": [27.2366, 88.5928], "Soreng": [27.1922, 88.1985]}
lat, lon = coords[district]

lead = st.select_slider("", options=list(range(0, 361, 15)), value=60, label_visibility="collapsed")
st.caption(f"Timeline: T+{lead} min | Drag to forecast 0-6 hours")

seed = hash(district + str(lead)) % 10000
np.random.seed(seed)
max_dbz = 38 + (12 if district in ["Mangan", "Gangtok"] else 8) + lead*0.04 + np.random.uniform(-1,3)

if max_dbz > 58: threat, color, level = "Cloudburst Likely", "#ef4444", "RED"
elif max_dbz > 50: threat, color, level = "Severe Thunderstorm", "#f59e0b", "ORANGE"
elif max_dbz > 42: threat, color, level = "Thunderstorm", "#eab308", "YELLOW"
else: threat, color, level = "No Severe Weather", "#22c55e", "GREEN"

col1, col2 = st.columns([2.4, 1])

with col1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    a,b,c = st.columns(3)
    a.markdown(f"<div class='card'><div style='font-size:10px;opacity:0.5'>PRIMARY THREAT</div><div style='font-size:14px;font-weight:700;color:{color};margin-top:4px'>{threat.upper()}</div><div style='font-size:11px;opacity:0.6;margin-top:2px'>T+{lead} min</div></div>", unsafe_allow_html=True)
    b.markdown(f"<div class='card'><div style='font-size:10px;opacity:0.5'>REFLECTIVITY</div><div style='font-size:18px;font-weight:700;margin-top:4px'>{max_dbz:.1f} dBZ</div><div style='font-size:11px;opacity:0.6;margin-top:2px'>{district}</div></div>", unsafe_allow_html=True)
    c.markdown(f"<div class='card'><div style='font-size:10px;opacity:0.5'>ALERT</div><div style='font-size:18px;font-weight:700;color:{color};margin-top:4px'>{level}</div><div style='font-size:11px;opacity:0.6;margin-top:2px'>{district} District</div></div>", unsafe_allow_html=True)

    m = folium.Map(location=[27.33, 88.61], zoom_start=9, tiles="CartoDB dark_matter")
    move_lat = -lead*0.0012
    move_lon = lead*0.001
    for i in range(4):
        clat = lat + np.random.uniform(-0.25, 0.25) + move_lat
        clon = lon + np.random.uniform(-0.25, 0.25) + move_lon
        intensity = max_dbz - i*3
        col = "#ef4444" if intensity>55 else "#f59e0b" if intensity>45 else "#38bdf8"
        folium.CircleMarker([clat, clon], radius=9, color=col, fill=True, fill_color=col, fill_opacity=0.85).add_to(m)
    folium.Marker([lat, lon], icon=folium.Icon(color="blue")).add_to(m)

    st_folium(m, width=800, height=420, key=f"map_{district}_{lead}")

    times = [f"T+{t}" for t in range(0, 361, 30)]
    vals = [max_dbz - (t-lead)*0.03 + np.random.uniform(-0.8,0.8) for t in range(0,361,30)]
    fig = go.Figure(go.Scatter(x=times, y=vals, mode='lines', line=dict(color=color, width=2.5), fill='tozeroy'))
    fig.update_layout(height=160, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#6b7280", size=10), xaxis=dict(showgrid=False), yaxis=dict(showgrid=False, range=[25,70]))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("**Threats**")
    for name, prob in [("Cloudburst", 72 if max_dbz>58 else 15), ("Thunderstorm", 85 if max_dbz>45 else 25), ("Lightning", 78 if max_dbz>48 else 20), ("Squall", 65 if max_dbz>42 else 18), ("Heavy Rain", 88 if max_dbz>40 else 28), ("Hailstorm", 42 if max_dbz>55 else 10)]:
        col_bar = "#ef4444" if prob>70 else "#f59e0b" if prob>40 else "#2a2f45"
        st.markdown(f"<div class='card' style='padding:10px 12px; margin-bottom:6px;'><div style='display:flex;justify-content:space-between; font-size:12px;'><span>{name}</span><span style='font-weight:600;'>{prob}%</span></div><div style='height:3px;background:#1a1f35;border-radius:10px;margin-top:6px'><div style='height:3px;width:{prob}%;background:{col_bar};border-radius:10px'></div></div></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="glass" style="border-left:3px solid {color}">
    <div style="font-size:10px; opacity:0.5;">ADVISORY • T+{lead}</div>
    <div style="font-size:13px; margin-top:6px; line-height:1.4;">
    {"High risk of intense rain in higher reaches. Avoid trekking & riverside areas." if level=="RED" else "Thunderstorm with gusty winds expected. Stay indoors." if level=="ORANGE" or level=="YELLOW" else "No severe weather expected. Stay updated."}
    </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='text-align:center; opacity:0.3; font-size:10px; margin-top:20px;'>0-6 Hour Convective Nowcasting • 1km Resolution</div>", unsafe_allow_html=True)
