import streamlit as st
import google.generativeai as genai

# ====================================================================
# 1. AI MODELİNİN AYARLANMASI (STABİL VERSİYA TƏNZİMLƏMƏSİ)
# ====================================================================
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

# Xətanın qarşısını almaq üçün rəsmi stabil API versiyasını məcburi təyin edirik
import os
os.environ["STREAMLIT_API_VERSION"] = "v1"

genai.configure(api_key=GOOGLE_API_KEY)

# Ən son və tam stabil işləyən yeni model adını istifadə edirik
model = genai.GenerativeModel('gemini-2.5-flash')

# ====================================================================
# 2. STREAMLIT VİZUAL İNTERFEYSİNİN QURULMASI
# ====================================================================
st.set_page_config(page_title="Evdə Nə Var? - AI Resept Botu", page_icon="🍳", layout="centered")

# Kreativ Başlıq və Dizayn
st.title("🍳 Evdə Nə Var? — Əlihüseynin süni intellekti ilə öyrən")
st.write("Əlinizdə olan qidaları qeyd edin, Süni İntellekt sizə dünya mətbəxlərindən unikal reseptlər hazırlasın!")

# İstifadəçidən giriş məlumatlarının alınması

with st.form("resept_formu"):
    erzaqlar = st.text_input(
        label="Evdə hansı ərzaqlar var? (Məsələn: kartof, toyuq, soğan, pomidor)",
        placeholder="Ərzaqları vergüllə ayıraraq yazın..."
    )

    metbex = st.selectbox(
        label="Hansı istiqamətdə resept istəyirsiniz?",
        options=["Milli Mətbəx (Azərbaycan)", "Avropa Mətbəxi", "Asiya Mətbəxi", "Ümumdünya/Qarışıq Mətbəx"]
    )

    dil = st.radio(
        label="Reseptin yazılma dili / Язык рецепта / Recipe Language:",
        options=["Azərbaycan dili", "Русский", "English"],
        horizontal=True
    )

    # Form daxilindəki rəsmi təsdiq düyməsi
    submit_button = st.form_submit_button("✨ Ən Optimal Resepti Tap")

# Düymə sıxıldıqda icra olunacaq hissə
if submit_button:
    if erzaqlar:
        with st.spinner("Süni İntellekt reseptləri təhlil edir, zəhmət olmasa gözləyin..."):
            prompt = f"Mənə elə bir resept hazırla ki, tərkibində mütləq bu ərzaqlar olsun: {erzaqlar}. İstiqamət: {metbex}. Cavabı yalnız bu dildə yaz: {dil}."
            try:
                response = model.generate_content(prompt)
                st.success("Budur sənin unikal reseptin:")
                st.write(response.text)
            except Exception as e:
                st.error(f"Xəta baş verdi. Bir az sonra yenidən cəhd edin. {e}")
    else:
        st.warning("Zəhmət olmasa, əvvəlcə evdə olan ərzaqları qeyd edin!")