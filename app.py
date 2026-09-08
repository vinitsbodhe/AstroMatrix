import streamlit as st
import swisseph as swe
import matplotlib.pyplot as plt
import datetime
from geopy.geocoders import Nominatim

# ---------------------------------------------------------
# 1. ASTRONOMICAL CONSTANTS & MAPS
# ---------------------------------------------------------
SIGN_RULERS = {
    1: 'Mars',    2: 'Venus',   3: 'Mercury', 4: 'Moon',
    5: 'Sun',     6: 'Mercury', 7: 'Venus',   8: 'Mars',
    9: 'Jupiter', 10: 'Saturn', 11: 'Saturn', 12: 'Jupiter'
}

RASHIS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
          "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# ---------------------------------------------------------
# 2. CORE RAJ YOG CALCULATION & SCORING ENGINE
# ---------------------------------------------------------
def get_coordinates(city_name):
    """Geocoding to get Latitude and Longitude"""
    try:
        geolocator = Nominatim(user_agent="rajyog_app")
        location = geolocator.geocode(city_name)
        return location.latitude, location.longitude
    except:
        return 28.6139, 77.2090  # Default fallback: New Delhi

def calculate_raj_yog_engine(year, month, day, hour_utc, lat, lon):
    # Setup Swiss Ephemeris with Lahiri Ayanamsa (Vedic)
    julian_day = swe.julday(year, month, day, hour_utc)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH

    # Calculate Ascendant / Lagna
    cusps, ascmc = swe.houses_ex(julian_day, lat, lon, b'A', flags)
    asc_deg = ascmc[0]
    lagna_sign_idx = int(asc_deg // 30) + 1  # 1 to 12

    # Map House Lords (1 to 12)
    house_lords = {}
    for h in range(1, 13):
        sign_of_house = ((lagna_sign_idx - 1 + h - 1) % 12) + 1
        house_lords[h] = SIGN_RULERS[sign_of_house]

    # Calculate 7 Major Planets Positions & Degrees
    planets_to_check = {
        'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS,
        'Mercury': swe.MERCURY, 'Jupiter': swe.JUPITER,
        'Venus': swe.VENUS, 'Saturn': swe.SATURN
    }
    
    planet_degrees = {}
    planet_houses = {}
    
    for p_name, p_code in planets_to_check.items():
        pos, _ = swe.calc_ut(julian_day, p_code, flags)
        p_deg = pos[0]
        planet_degrees[p_name] = p_deg
        p_sign_idx = int(p_deg // 30) + 1
        h_num = ((p_sign_idx - lagna_sign_idx) % 12) + 1
        planet_houses[p_name] = h_num

    # Check Combustion (Is planet within 6 degrees of Sun?)
    sun_deg = planet_degrees['Sun']
    combust_planets = set()
    for p_name, p_deg in planet_degrees.items():
        if p_name != 'Sun':
            deg_diff = abs(p_deg - sun_deg) % 360
            if deg_diff > 180:
                deg_diff = 360 - deg_diff
            if deg_diff <= 6.0:
                combust_planets.add(p_name)

    # DETECT RAJ YOGAS AND SCORE THEM
    total_score = 0
    detected_yogas = []
    kendras = [1, 4, 7, 10]
    trikonas = [1, 5, 9]

    # Rule 1: Yogakaraka Planet (Base Score: 35 pts)
    kendra_lords = set(house_lords[k] for k in kendras)
    trikona_lords = set(house_lords[t] for t in trikonas)
    yogakaraka_planets = kendra_lords.intersection(trikona_lords)

    for yk in yogakaraka_planets:
        base_val = 35
        is_combust = yk in combust_planets
        final_val = base_val // 2 if is_combust else base_val
        total_score += final_val
        
        status = " (Weakened by Combustion)" if is_combust else ""
        detected_yogas.append({
            'name': 'Yogakaraka Raj Yog',
            'score': final_val,
            'desc': f"{yk} naturally rules both a Kendra and Trikona house for {RASHIS[lagna_sign_idx-1]} Lagna{status}."
        })

    # Rule 2: Kendra-Trikona Conjunctions
    processed_pairs = set()
    for k_house in kendras:
        for t_house in trikonas:
            k_lord = house_lords[k_house]
            t_lord = house_lords[t_house]

            if k_lord != t_lord and (k_lord, t_lord) not in processed_pairs and (t_lord, k_lord) not in processed_pairs:
                if planet_houses[k_lord] == planet_houses[t_lord]:
                    processed_pairs.add((k_lord, t_lord))
                    
                    # Highest potency for 9th and 10th lords (Dharma-Karma Adhipati)
                    base_val = 40 if (k_house in [9,10] and t_house in [9,10]) else 25
                    
                    if k_lord in combust_planets or t_lord in combust_planets:
                        base_val = int(base_val * 0.6)
                        combust_note = " [Combustion Penalty Applied]"
                    else:
                        combust_note = ""

                    total_score += base_val
                    y_type = "Dharma-Karma Adhipati Raj Yog" if (k_house in [9,10] and t_house in [9,10]) else "Kendra-Trikona Raj Yog"
                    
                    detected_yogas.append({
                        'name': y_type,
                        'score': base_val,
                        'desc': f"{k_lord} (Lord of H{k_house}) and {t_lord} (Lord of H{t_house}) sit together in House {planet_houses[k_lord]}{combust_note}."
                    })

    # Rule 3: Special Yogas (Gajakesari & Budhaditya)
    jup_h = planet_houses['Jupiter']
    moon_h = planet_houses['Moon']
    diff = ((jup_h - moon_h) % 12) + 1
    if diff in [1, 4, 7, 10]:
        total_score += 20
        detected_yogas.append({
            'name': 'Gajakesari Raj Yog',
            'score': 20,
            'desc': 'Jupiter sits in a Kendra house relative to the Moon, conferring wisdom and prosperity.'
        })

    if planet_houses['Sun'] == planet_houses['Mercury']:
        merc_combust = 'Mercury' in combust_planets
        b_score = 8 if merc_combust else 15
        total_score += b_score
        detected_yogas.append({
            'name': 'Budhaditya Yog',
            'score': b_score,
            'desc': f"Sun and Mercury sit together in House {planet_houses['Sun']} (Intellectual prominence)."
        })

    final_raj_yog_score = min(total_score, 100)
    return RASHIS[lagna_sign_idx - 1], planet_houses, lagna_sign_idx, final_raj_yog_score, detected_yogas

# ---------------------------------------------------------
# 3. CHART VISUALIZATION (North Indian Diamond Grid)
# ---------------------------------------------------------
def draw_kundli_chart(lagna_num, planet_positions):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Draw Outer Border & Inner Diamond Lines
    ax.plot([0, 10, 10, 0, 0], [0, 0, 10, 10, 0], 'k-', lw=2)
    ax.plot([0, 10], [10, 0], 'k-', lw=1)
    ax.plot([0, 10], [0, 10], 'k-', lw=1)
    ax.plot([5, 0, 5, 10, 5], [10, 5, 0, 5, 10], 'k-', lw=1)

    house_centers = {
        1: (5, 7.5),   2: (2.5, 8.8), 3: (1.2, 7.5), 4: (2.5, 5),
        5: (1.2, 2.5), 6: (2.5, 1.2), 7: (5, 2.5),   8: (7.5, 1.2),
        9: (8.8, 2.5), 10: (7.5, 5),  11: (8.8, 7.5),12: (7.5, 8.8)
    }

    house_planets = {i: [] for i in range(1, 13)}
    for p_name, h_num in planet_positions.items():
        house_planets[h_num].append(p_name[:2])

    for h_num, (x, y) in house_centers.items():
        rashi_val = ((lagna_num - 1 + h_num - 1) % 12) + 1
        ax.text(x, y + 0.5, str(rashi_val), color="#d9534f", fontsize=10, fontweight='bold', ha='center')
        
        p_text = " ".join(house_planets[h_num])
        if p_text:
            ax.text(x, y - 0.4, p_text, color="#0275d8", fontsize=9, fontweight='bold', ha='center')

    return fig

# ---------------------------------------------------------
# 4. STREAMLIT FRONTEND
# ---------------------------------------------------------
st.set_page_config(page_title="MyNaksh - Raj Yog Intelligence", layout="wide")

st.title("👑 Raj Yog Intelligence Engine")
st.caption("Calculate planetary alignments, birth chart positions, and Raj Yog potency scores.")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("Enter Birth Details")
    name = st.text_input("Full Name", "Rahul Sharma")
    b_date = st.date_input("Birth Date", datetime.date(1995, 7, 15))
    b_time = st.time_input("Birth Time", datetime.time(14, 30))
    city = st.text_input("Birth City", "New Delhi")
    
    calc_btn = st.button("Calculate Raj Yog Score", type="primary", use_container_width=True)

if calc_btn:
    lat, lon = get_coordinates(city)
    utc_hour = b_time.hour + (b_time.minute / 60.0) - 5.5  # IST to UTC
    
    lagna_name, planet_pos, lagna_num, score, yogas = calculate_raj_yog_engine(
        b_date.year, b_date.month, b_date.day, utc_hour, lat, lon
    )

    with col2:
        st.subheader(f"✨ Raj Yog Profile: {name}")
        
        mcol1, mcol2 = st.columns(2)
        mcol1.metric("Ascendant (Lagna)", lagna_name)
        mcol2.metric("Raj Yog Score", f"{score} / 100")
        st.progress(score / 100)

        c_left, c_right = st.columns([1, 1])
        with c_left:
            fig = draw_kundli_chart(lagna_num, planet_pos)
            st.pyplot(fig)
        
        with c_right:
            st.write("**Detected Planetary Combinations:**")
            if yogas:
                for y in yogas:
                    st.success(f"**{y['name']}** (+{y['score']} pts)\n\n_{y['desc']}_")
            else:
                st.info("No major Kendra-Trikona Raj Yogas detected in primary houses.")