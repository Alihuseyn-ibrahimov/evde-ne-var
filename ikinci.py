import streamlit as st
import google.generativeai as genai
import os

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

/* ── RƏNG PALETİ ── */
:root {
  --nar:     #C0392B;
  --qizil:   #D4A017;
  --yaşıl:   #1A6B3A;
  --fon:     #FDF6EC;
  --tund:    #1C1008;
  --krem:    #F5E6C8;
  --işıq:    #FFF8F0;
}

/* ── ARXA FON ── */
.stApp {
  background-color: var(--fon);
  background-image:
    /* Milli şəbəkə/ornament SVG pattern */
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80' viewBox='0 0 80 80'%3E%3Cg fill='none' stroke='%23D4A017' stroke-width='0.6' opacity='0.25'%3E%3C!-- Mərkəzi səkkizguşəli ulduz --%3E%3Cpolygon points='40,8 47,20 60,20 52,30 56,43 40,36 24,43 28,30 20,20 33,20' /%3E%3C!-- Köşə bəzəkləri --%3E%3Ccircle cx='0' cy='0' r='8' /%3E%3Ccircle cx='80' cy='0' r='8' /%3E%3Ccircle cx='0' cy='80' r='8' /%3E%3Ccircle cx='80' cy='80' r='8' /%3E%3C!-- Kənar xətlər --%3E%3Crect x='2' y='2' width='76' height='76' rx='4' /%3E%3Cline x1='40' y1='2' x2='40' y2='78' /%3E%3Cline x1='2' y1='40' x2='78' y2='40' /%3E%3Cline x1='2' y1='2' x2='78' y2='78' /%3E%3Cline x1='78' y1='2' x2='2' y2='78' /%3E%3C/g%3E%3C/svg%3E");
  background-size: 80px 80px;
  font-family: 'Inter', sans-serif;
}

/* ── BAŞLIQ BLOKU ── */
.hero-block {
  background: linear-gradient(135deg, var(--nar) 0%, #8B1A1A 50%, #5C0E0E 100%);
  border-radius: 20px;
  padding: 2.5rem 2rem 2rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(192,57,43,0.35);
  text-align: center;
}

.hero-block::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60' viewBox='0 0 60 60'%3E%3Cg fill='none' stroke='%23FFD700' stroke-width='0.5' opacity='0.15'%3E%3Cpolygon points='30,5 35,18 49,18 38,27 42,40 30,32 18,40 22,27 11,18 25,18' /%3E%3C/g%3E%3C/svg%3E");
  background-size: 60px 60px;
  pointer-events: none;
}

.hero-title {
  font-family: 'Cinzel', serif;
  font-size: 2.2rem;
  font-weight: 700;
  color: #FFD700;
  text-shadow: 0 2px 8px rgba(0,0,0,0.4);
  margin: 0 0 0.5rem;
  position: relative;
  z-index: 1;
}

.hero-subtitle {
  font-size: 1rem;
  color: rgba(255,248,230,0.9);
  font-weight: 400;
  position: relative;
  z-index: 1;
  margin: 0;
}

.ornament-divider {
  text-align: center;
  font-size: 1.5rem;
  color: var(--qizil);
  letter-spacing: 0.5rem;
  margin: 0.5rem 0 1.5rem;
  opacity: 0.7;
}

/* ── KART KONTEYNERI ── */
.card {
  background: var(--işıq);
  border: 1.5px solid rgba(212,160,23,0.3);
  border-radius: 16px;
  padding: 1.8rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.07);
}

.card-title {
  font-family: 'Cinzel', serif;
  font-size: 1.05rem;
  color: var(--nar);
  font-weight: 600;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border-bottom: 2px solid var(--krem);
  padding-bottom: 0.6rem;
}

/* ── BADGE — rejim ── */
.badge-row {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  margin-top: 0.5rem;
}
.badge {
  padding: 0.3rem 0.9rem;
  border-radius: 50px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}
.badge-resept { background:#FEF3C7; color:#92400E; border:1.5px solid #F59E0B; }
.badge-idmanci { background:#D1FAE5; color:#065F46; border:1.5px solid #10B981; }

/* ── INPUT STİLLƏRİ ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
  background: white !important;
  border: 2px solid rgba(212,160,23,0.4) !important;
  border-radius: 10px !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.95rem !important;
  color: var(--tund) !important;
  padding: 0.7rem 1rem !important;
  transition: border-color 0.2s;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--nar) !important;
  box-shadow: 0 0 0 3px rgba(192,57,43,0.12) !important;
}

/* ── SELECTbox ── */
.stSelectbox > div > div {
  background: white !important;
  border: 2px solid rgba(212,160,23,0.4) !important;
  border-radius: 10px !important;
}

/* ── RADIO ── */
.stRadio > div { gap: 0.8rem; }
.stRadio label {
  background: var(--krem);
  border: 1.5px solid rgba(212,160,23,0.3);
  border-radius: 8px;
  padding: 0.4rem 0.9rem;
  font-size: 0.88rem;
  cursor: pointer;
  transition: all 0.2s;
}
.stRadio label:hover { border-color: var(--nar); }

/* ── DÜYMƏ ── */
.stButton > button, .stFormSubmitButton > button {
  background: linear-gradient(135deg, var(--nar), #8B1A1A) !important;
  color: #FFD700 !important;
  font-family: 'Cinzel', serif !important;
  font-weight: 700 !important;
  font-size: 1rem !important;
  border: none !important;
  border-radius: 12px !important;
  padding: 0.75rem 2rem !important;
  width: 100% !important;
  cursor: pointer !important;
  box-shadow: 0 4px 15px rgba(192,57,43,0.4) !important;
  transition: all 0.2s !important;
  letter-spacing: 0.03em !important;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(192,57,43,0.5) !important;
}

/* ── NƏTİCƏ BLOKU ── */
.result-box {
  background: linear-gradient(135deg, #FFFBF0, #FEF3C7);
  border: 2px solid var(--qizil);
  border-radius: 16px;
  padding: 1.8rem;
  margin-top: 1.5rem;
  box-shadow: 0 4px 20px rgba(212,160,23,0.2);
}

.result-header {
  font-family: 'Cinzel', serif;
  color: var(--yaşıl);
  font-size: 1.15rem;
  font-weight: 700;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* ── KALORİ PANEL ── */
.calorie-bar {
  background: linear-gradient(90deg, var(--yaşıl), #2ECC71);
  border-radius: 12px;
  padding: 1rem 1.5rem;
  margin-bottom: 1rem;
  color: white;
  font-weight: 600;
}

/* ── XƏBƏRDARLIQ ── */
.stWarning { border-radius: 10px !important; }
.stSuccess { border-radius: 10px !important; }
.stError   { border-radius: 10px !important; }

/* ── FOOTER ── */
.footer {
  text-align: center;
  color: rgba(28,16,8,0.35);
  font-size: 0.8rem;
  margin-top: 3rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(212,160,23,0.2);
}

/* Streamlit default padding azalt */
.block-container { padding-top: 1.5rem !important; max-width: 780px !important; }
div[data-testid="stVerticalBlock"] { gap: 0.5rem; }
</style>
""", unsafe_allow_html=True)

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
# 4. REJİM SEÇİMİ
# ====================================================================
st.markdown('<div class="card"><div class="card-title">⚙️ Rejim seçin</div>', unsafe_allow_html=True)
rejim = st.radio(
    label="",
    options=["🍽️ Adi Resept", "💪 İdmançı Rejimi (Kalori + Makro)"],
    horizontal=True,
    label_visibility="collapsed"
)
st.markdown('</div>', unsafe_allow_html=True)

# ====================================================================
# 5. ƏRZAQ + PARAMETRLƏR FORMU
# ====================================================================
with st.form("resept_formu"):
    st.markdown('<div class="card"><div class="card-title">🧂 Ərzaqlarınız</div>', unsafe_allow_html=True)
    erzaqlar = st.text_area(
        label="Evdə hansı ərzaqlar var?",
        placeholder="Məsələn: 200q toyuq döşü, 2 yumurta, kartof, soğan, pomidor, zeytun yağı...\n\nİdmançı rejimində qram yazmağınız tövsiyə olunur.",
        height=110,
        label_visibility="visible"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card"><div class="card-title">🌍 Mətbəx istiqaməti</div>', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card"><div class="card-title">📝 Dil seçin</div>', unsafe_allow_html=True)
        dil = st.radio(
            label="",
            options=["Azərbaycanca", "Русский", "English"],
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # İdmançı rejimi üçün əlavə parametrlər
    if "💪" in rejim:
        st.markdown('<div class="card"><div class="card-title">💪 İdmançı parametrləri</div>', unsafe_allow_html=True)
        col3, col4, col5 = st.columns(3)
        with col3:
            çəki = st.number_input("Çəki (kq)", min_value=40, max_value=200, value=75)
        with col4:
            hədəf = st.selectbox("Məqsəd", ["Kütlə artım", "Yağ yandırma", "Güc saxlama", "Rəqabət hazırlığı"])
        with col5:
            idman_növü = st.selectbox("İdman növü", ["Fitnes/Gym", "Qaçış", "Üzgüçülük", "Futbol", "Digər"])
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        çəki = hədəf = idman_növü = None

    submitted = st.form_submit_button("✨ Resept Hazırla")

# ====================================================================
# 6. AI CAVABI
# ====================================================================
if submitted:
    if not erzaqlar.strip():
        st.warning("⚠️ Zəhmət olmasa əvvəlcə ərzaqları qeyd edin!")
    else:
        with st.spinner("🔮 AI reseptinizi hazırlayır..."):

            # PROMPT QURULMASI
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
[ad]

## ⏱️ Hazırlanma Vaxtı
[dəqiqə]

## 📊 KALORİ VƏ MAKRO CƏDVƏLİ
Hər maddə üçün ayrıca:
| Ərzaq | Miqdar | Kalori | Protein | Karbohidrat | Yağ |
|-------|--------|--------|---------|-------------|-----|
[cədvəl]

**CƏMI: X kalori | Protein: Xq | Karbo: Xq | Yağ: Xq**

## 🎯 İdmançı üçün uyğunluq analizi
- Bu məqsədə ({hədəf}) nə qədər uyğundur?
- Protein hədəfi: {çəki}kq × 1.8-2.2q = {round(çəki*2,0)}-{round(çəki*2.2,0)}q/gün — bu yeməkdən alınan hissə
- Tövsiyə olunan qəbul vaxtı (məşqdən əvvəl/sonra?)

## 🥄 Addım-addım hazırlanma
[nömrəli addımlar]

## 💡 İdmançı üçün əlavə məsləhətlər
[2-3 praktik məsləhət]
"""
            else:
                prompt = f"""
Sən peşəkar aşpaz və qidalanma mütəxəssisisan.

Mövcud ərzaqlar: {erzaqlar}
Mətbəx istiqaməti: {metbex}

Cavabı YALNIZ {dil} dilində ver. Aşağıdakı formatda detallı cavab hazırla:

## 🍽️ Yeməyin Adı
[ad]

## ⏱️ Hazırlanma Vaxtı
[dəqiqə]

## 📊 Kalori məlumatı
Hər maddə üçün:
| Ərzaq | Miqdar | Kalori |
|-------|--------|--------|
[cədvəl]
**Cəmi: ~X kalori (1 porsiya)**

## 🛒 Tam Ərzaq Siyahısı (miqdarlarla)
[siyahı]

## 🥄 Addım-addım hazırlanma
[nömrəli addımlar]

## ✨ Servis etmə məsləhəti
[1-2 cümlə]
"""

            try:
                response = model.generate_content(prompt)

                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.markdown('<div class="result-header">🌟 Sizin üçün hazırlanan resept</div>', unsafe_allow_html=True)
                st.markdown(response.text)
                st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Xəta baş verdi: {e}")

# ====================================================================
# 7. FOOTER
# ====================================================================
st.markdown("""
<div class="ornament-divider" style="margin-top:2.5rem">✦ ◈ ✦ ◈ ✦</div>
<div class="footer">
  🇦🇿 Azərbaycan mətbəxindən ilhamlanaraq hazırlanmışdır &nbsp;·&nbsp; AI ilə qidalanmanı kəşf et
</div>
""", unsafe_allow_html=True)
