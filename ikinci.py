import streamlit as st
import google.generativeai as genai

# ====================================================================
# 1. AI MODELİNİN AYARLANMASI
# ====================================================================
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# ====================================================================
# 2. VİZUAL DİZAYN — MİLLİ ORNAMENT + CANLİ RƏNGLƏR
# ====================================================================
st.set_page_config(
    page_title="Evdə Nə Var? — AI Resept Botu",
    page_icon="🍳",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Inter:wght@400;500;600&display=swap');

:root {
  --nar:     #C0392B;
  --qizil:   #D4A017;
  --yaşıl:   #1A6B3A;
  --fon:     #FDF6EC;
  --tund:    #1C1008;
  --krem:    #F5E6C8;
  --işıq:    #FFF8F0;
}

.stApp {
  background-color: var(--fon);
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80' viewBox='0 0 80 80'%3E%3Cg fill='none' stroke='%23D4A017' stroke-width='0.6' opacity='0.25'%3E%3Cpolygon points='40,8 47,20 60,20 52,30 56,43 40,36 24,43 28,30 20,20 33,20' /%3E%3Ccircle cx='0' cy='0' r='8' /%3E%3Ccircle cx='80' cy='0' r='8' /%3E%3Ccircle cx='0' cy='80' r='8' /%3E%3Ccircle cx='80' cy='80' r='8' /%3E%3Crect x='2' y='2' width='76' height='76' rx='4' /%3E%3Cline x1='40' y1='2' x2='40' y2='78' /%3E%3Cline x1='2' y1='40' x2='78' y2='40' /%3E%3Cline x1='2' y1='2' x2='78' y2='78' /%3E%3Cline x1='78' y1='2' x2='2' y2='78' /%3E%3C/g%3E%3C/svg%3E");
  background-size: 80px 80px;
  font-family: 'Inter', sans-serif;
}

.hero-block {
  background: linear-gradient(135deg, var(--nar) 0%, #8B1A1A 50%, #5C0E0E 100%);
  border-radius: 20px;
  padding: 2.5rem 2rem 2rem;
  margin-bottom: 2rem;
  text-align: center;
  box-shadow: 0 8px 32px rgba(192,57,43,0.35);
}

.hero-title {
  font-family: 'Cinzel', serif;
  font-size: 2.2rem;
  font-weight: 700;
  color: #FFD700;
  text-shadow: 0 2px 8px rgba(0,0,0,0.4);
}

.hero-subtitle {
  font-size: 1rem;
  color: rgba(255,248,230,0.9);
}

.ornament-divider {
  text-align: center;
  font-size: 1.5rem;
  color: var(--qizil);
  letter-spacing: 0.5rem;
  margin: 0.5rem 0 1.5rem;
}

/* Kart strukturlarını təmiz Streamlit containerlərinə tətbiq edirik */
div[data-testid="stForm"] {
  background: var(--işıq);
  border: 2px solid rgba(212,160,23,0.4) !important;
  padding: 2rem !important;
  border-radius: 16px;
}

.section-title {
  font-family: 'Cinzel', serif;
  font-size: 1.1rem;
  color: var(--nar);
  font-weight: 600;
  border-bottom: 2px solid var(--krem);
  padding-bottom: 0.4rem;
  margin-top: 1rem;
  margin-bottom: 0.8rem;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
  background: white !important;
  border: 2px solid rgba(212,160,23,0.3) !important;
  border-radius: 10px !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--nar) !important;
}

.stButton > button, .stFormSubmitButton > button {
  background: linear-gradient(135deg, var(--nar), #8B1A1A) !important;
  color: #FFD700 !important;
  font-family: 'Cinzel', serif !important;
  font-weight: 700 !important;
  font-size: 1.1rem !important;
  border-radius: 12px !important;
  box-shadow: 0 4px 15px rgba(192,57,43,0.4) !important;
}

.result-box {
  background: linear-gradient(135deg, #FFFBF0, #FEF3C7);
  border: 2px solid var(--qizil);
  border-radius: 16px;
  padding: 1.8rem;
  margin-top: 1.5rem;
}

.footer {
  text-align: center;
  color: rgba(28,16,8,0.4);
  font-size: 0.8rem;
  margin-top: 3rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(212,160,23,0.2);
}
</style>
""", unsafe_allow_html=True)

if "ai_response" not in st.session_state:
    st.session_state.ai_response = None

# ====================================================================
# 3. BAŞLIQ HERO
# ====================================================================
st.markdown("""
<div class="hero-block">
  <div class="hero-title">🍳 Evdə Nə Var?</div>
  <div class="hero-subtitle">Əlinizdəki ərzaqlardan AI sizə mükəmməl resept və qidalanma planı hazırlayır</div>
</div>
<div class="ornament-divider">✦ ◈ ✦ ◈ ✦</div>
""", unsafe_allow_html=True)

# ====================================================================
# 4. REJİM SEÇİMİ (Formdan kənarda - Reaktivlik üçün)
# ====================================================================
st.markdown('<div class="section-title">⚙️ Rejim seçin</div>', unsafe_allow_html=True)
rejim = st.radio(
    label="",
    options=["🍽️ Adi Resept", "💪 İdmançı Rejimi (Kalori + Makro)"],
    horizontal=True,
    label_visibility="collapsed"
)

# ====================================================================
# 5. VAHİD FORM
# ====================================================================
with st.form("resept_formu_yeni"):
    
    st.markdown('<div class="section-title">🧂 Ərzaqlarınız</div>', unsafe_allow_html=True)
    erzaqlar = st.text_area(
        label="Evdə hansı ərzaqlar var?",
        placeholder="Məsələn: 200q toyuq döşü, 2 yumurta, kartof, soğan...\n\nİdmançı rejimində qram yazmağınız tövsiyə olunur.",
        height=110,
        label_visibility="collapsed"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">🌍 Mətbəx istiqaməti</div>', unsafe_allow_html=True)
        metbex = st.selectbox(
            label="",
            options=[
                "Milli Mətbəx (Azərbaycan)",
                "Avropa Mətbəxi",
                "Asiya Mətbəxi",
                "Yüksək Protein (İdman)",
                "Az Kalorili (Diet)",
                "Ümumdünya/Qarışıq"
            ],
            label_visibility="collapsed"
        )

    with col2:
        st.markdown('<div class="section-title">📝 Dil seçin</div>', unsafe_allow_html=True)
        dil = st.radio(
            label="",
            options=["Azərbaycanca", "Русский", "English"],
            horizontal=True,
            label_visibility="collapsed"
        )

    # İdmançı parametrləri yalnız müvafiq rejim seçildikdə dinamik açılır
    if "💪" in rejim:
        st.markdown('<div class="section-title">💪 İdmançı parametrləri</div>', unsafe_allow_html=True)
        col3, col4, col5 = st.columns(3)
        with col3:
            çəki = st.number_input("Çəki (kq)", min_value=40, max_value=200, value=75)
        with col4:
            hədəf = st.selectbox("Məqsəd", ["Kütlə artımı", "Yağ yandırma", "Güc saxlama", "Rəqabət hazırlığı"])
        with col5:
            idman_növü = st.selectbox("İdman növü", ["Fitnes/Gym", "Qaçış", "Üzgüçülük", "Futbol", "Digər"])

    submitted = st.form_submit_button("✨ Mükəmməl Resepti Hazırla")

# ====================================================================
# 6. AI PROCESİNİN İCRA OLUNMASI
# ====================================================================
if submitted:
    if not erzaqlar.strip():
        st.warning("⚠️ Zəhmət olmasa əvvəlcə ərzaqları qeyd edin!")
    else:
        with st.spinner("🔮 Süni İntellekt reseptinizi və cədvəlinizi hesablayır..."):
            if "💪" in rejim:
                prompt = f"""
Sən elit idman qidalanması mütəxəssisi və peşəkar aşpazsan.
İdmançı məlumatları:
- Çəki: {çəki} kq
- Məqsəd: {hədəf}
- İdman növü: {idman_növü}
Mövcud ərzaqlar: {erzaqlar}
Mətbəx istiqaməti: {metbex}

Cavabı YALNIZ {dil} dilində ver. Aşağıdakı formatda detallı cavab hazırla:
## 🍽️ Yeməyin Adı
## ⏱️ Hazırlanma Vaxtı
## 📊 KALORİ VƏ MAKRO CƏDVƏLİ
| Ərzaq | Miqdar | Kalori | Protein | Karbohidrat | Yağ |
**CƏMI: X kalori | Protein: Xq | Karbo: Xq | Yağ: Xq**
## 🎯 İdmançı üçün uyğunluq analizi
## 🥄 Addım-addım hazırlanma
## 💡 İdmançı üçün əlavə məsləhətlər
"""
            else:
                prompt = f"""
Sən peşəkar aşpaz və qidalanma mütəxəssisisan.
Mövcud ərzaqlar: {erzaqlar}
Mətbəx istiqaməti: {metbex}

Cavabı YALNIZ {dil} dilində ver. Aşağıdakı formatda detallı cavab hazırla:
## 🍽️ Yeməyin Adı
## ⏱️ Hazırlanma Vaxtı
## 📊 Kalori məlumatı
**Cəmi: ~X kalori (1 porsiya)**
## 🛒 Tam Ərzaq Siyahısı (miqdarlarla)
## 🥄 Addım-addım hazırlanma
## ✨ Servis etmə məsləhəti
"""
            try:
                response = model.generate_content(prompt)
                st.session_state.ai_response = response.text
            except Exception as e:
                st.error(f"❌ Xəta baş verdi: {e}")

if st.session_state.ai_response:
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    st.markdown('<div class="result-header">🌟 Sizin üçün hazırlanan resept</div>', unsafe_allow_html=True)
    st.markdown(st.session_state.ai_response)
    st.markdown('</div>', unsafe_allow_html=True)

    st.download_button(
        label="📥 Resepti Mətn Faylı Kimi Yadda Saxla",
        data=st.session_state.ai_response,
        file_name="ai_resept_plani.txt",
        mime="text/plain"
    )

# ====================================================================
# 7. FOOTER
# ====================================================================
st.markdown("""
<div class="ornament-divider" style="margin-top:2.5rem">✦ ◈ ✦ ◈ ✦</div>
<div class="footer">
  🇦🇿 Azərbaycan mətbəxindən ilhamlanaraq hazırlanmışdır &nbsp;·&nbsp; AI ilə qidalanmanı kəşf et
</div>
""", unsafe_allow_html=True)
