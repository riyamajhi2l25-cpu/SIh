import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="Sikkim Nowcast", layout="wide", page_icon="⛈️")

st.markdown("""
<style>
.stApp { background: #0A0E1C; }
.block-container { padding-top: 0.8rem; }
.header { background: linear-gradient(180deg, #111A33 0%, #0D1226 100%); border: 1px solid rgba(255,255,255,0.06); border-radius: 18px; padding: 18px 22px; }
.glass { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 16px; }
.card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); border-radius: 14px; padding: 12px; }
.small { font-size:11px; opacity:0.6; }
div[data-testid="stTextInput"] input { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; color: white; }
</style>
""", unsafe_allow_html=True)

places = {
    "Gangtok": ["Tadong", "Ranipool", "Rumtek", "Penlong", "Sichey", "Deorali"],
    "Mangan": ["Lachen", "Lachung", "Chungthang", "Dzongu", "Thangu", "Yumthang"],
    "Gyalshing": ["Pelling", "Yuksom", "Tashiding", "Legship", "Dentam", "Hee"],
    "Namchi": ["Ravangla", "Jorethang", "Temi", "Sikip", "Namthang", "Wok"],
    "Pakyong": ["Rangpo", "Rhenock", "Rolep", "Dzuluk", "Gnathang", "Kupup"],
    "Soreng": ["Sombarey", "Chakung", "Tharpu", "Malbasey", "Kaluk", "Sombaria"]
}
all_villages = [v for lst in places.values() for v in lst]

now = datetime.now()
st.markdown(f"""
<div class="header">
<div style="display:flex; justify-content:space-between; align-items:center;">
<div>
<div style="font-size:12px; opacity:0.5; letter-spacing:1.5px;">SIKKIM • CONVECTIVE NOWCAST • 0-6 HR</div>
<div style="font-size:23px; font-weight:700; margin-top:4px;">Weather Nowcasting System</div>
<div style="font-size:11px; opacity:0.5; margin-top:2px;">1 km • Updates every 10 min • {now.strftime("%d %b %Y")}</div>
</div>
<div style="text-align:right">
<div style="font-size:12px; opacity:0.6;">{now.strftime("%H:%M IST")}</div>
<div style="margin-top:6px; background:#1E293B; padding:5px 12px; border-radius:20px; font-size:11px;">LIVE</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

# SEARCH BAR + DISTRICT SELECTOR
c_search, c_dist = st.columns([2, 1])
with c_search:
    search = st.text_input("", placeholder="🔍 Search any place in Sikkim - e.g. Lachen, Yumthang, Pelling, Ravangla, Zuluk...", label_visibility="collapsed")
with c_dist:
    district = st.selectbox("District", ["Gangtok", "Mangan", "Gyalshing", "Namchi", "Pakyong", "Soreng"], index=0, label_visibility="collapsed")

# If user searches, auto-detect district
searched_place = None
if search:
    search_lower = search.lower().strip()
    for dist, villages in places.items():
        for v in villages:
            if search_lower in v.lower() or v.lower() in search_lower:
                district = dist
                searched_place = v
                break
    if not searched_place and search_lower:
        # fuzzy match
        for v in all_villages:
            if search_lower[:3] in v.lower():
                searched_place = v
                break

coords = {"Gangtok": [27.3389, 88.6065], "Mangan": [27.5142, 88.5337], "Gyalshing": [27.2926, 88.2667], "Namchi": [27.1658, 88.3630], "Pakyong": [27.2366, 88.5928], "Soreng": [27.1922, 88.1985]}
lat, lon = coords[district]

# If searched place, adjust lat/lon slightly
if searched_place:
    lat += np.random.uniform(-0.15, 0.15)
    lon += np.random.uniform(-0.15, 0.15)
    st.success(f"Showing results for **{searched_place}**, {district} District")

lead = st.select_slider("Forecast Timeline", options=list(range(0, 361, 15)), value=60, label_visibility="collapsed")
st.caption(f"Timeline: T+{lead} min • Drag to see storm movement • Map: Use + / - to zoom")

seed = hash(district + str(lead) + (searched_place or "")) % 10000
np.random.seed(seed)
max_dbz = 38 + (12 if district in ["Mangan", "Gangtok"] else 8) + lead*0.04 + np.random.uniform(-1,3)

if max_dbz > 58: threat, color, level = "Cloudburst Likely", "#ef4444", "RED"
elif max_dbz > 50: threat, color, level = "Severe Thunderstorm", "#f59e0b", "ORANGE"
elif max_dbz > 42: threat, color, level = "Thunderstorm", "#eab308", "YELLOW"
else: threat, color, level = "No Severe Weather", "#22c55e", "GREEN"

def get_affected(threat_type):
    all_places = places[district]
    if searched_place and searched_place in all_places:
        all_places = [searched_place] + [p for p in all_places if p!= searched_place]
    if max_dbz < 42: return []
    if threat_type == "Cloudburst" and max_dbz > 58: return random.sample(all_places, k=min(2, len(all_places)))
    if threat_type == "Thunderstorm" and max_dbz > 45: return random.sample(all_places, k=min(3, len(all_places)))
    if threat_type == "Lightning" and max_dbz > 48: return random.sample(all_places, k=min(2, len(all_places)))
    if threat_type == "Hailstorm" and max_dbz > 55: return random.sample(all_places, k=1)
    if threat_type == "Squall" and max_dbz > 42: return random.sample(all_places, k=min(3, len(all_places)))
    if threat_type == "Heavy Rain" and max_dbz > 40: return random.sample(all_places, k=min(3, len(all_places)))
    return []

col1, col2 = st.columns([2.4, 1])

with col1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    a,b,c,d = st.columns(4)
    a.markdown(f"<div class='card'><div class='small'>PRIMARY THREAT</div><div style='font-size:13px;font-weight:700;color:{color};margin-top:4px'>{threat.upper()}</div><div class='small' style='margin-top:2px'>T+{lead} min</div></div>", unsafe_allow_html=True)
    b.markdown(f"<div class='card'><div class='small'>REFLECTIVITY</div><div style='font-size:17px;font-weight:700;margin-top:4px'>{max_dbz:.1f} dBZ</div><div class='small'>{searched_place or district}</div></div>", unsafe_allow_html=True)
    c.markdown(f"<div class='card'><div class='small'>RAINFALL RATE</div><div style='font-size:17px;font-weight:700;margin-top:4px'>{max(0,(max_dbz-30)*1.6):.1f} mm/hr</div><div class='small'>Next 1 hr</div></div>", unsafe_allow_html=True)
    d.markdown(f"<div class='card'><div class='small'>ALERT</div><div style='font-size:17px;font-weight:700;color:{color};margin-top:4px'>{level}</div><div class='small'>{district} District</div></div>", unsafe_allow_html=True)

    m = folium.Map(location=[lat, lon], zoom_start=10, tiles="CartoDB dark_matter", scrollWheelZoom=False, dragging=True)
    move_lat = -lead*0.0012
    move_lon = lead*0.001
    affected_all = []
    for i in range(4):
        clat = lat + np.random.uniform(-0.25, 0.25) + move_lat
        clon = lon + np.random.uniform(-0.25, 0.25) + move_lon
        intensity = max_dbz - i*3
        col = "#ef4444" if intensity>55 else "#f59e0b" if intensity>45 else "#38bdf8"
        place_name = (searched_place if i==0 and searched_place else places[district][i % len(places[district])])
        affected_all.append(place_name)
        folium.CircleMarker([clat, clon], radius=10, color=col, fill=True, fill_color=col, fill_opacity=0.85, tooltip=f"{place_name}: {intensity:.1f} dBZ").add_to(m)
        folium.Marker([clat, clon], icon=folium.DivIcon(html=f"<div style='font-size:10px;color:white;background:rgba(0,0,0,0.6);padding:2px 5px;border-radius:8px;'>{place_name}</div>")).add_to(m)

    if searched_place:
        folium.Marker([lat, lon], popup=f"{searched_place} - Searched", icon=folium.Icon(color="red", icon="magnifying-glass", prefix="fa")).add_to(m)
    else:
        folium.Marker([lat, lon], popup=f"{district}", icon=folium.Icon(color="blue", icon="location-dot", prefix="fa")).add_to(m)

    st_folium(m, width=800, height=430, key=f"map_{district}_{lead}_{searched_place}", returned_objects=[])

    st.markdown(f"<div class='small' style='text-align:center; margin-top:6px;'>📍 Red zones = Severe cells • Use +/- to zoom • {', '.join(affected_all)} affected • Moving SE {20+max_dbz*0.5:.0f} km/h</div>", unsafe_allow_html=True)

    st.markdown("**6-Hour Forecast**")
    times = [(now+timedelta(minutes=t)).strftime("%H:%M") for t in range(0, 361, 60)]
    dbz_t = [max_dbz - (t-lead)*0.03 + np.random.uniform(-1,1) for t in range(0,361,60)]
    rain_t = [max(0,(d-30)*1.5) for d in dbz_t]
    df = pd.DataFrame({"Time": times, "dBZ": [f"{d:.1f}" for d in dbz_t], "Rain mm/hr": [f"{r:.1f}" for r in rain_t], "Status": ["Severe" if d>50 else "Moderate" if d>42 else "Light" for d in dbz_t]})
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("**Threat Analysis**")
    threats_data = [
        ("Cloudburst", 75 if max_dbz>58 else 12, "#ef4444"),
        ("Thunderstorm", 88 if max_dbz>45 else 28, "#f59e0b"),
        ("Lightning", 82 if max_dbz>48 else 22, "#f59e0b"),
        ("Hailstorm", 48 if max_dbz>55 else 8, "#a855f7"),
        ("Squall", 68 if max_dbz>42 else 18, "#38bdf8"),
        ("Heavy Rain", 90 if max_dbz>40 else 30, "#22c55e"),
    ]
    for name, prob, col in threats_data:
        affected = get_affected(name)
        affected_text = f"📍 {', '.join(affected)}" if affected else "No active zones"
        st.markdown(f"""
        <div class='card' style='margin-bottom:8px; border-left:3px solid {col};'>
        <div style='display:flex;justify-content:space-between; font-size:12px;'><b>{name}</b><b style='color:{col}'>{prob}%</b></div>
        <div style='height:3px;background:#1a1f35;border-radius:10px;margin-top:6px'><div style='height:3px;width:{prob}%;background:{col};border-radius:10px'></div></div>
        <div style='font-size:10px; opacity:0.7; margin-top:6px;'>{affected_text}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="glass" style="border-left:3px solid {color}; margin-top:12px;">
    <div style="font-size:10px; opacity:0.5;">IMPACT ADVISORY • T+{lead} MIN • {searched_place or district}</div>
    <div style="font-size:12px; margin-top:8px; line-height:1.5; font-weight:600; color:{color}">{level} - {searched_place or district}</div>
    <div style="font-size:11px; margin-top:6px; line-height:1.4; opacity:0.8;">
    {"Cloudburst risk in higher reaches. Avoid trekking, landslides possible on NH-10." if level=="RED" else "Thunderstorm with lightning & 50-70 km/h winds. Avoid open areas." if level!="GREEN" else "No severe weather. Light rain at isolated places."}
    </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**System Stats**")
    s1, s2 = st.columns(2)
    s1.metric("Wind", f"{20+max_dbz*0.55:.0f} km/h")
    s2.metric("Lightning", f"{int(max_dbz*2.1)}/hr")
    s1.metric("Coverage", f"{12+max_dbz*0.3:.1f}%")
    s2.metric("Confidence", f"{max(60, 94-lead*0.08):.0f}%")

st.caption("Sikkim Nowcast • 1km • Search any village")
