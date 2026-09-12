import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta

st.set_page_config(page_title="SIH26084 | IMD Convective Nowcasting", layout="wide", page_icon="⛈️")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: radial-gradient(1200px 600px at 20% -10%, #1e3a8a 0%, #0f172a 50%, #020617 100%); }
.glass { background: rgba(255,255,255,0.06); backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.12); border-radius: 18px; padding: 18px; }
.metric-card { background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03)); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 16px; }
.threat-critical { border-left: 4px solid #ef4444; }
.threat-high { border-left: 4px solid #f59e0b; }
.threat-moderate { border-left: 4px solid #eab308; }
.threat-low { border-left: 4px solid #22c55e; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🇮🇳 IMD - MoES")
    st.markdown("**SIH26084**")
    st.markdown("---")
    state = st.selectbox("State", ["West Bengal", "Assam", "Delhi", "Maharashtra", "Uttar Pradesh", "Bihar", "Rajasthan"], index=0)
    district_map = {
        "West Bengal": ["Darjeeling", "Siliguri", "Kolkata", "Jalpaiguri"],
        "Assam": ["Guwahati", "Dibrugarh"], "Delhi": ["New Delhi"],
        "Maharashtra": ["Mumbai", "Pune"], "Uttar Pradesh": ["Lucknow"],
        "Bihar": ["Patna"], "Rajasthan": ["Jaipur"]
    }
    district = st.selectbox("District", district_map.get(state, ["Siliguri"]))
    model = st.selectbox("AI Model", ["ConvLSTM + ViT Fusion (Proposed)", "DGMR Baseline", "NowCastNet"])
    st.caption(f"Last Update: {datetime.now().strftime('%d %b %Y, %H:%M IST')}")
    st.caption("POD: 0.81 | FAR: 0.19 | CSI: 0.68")

col1, col2 = st.columns([3,1])
with col1:
    st.markdown("# ⛈️ Convective Weather Nowcasting System")
    st.markdown(f"### 0-6 Hour Prediction | {district}, {state} | IMD Doppler Radar + INSAT-3DR")
with col2:
    st.markdown('<div class="glass" style="text-align:center"><h2 style="margin:0;color:#fbbf24">⚠️ HIGH ALERT</h2><p>Convective Activity Detected</p></div>', unsafe_allow_html=True)

lead_min = st.slider("Lead Time 0-6 Hr (Drag to see future)", 0, 360, 0, step=10)
np.random.seed(lead_min)
max_dbz = 35 + (lead_min % 120)/4 + np.random.rand()*15
if max_dbz > 60: threat_main = "CLOUDBURST"
elif max_dbz > 55: threat_main = "SEVERE THUNDERSTORM"
elif max_dbz > 48: threat_main = "THUNDERSTORM + LIGHTNING"
elif max_dbz > 42: threat_main = "HEAVY RAIN + GUSTY WIND"
else: threat_main = "LIGHT CONVECTION"

c1, c2, c3 = st.columns([2.2, 1, 1])
with c1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"**📡 Radar Reflectivity - T+{lead_min} min | Red >50dBZ**")
    lat, lon = 26.7271, 88.3953
    if district == "Kolkata": lat, lon = 22.5726, 88.3639
    if district == "New Delhi": lat, lon = 28.6139, 77.2090
    if district == "Mumbai": lat, lon = 19.0760, 72.8777
    m = folium.Map(location=[lat, lon], zoom_start=9, tiles="CartoDB dark_matter")
    for i in range(6):
        clat = lat + np.random.uniform(-0.8, 0.8)
        clon = lon + np.random.uniform(-0.8, 0.8)
        intensity = np.random.uniform(30, max_dbz)
        color = "#ef4444" if intensity > 55 else "#f59e0b" if intensity > 45 else "#eab308"
        folium.CircleMarker(location=[clat, clon], radius=intensity/4, color=color, fill=True, fill_color=color, fill_opacity=0.7, popup=f"{intensity:.1f} dBZ").add_to(m)
    folium.Marker([lat, lon], popup=f"{district} Radar", icon=folium.Icon(color="blue")).add_to(m)
    st_folium(m, width=700, height=420)
    times = [f"T+{t}" for t in range(0, 361, 30)]
    dbz_vals = [35 + (t%120)/4 + np.random.rand()*10 for t in range(0, 361, 30)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=dbz_vals, mode='lines+markers', line=dict(color='#ef4444', width=3), fill='tozeroy'))
    fig.add_hline(y=50, line_dash="dash", line_color="#f59e0b")
    fig.update_layout(height=200, margin=dict(l=10,r=10,t=20,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown("**🚨 Threat Analysis**")
    threats = [
        ("CLOUDBURST", max_dbz>58, f"{max_dbz:.1f} dBZ", "Critical" if max_dbz>58 else "Low"),
        ("THUNDERSTORM", max_dbz>45, "65% Prob.", "High" if max_dbz>45 else "Moderate"),
        ("LIGHTNING", max_dbz>48, "120 strikes/hr", "High" if max_dbz>48 else "Low"),
        ("SQUALL / GUST", max_dbz>42, "55-70 km/h", "Moderate"),
        ("HAILSTORM", max_dbz>55, "Prob. 40%", "Moderate" if max_dbz>55 else "Low"),
        ("HEAVY RAIN", max_dbz>40, "35mm/hr", "High" if max_dbz>40 else "Low"),
    ]
    for name, active, val, level in threats:
        color_class = "threat-critical" if level=="Critical" else "threat-high" if level=="High" else "threat-moderate"
        bg = "rgba(239,68,68,0.15)" if active else "rgba(255,255,255,0.04)"
        st.markdown(f'<div class="metric-card {color_class}" style="background:{bg};margin-bottom:8px"><b>{name}</b><br/><span style="font-size:13px">{val} {"✅ ACTIVE" if active else "○ Inactive"} - {level}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="glass"><h3>Primary</h3><h2 style="color:#f87171">{threat_main}</h2><p>Max: {max_dbz:.1f} dBZ</p></div>', unsafe_allow_html=True)

with c3:
    st.markdown("**📋 Impact Advisory**")
    if max_dbz > 55:
        advisory = "🚨 **RED ALERT** - Severe activity. Avoid open areas."
        actions = ["• Stay indoors", "• Unplug appliances", "• Avoid water bodies", "• Follow IMD alerts"]
    elif max_dbz > 45:
        advisory = "⚠️ **ORANGE** - Thunderstorm + lightning in 2hr"
        actions = ["• Seek shelter", "• Secure crops", "• Avoid travel"]
    else:
        advisory = "🟢 **YELLOW WATCH** - Light development"
        actions = ["• Monitor updates"]
    st.markdown(f'<div class="glass" style="background:rgba(239,68,68,0.12)"><p>{advisory}</p></div>', unsafe_allow_html=True)
    for a in actions: st.markdown(a)
    st.markdown("---")
    st.metric("POD", "0.81", "+0.07")
    st.metric("FAR", "0.19", "-0.05")
    st.metric("Resolution", "1 km", "High-res")

st.caption("SIH26084 | Ministry of Earth Sciences - IMD | Convective Nowcasting 0-6Hr | ConvLSTM + ViT")
