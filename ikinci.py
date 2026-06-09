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
st.title("🍳 Evdə Nə Var? — Əlihüseynin süni zəkası ilə öyrən")
st.write("Əlinizdə olan qidaları qeyd edin, Süni İntellekt sizə dünya mətbəxlərindən unikal reseptlər hazırlasın!")

# İstifadəçidən giriş məlumatlarının alınması
erzaqlar = st.text_input("Evdə hansı ərzaqlar var? (Məsələn: kartof, toyuq, soğan, pomidor)",
                         placeholder="Ərzaqları vergüllə ayıraraq yazın...")

# Mətbəx seçimi
metbex = st.selectbox(
    "Hansı istiqamətdə resept istəyirsiniz?",
    ["Milli Mətbəx (Azərbaycan)", "Avropa Mətbəxi", "Asiya Mətbəxi", "Ümumdünya/Qarışıq Mətbəx"]
)

# Dil seçimi
dil = st.radio("Reseptin yazılma dili / Язык рецепта / Recipe Language:", ["Azərbaycan dili", "Русский", "English"],
               horizontal=True)

# ====================================================================
# 3. SÜNİ İNTELLEKTİN GENERASİYA PROSESİ
# ====================================================================
if st.button("✨ Ən Optimal Resepti Tap"):
    if erzaqlar:
        with st.spinner("Süni İntellekt reseptləri təhlil edir, zəhmət olmasa gözləyin..."):
            try:
                # Prompt Engineering: Süni intellektə rol və dəqiq təlimatlar veririk
                prompt = f"""
                Sən peşəkar bir şef-aşpaz və Süni İntellekt köməkçisən. 
                İstifadəçinin əlində yalnız bu ərzaqlar var: {erzaqlar}.
                Səndən istənilən mətbəx növü: {metbex}.

                Tapşırıq:
                1. Bu ərzaqlardan istifadə edərək hazırlana biləcək ən optimal və dadlı yemək reseptini tap.
                2. Cavabı tamamilə bu dildə yaz: {dil}.
                3. Cavabın strukturu belə olsun:
                   - Yeməyin Adı (Mətbəx növünə uyğun kreativ ad)
                   - Lazım olan və istifadə edilən ərzaqların siyahısı
                   - Addım-addım hazırlanma qaydası (Sadə və aydın)
                   - Şefin tövsiyəsi (Kiçik bir dad sirri və ya məsləhət)

                Əgər verilən ərzaqlarla heç bir yemək hazırlamaq mümkün deyilsə, istifadəçiyə nəzakətlə bildirin və əlavə hansı kiçik ərzağı alsa nələr edə biləcəyini təklif edin.
                """

                # AI Modelinə sorğu göndəririk
                response = model.generate_content(prompt)

                # Nəticəni ekranda göstəririk
                st.success("🎉 Reseptiniz Hazırdır!")
                st.markdown("---")
                st.markdown(response.text)
                st.markdown("---")

            except Exception as e:
                st.error(f"Xəta baş verdi. API açarınızı yoxlayın və ya bir az sonra yenidən cəhd edin. {e}")
    else:
        st.warning("Zəhmət olmasa, ən azı bir neçə ərzaq adı daxil edin.")