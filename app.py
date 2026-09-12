import streamlit as st
import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="Sikkim Nowcast", layout="wide", page_icon="⛈️")

st.markdown("""
<style>
.stApp { background: #080C1A; }
.block-container { padding-top: 0.6rem; }
.header { background: linear-gradient(180deg, #111A33 0%, #0D1226 100%); border: 1px solid rgba(255,255,255,0.06); border-radius: 20px; padding: 18px 24px; }
.glass { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 18px; padding: 18px; }
.card { background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02)); border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 14px; transition: 0.2s; }
.card:hover { border-color: rgba(255,255,255,0.12); }
.small { font-size:11px; opacity:0.55; letter-spacing:0.3px; }
.pill { padding:3px 8px; border-radius:20px; font-size:10px; font-weight:700; letter-spacing:0.5px; }
</style>
""", unsafe_allow_html=True)

now = datetime.now()
st.markdown(f"""
<div class="header">
<div style="display:flex; justify-content:space-between; align-items:center;">
<div>
<div style="font-size:11px; opacity:0.5; letter-spacing:2px;">0-6 HOUR • 1KM RESOLUTION</div>
<div style="font-size:24px; font-weight:700; margin-top:4px; letter-spacing:-0.5px;">Sikkim Weather Nowcasting</div>
<div style="font-size:11px; opacity:0.45; margin-top:3px;">{now.strftime("%d %B %Y")} • Live Radar Tracking</div>
</div>
<div style="text-align:right">
<div style="font-size:12px; opacity:0.7;">{now.strftime("%H:%M IST")}</div>
<div style="margin-top:8px; display:flex; gap:6px; justify-content:flex-end;">
<div style="background: rgba(34,197,94,0.15); border:1px solid rgba(34,197,94,0.3); color:#22c55e; padding:4px 10px; border-radius:20px; font-size:10px; font-weight:600;">● LIVE</div>
<div style="background: rgba(255,255,255,0.06); padding:4px 10px; border-radius:20px; font-size:10px;">T+0 to T+360</div>
</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

# DISTRICT
with st.sidebar:
    district = st.selectbox("District", ["Gangtok", "Mangan", "Gyalshing", "Namchi", "Pakyong", "Soreng"], index=0)
    st.markdown("---")
    st.markdown('<div class="small">RADAR • DWR Gangtok • INSAT-3DR</div>', unsafe_allow_html=True)
    st.markdown('<div class="small" style="margin-top:8px;">RESOLUTION: 1 km<br>LATENCY: ~4 min<br>MODEL: ConvLSTM-ViT</div>', unsafe_allow_html=True)

coords = {"Gangtok": [27.3389, 88.6065], "Mangan": [27.5142, 88.5337], "Gyalshing": [27.2926, 88.2667], "Namchi": [27.1658, 88.3630], "Pakyong": [27.2366, 88.5928], "Soreng": [27.1922, 88.1985]}
lat, lon = coords[district]

# TIMELINE
lead = st.select_slider(" ", options=list(range(0, 361, 15)), value=60, label_visibility="collapsed")
st.markdown(f"<div style='display:flex; justify-content:space-between;'><span class='small'>T+0 MIN • NOW</span><span style='font-size:12px; font-weight:600;'>T+{lead} MIN FORECAST</span><span class='small'>T+360 MIN • +6 HR</span></div>", unsafe_allow_html=True)

seed = hash(district + str(lead)) % 10000
np.random.seed(seed)
random.seed(seed)
max_dbz = 38 + (12 if district in ["Mangan", "Gangtok"] else 8) + lead*0.04 + np.random.uniform(-1,3)

if max_dbz > 58: threat, color, level, desc = "CLOUDBURST", "#ef4444", "CRITICAL", "Extreme rainfall risk in higher reaches"
elif max_dbz > 50: threat, color, level, desc = "SEVERE THUNDERSTORM", "#f59e0b", "HIGH", "Thunderstorm with intense lightning"
elif max_dbz > 42: threat, color, level, desc = "THUNDERSTORM", "#eab308", "MODERATE", "Isolated thunderstorm expected"
else: threat, color, level, desc = "NO SEVERE", "#22c55e", "LOW", "No significant weather"

col1, col2 = st.columns([2.5, 1])

with col1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)

    # TOP METRICS - PROFESSIONAL
    m1,m2,m3,m4 = st.columns(4)
    m1.markdown(f"<div class='card' style='border-left:3px solid {color}'><div class='small'>PRIMARY THREAT</div><div style='font-size:12px; font-weight:700; color:{color}; margin-top:6px;'>{threat}</div><div class='small' style='margin-top:4px;'>{level} • T+{lead}</div></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='card'><div class='small'>REFLECTIVITY</div><div style='font-size:18px; font-weight:700; margin-top:6px;'>{max_dbz:.1f} dBZ</div><div class='small' style='margin-top:4px;'>Max in {district}</div></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='card'><div class='small'>RAINFALL</div><div style='font-size:18px; font-weight:700; margin-top:6px;'>{max(0,(max_dbz-30)*1.6):.1f} mm/hr</div><div class='small' style='margin-top:4px;'>Next 60 min</div></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='card'><div class='small'>WIND GUST</div><div style='font-size:18px; font-weight:700; margin-top:6px;'>{20+max_dbz*0.55:.0f} km/h</div><div class='small' style='margin-top:4px;'>NW → SE</div></div>", unsafe_allow_html=True)

    # MAP - SCROLL FIX: scrollWheelZoom=False + dragging=False, only zoom buttons work
    m = folium.Map(location=[lat, lon], zoom_start=10, tiles="CartoDB dark_matter", scrollWheelZoom=False, dragging=False, doubleClickZoom=False, zoom_control=True)

    move_lat = -lead*0.0012
    move_lon = lead*0.001
    for i in range(5):
        clat = lat + np.random.uniform(-0.3, 0.3) + move_lat
        clon = lon + np.random.uniform(-0.3, 0.3) + move_lon
        intensity = max_dbz - i*2.5
        c = "#ef4444" if intensity>55 else "#f59e0b" if intensity>45 else "#38bdf8" if intensity>38 else "#3b82f6"
        folium.CircleMarker([clat, clon], radius= max(6, intensity/5), color=c, fill=True, fill_color=c, fill_opacity=0.8, weight=1).add_to(m)
        if i==0 and max_dbz>50:
            folium.Circle([clat, clon], radius=5000, color=c, fill=True, fill_opacity=0.15, weight=1).add_to(m)

    folium.Marker([lat, lon], icon=folium.Icon(color="white", icon="tower-broadcast", prefix="fa")).add_to(m)

    st_folium(m, width=850, height=440, key=f"map_{district}_{lead}", returned_objects=[])

    st.markdown("<div class='small' style='text-align:center; margin-top:8px;'>Map controls: Use +/- buttons to zoom • Scroll is disabled to prevent page glitch • Storm cells moving SE</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("**Threat Matrix**")

    threats = [
        ("Cloudburst", 78 if max_dbz>58 else 18, max_dbz>58, "Critical" if max_dbz>58 else "Low", f"{random.randint(1,3)} hr" if max_dbz>58 else "-"),
        ("Thunderstorm", 88 if max_dbz>45 else 32, max_dbz>45, "High" if max_dbz>50 else "Moderate" if max_dbz>42 else "Low", f"{random.randint(2,4)} hr" if max_dbz>45 else "-"),
        ("Lightning", 84 if max_dbz>48 else 26, max_dbz>48, "High" if max_dbz>50 else "Moderate", f"{random.randint(2,5)} hr" if max_dbz>48 else "-"),
        ("Hailstorm", 52 if max_dbz>55 else 10, max_dbz>55, "Moderate" if max_dbz>55 else "Low", f"{random.randint(1,2)} hr" if max_dbz>55 else "-"),
        ("Squall", 70 if max_dbz>42 else 20, max_dbz>42, "Moderate" if max_dbz>45 else "Low", f"{random.randint(2,3)} hr" if max_dbz>42 else "-"),
        ("Heavy Rain", 92 if max_dbz>40 else 34, max_dbz>40, "High" if max_dbz>50 else "Moderate", f"{random.randint(3,6)} hr" if max_dbz>40 else "-"),
    ]

    for name, prob, active, lvl, duration in threats:
        active_color = "#ef4444" if lvl=="Critical" else "#f59e0b" if lvl=="High" else "#eab308" if lvl=="Moderate" else "#2a3441"
        status_bg = "rgba(239,68,68,0.12)" if active else "rgba(255,255,255,0.02)"
        status_text = "● ACTIVE" if active else "○ INACTIVE"
        status_col = "#ef4444" if active and lvl=="Critical" else "#f59e0b" if active else "#6b7280"

        st.markdown(f"""
        <div class='card' style='margin-bottom:8px; background:{status_bg}; border-left:3px solid {active_color};'>
        <div style='display:flex; justify-content:space-between; align-items:center;'>
        <div style='font-size:12px; font-weight:600;'>{name.upper()}</div>
        <div class='pill' style='background:{active_color}20; color:{active_color}; border:1px solid {active_color}40;'>{lvl}</div>
        </div>
        <div style='display:flex; justify-content:space-between; margin-top:8px; align-items:center;'>
        <div style='font-size:11px; color:{status_col}; font-weight:600;'>{status_text}</div>
        <div style='font-size:11px; opacity:0.7;'>{prob}% • {duration}</div>
        </div>
        <div style='height:3px; background:#151a2a; border-radius:10px; margin-top:8px;'><div style='height:3px; width:{prob}%; background:{active_color}; border-radius:10px;'></div></div>
        </div>
        """, unsafe_allow_html=True)

    # ADVISORY
    st.markdown(f"""
    <div class="glass" style="border-left:3px solid {color}; margin-top:14px;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
    <div style="font-size:10px; opacity:0.5; letter-spacing:1px;">ADVISORY • T+{lead} MIN</div>
    <div class='pill' style='background:{color}20; color:{color}; border:1px solid {color}40;'>{level}</div>
    </div>
    <div style="font-size:13px; font-weight:700; color:{color}; margin-top:10px;">{threat} - {district}</div>
    <div style="font-size:11px; margin-top:8px; line-height:1.5; opacity:0.8;">{desc}. Wind {20+max_dbz*0.55:.0f} km/h. {"Avoid higher reaches, NH-10 landslide risk." if level in ["CRITICAL","HIGH"] else "Stay indoors during thunder, avoid hilltops." if level=="MODERATE" else "No major impact expected."}</div>
    <div style="margin-top:12px; padding-top:10px; border-top:1px solid rgba(255,255,255,0.06); display:flex; justify-content:space-between;">
    <span class='small'>Valid: {(now+timedelta(minutes=lead)).strftime("%H:%M")} - {(now+timedelta(minutes=lead+60)).strftime("%H:%M")}</span>
    <span class='small'>Confidence {max(62, 92-lead*0.08):.0f}%</span>
    </div>
    </div>
    """, unsafe_allow_html=True)

# FOOTER STATS - PREMIUM
st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
f1,f2,f3,f4,f5 = st.columns(5)
f1.markdown(f"<div class='card' style='text-align:center;'><div class='small'>MAX DBZ</div><div style='font-weight:700; margin-top:4px;'>{max_dbz:.1f}</div></div>", unsafe_allow_html=True)
f2.markdown(f"<div class='card' style='text-align:center;'><div class='small'>LIGHTNING</div><div style='font-weight:700; margin-top:4px;'>{int(max_dbz*2.2)}/hr</div></div>", unsafe_allow_html=True)
f3.markdown(f"<div class='card' style='text-align:center;'><div class='small'>COVERAGE</div><div style='font-weight:700; margin-top:4px;'>{12+max_dbz*0.28:.1f}%</div></div>", unsafe_allow_html=True)
f4.markdown(f"<div class='card' style='text-align:center;'><div class='small'>MOVEMENT</div><div style='font-weight:700; margin-top:4px;'>SE {18+max_dbz*0.4:.0f} km/h</div></div>", unsafe_allow_html=True)
f5.markdown(f"<div class='card' style='text-align:center;'><div class='small'>NEXT UPDATE</div><div style='font-weight:700; margin-top:4px;'>{(now+timedelta(minutes=10)).strftime('%H:%M')}</div></div>", unsafe_allow_html=True)
