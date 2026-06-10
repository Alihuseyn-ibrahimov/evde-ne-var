import streamlit as st
import google.generativeai as genai
import urllib.parse

# ====================================================================
# 1. AI MODELİNİN AYARLANMASI
# ====================================================================
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

# Modeli yenidən sizin ilkin versiyaya qaytarırıq:
model = genai.GenerativeModel('gemini-2.5-flash')

# ====================================================================
# 2. VİZUAL DİZAYN
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
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80' viewBox='0 0 80 80'%3E%3Cg fill='none' stroke='%23D4A017' stroke-width='0.6' opacity='0.25'%3E%3Cpolygon points='40,8 47,20 60,20 52,30 56,43 40,36 24,43 28,30 20,20 33,20' /%3E%3Crect x='2' y='2' width='76' height='76' rx='4' /%3E%3C/g%3E%3C/svg%3E");
  background-size: 80px 80px;
}

.hero-block {
  background: linear-gradient(135deg, var(--nar) 0%, #8B1A1A 50%, #5C0E0E 100%);
  border-radius: 20px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 8px 32px rgba(192,57,43,0.35);
  margin-bottom: 1.5rem;
}

.hero-title {
  font-family: 'Cinzel', serif;
  font-size: 2.2rem;
  color: #FFD700;
}

.section-title {
  font-family: 'Cinzel', serif;
  font-size: 1.1rem;
  color: var(--nar);
  font-weight: 600;
  border-bottom: 2px solid var(--krem);
  padding-bottom: 0.4rem;
  margin-top: 1.2rem;
  margin-bottom: 0.8rem;
}

div[data-testid="stForm"] {
  background: var(--işıq);
  border: 2px solid rgba(212,160,23,0.4) !important;
  padding: 2rem !important;
  border-radius: 16px;
}

.recipe-img {
    border-radius: 15px;
    border: 3px solid var(--qizil);
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    margin-bottom: 20px;
}

.allergy-warning {
    background-color: #FDEDEC;
    border-left: 5px solid #E74C3C;
    padding: 10px;
    color: #943126;
    font-size: 0.9rem;
    border-radius: 5px;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# ====================================================================
# 3. KÖMƏKÇİ FUNKSİYALAR
# ====================================================================
def get_image_url(food_name):
    """Yemək adına uyğun olaraq Pollinations.ai vasitəsilə şəkil URL-i yaradır"""
    encoded_name = urllib.parse.quote(f"professional food photography of {food_name}, high resolution, 4k, delicious, plated beautifully")
    return f"https://pollinations.ai/p/{encoded_name}?width=1024&height=1024&nologo=true"

# Session State
if "ai_response" not in st.session_state:
    st.session_state.ai_response = None
if "recipe_title" not in st.session_state:
    st.session_state.recipe_title = None

# Hero
st.markdown('<div class="hero-block"><div class="hero-title">🍳 Evdə Nə Var?</div></div>', unsafe_allow_html=True)

# Rejim
st.markdown('<div class="section-title">⚙️ Rejim seçin</div>', unsafe_allow_html=True)
rejim = st.radio("", ["🍽️ Adi Resept", "💪 İdmançı Rejimi"], horizontal=True, label_visibility="collapsed")

# ====================================================================
# 4. FORM
# ====================================================================
with st.form("master_form"):
    st.markdown('<div class="section-title">🧂 Ərzaqlarınız</div>', unsafe_allow_html=True)
    erzaqlar = st.text_area("erzaq", placeholder="Məs: toyuq, qaymaq, göbələk...", height=100, label_visibility="collapsed")

    # --- YENİ: ALLERGİYA BÖLMƏSİ ---
    st.markdown('<div class="section-title">⚠️ Allergiyalar və Məhdudiyyətlər</div>', unsafe_allow_html=True)
    allergiyalar = st.multiselect(
        "Allergiyanız varmı?",
        ["Süd məhsulları (Laktaza)", "Qoz-fındıq", "Qluten", "Yumurta", "Dəniz məhsulları", "Soya", "Balıq"],
        help="Seçdiyiniz ərzaqlar reseptdən qəti şəkildə çıxarılacaq."
    )
    xususi_allergiya = st.text_input("Digər (məs: bal, çiyələk)", placeholder="Xüsusi allergiya varsa qeyd edin")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">🌍 Mətbəx</div>', unsafe_allow_html=True)
        metbex = st.selectbox("", ["Azərbaycan", "Avropa", "Asiya", "İtaliya", "Dietik"], label_visibility="collapsed")
    with col2:
        st.markdown('<div class="section-title">📝 Dil</div>', unsafe_allow_html=True)
        dil = st.radio("", ["Azərbaycanca", "Русский", "English"], horizontal=True, label_visibility="collapsed")

    if "💪" in rejim:
        st.markdown('<div class="section-title">💪 İdmançı Parametrləri</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        çəki = c1.number_input("Çəki (kq)", 40, 200, 75)
        hədəf = c2.selectbox("Məqsəd", ["Kütlə artımı", "Yağ yandırma", "Güc"])

    submitted = st.form_submit_button("✨ Resepti və Şəkli Hazırla")

# ====================================================================
# 5. AI GENERASİYA
# ====================================================================
if submitted:
    if not erzaqlar.strip():
        st.warning("⚠️ Ərzaqları daxil edin!")
    else:
        with st.spinner("👩‍🍳 Süni İntellekt aşpazınız hazırlayır..."):
            
            allergy_info = ", ".join(allergiyalar) + (f", {xususi_allergiya}" if xususi_allergiya else "")
            
            # Prompt mühəndisliyi
            prompt = f"""
            Sən peşəkar aşpazsan. 
            Ərzaqlar: {erzaqlar}
            Allergiyalar (BUNLARI QƏTİ İSTİFADƏ ETMƏ): {allergy_info}
            Mətbəx: {metbex}
            Rejim: {rejim}
            Dil: {dil}

            Tələblər:
            1. Resepti {dil} dilində yaz.
            2. Ən başda birinci sətirdə 'TITLE: [Yeməyin Adı]' formatında adını yaz.
            3. Allergiyalara uyğun alternativlər təklif et.
            4. İdmançı rejimindədirsə kalori hesabla.
            """

            try:
                response = model.generate_content(prompt)
                full_text = response.text
                
                # Başlığı ayırırıq (Şəkil generasityası üçün)
                if "TITLE:" in full_text:
                    title_part = full_text.split("TITLE:")[1].split("\n")[0].strip()
                    st.session_state.recipe_title = title_part
                
                st.session_state.ai_response = full_text
            except Exception as e:
                st.error(f"Xəta: {e}")

# ====================================================================
# 6. NƏTİCƏNİN GÖSTƏRİLMƏSİ
# ====================================================================
if st.session_state.ai_response:
    # Şəkli göstər
    if st.session_state.recipe_title:
        img_url = get_image_url(st.session_state.recipe_title)
        st.markdown(f'<img src="{img_url}" class="recipe-img" width="100%">', unsafe_allow_html=True)
        st.caption(f"📸 Süni İntellekt tərəfindən generasiya olunmuş vizual: {st.session_state.recipe_title}")

    # Allergik xəbərdarlıq
    if allergiyalar or xususi_allergiya:
        st.markdown(f'<div class="allergy-warning">ℹ️ Bu resept sizin <b>{allergy_info}</b> allergiyanız nəzərə alınaraq hazırlanmışdır.</div>', unsafe_allow_html=True)

    # Resepti göstər
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    st.markdown(st.session_state.ai_response.replace(f"TITLE: {st.session_state.recipe_title}", ""))
    st.markdown('</div>', unsafe_allow_html=True)

    st.download_button("📥 Resepti Yadda Saxla", st.session_state.ai_response, "resept.txt")

# Footer
st.markdown('<div class="footer">Azərbaycan mətbəxi & AI texnologiyası</div>', unsafe_allow_html=True)
