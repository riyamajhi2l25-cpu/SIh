def get_alert_text(hazard, lead_min, lang="English"):
    templates={
        "English": f"ALERT ({lead_min} min): {hazard} predicted near your location. Avoid open areas, stay indoors. - IMD/MoES",
        "Hindi": f"चेतावनी ({lead_min} मिनट): {hazard} की संभावना। खुले में न जाएं, सुरक्षित रहें। - IMD/MoES",
        "Bengali": f"সতর্কতা ({lead_min} মিনিট): {hazard} এর সম্ভাবনা। নিরাপদে থাকুন। - IMD/MoES",
        "Nepali": f"चेतावनी ({lead_min} मिनेट): {hazard} को सम्भावना। सुरक्षित रहनुहोस्। - IMD/MoES",
        "Tamil": f"எச்சரிக்கை ({lead_min} நிமிடம்): {hazard} கணிக்கப்பட்டுள்ளது। - IMD/MoES"
    }
    return templates.get(lang, templates["English"])
