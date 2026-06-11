import streamlit as st
import google.generativeai as genai
import urllib.parse
import re
import requests  # YENİ: Unsplash-dan ildırım sürətilə şəkil çəkmək üçün
from PIL import Image

# ====================================================================
# 1. AI MODELİNİN AYARLANMASI
# ====================================================================
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

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

/* st.image üçün dizayn (Qızılı Çərçivə) */
div[data-testid="stImage"] img {
    border-radius: 15px !important;
    border: 3px solid var(--qizil) !important;
    box-shadow: 0 10px 25px rgba(0,0,0,0.2) !important;
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
# 3. KÖMƏKÇİ FUNKSİYALAR (YENİLƏNDİ)
# ====================================================================

def herfleri_temizle(metn):
    """ZİREH: Bütün xüsusi simvolları və yad hərfləri silir."""
    if not metn:
        return ""
    
    deyismeler = {
        'ə': 'e', 'Ə': 'E', 'ı': 'i', 'İ': 'I', 'ö': 'o', 'Ö': 'O',
        'ğ': 'g', 'Ğ': 'G', 'ü': 'u', 'Ü': 'U', 'ş': 's', 'Ş': 'S', 'ç': 'c', 'Ç': 'C'
    }
    for az_herf, en_herf in deyismeler.items():
        metn = metn.replace(az_herf, en_herf)
        
    metn = re.sub(r'[^a-zA-Z0-9\s]', '', metn)
    metn = re.sub(r'\s+', ' ', metn).strip()
    
    return metn

def get_image_url(food_name_eng):
    """Yeməyin adına uyğun olaraq Unsplash API-dən ildırım sürətilə real şəkil tapır"""
    tehlukesiz_ad = herfleri_temizle(food_name_eng)
    
    if not tehlukesiz_ad:
        tehlukesiz_ad = "delicious food"
        
    # Standart zəmanət şəkli (Heç nə tapılmasa və ya internet kəsilsə bu açılacaq)
    default_image = "https://images.unsplash.com/photo-1495147466023-e6a92040d64a?auto=format&fit=crop&w=1024&q=80"
        
    try:
        # Streamlit Secrets-dən Unsplash açarını oxuyuruq
        UNSPLASH_API_KEY = st.secrets["UNSPLASH_API_KEY"]
        
        url = f"https://api.unsplash.com/search/photos?page=1&query={urllib.parse.quote(tehlukesiz_ad + ' food')}&client_id={UNSPLASH_API_KEY}&per_page=1&orientation=landscape"
        
        response = requests.get(url, timeout=3) # Maksimum 3 saniyə gözləyir
        data = response.json()
        
        if data.get('results') and len(data['results']) > 0:
            return data['results'][0]['urls']['regular']
            
    except Exception as e:
        # API açarı səhvdirsə və ya yüklənmədisə, qorunma bloku işə düşür
        pass

    return default_image


# Session State
if "ai_response" not in st.session_state:
    st.session_state.ai_response = None
if "recipe_title" not in st.session_state:
    st.session_state.recipe_title = None
if "recipe_title_eng" not in st.session_state: 
    st.session_state.recipe_title_eng = None
if "user_image" not in st.session_state:
    st.session_state.user_image = None

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
    erzaqlar = st.text_area("erzaq", placeholder="Məs: toyuq, qaymaq, göbələk...", height=100,
                            label_visibility="collapsed")

    with st.expander("📷 Ərzaqınızın şəklini yükləyin"):
        cekilen_sekil = st.camera_input("Kamera", label_visibility="collapsed")

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
    if not erzaqlar.strip() and not cekilen_sekil:
        st.warning("⚠️ Zəhmət olmasa, ərzaqları yazın və ya şəklini çəkin!")
    else:
        st.session_state.user_image = cekilen_sekil
        
        with st.spinner("👩‍🍳 Süni İntellekt aşpazınız hazırlayır..."):

            allergy_info = ", ".join(allergiyalar) + (f", {xususi_allergiya}" if xususi_allergiya else "")

            prompt = f"""
            Sən peşəkar aşpazsan. 
            Ərzaqlar: {erzaqlar}
            Allergiyalar (BUNLARI QƏTİ İSTİFADƏ ETMƏ): {allergy_info}
            Mətbəx: {metbex}
            Rejim: {rejim}
            Dil: {dil}

            Tələblər:
            1. Resepti {dil} dilində yaz.
            2. ƏN BAŞDA BİRİNCİ SƏTİRDƏ MÜTLƏQ BU FORMATDA AD YAZ: 
               TITLE: [Yerli dildə ad] | [İngiliscə tərcüməsi]
               NÜMUNƏ: TITLE: Quzu Qovurması | Lamb Stew
               DİQQƏT: "|" işarəsini və İngiliscə tərcüməni YADDAN ÇIXARMA!
            3. Allergiyalara uyğun alternativlər təklif et.
            4. İdmançı rejimindədirsə kalori hesabla.
            """

            try:
                if cekilen_sekil:
                    img = Image.open(cekilen_sekil)
                    response = model.generate_content([prompt, img])
                else:
                    response = model.generate_content(prompt)

                full_text = response.text

                # Markdown ulduzlarını təmizləyirik
                clean_text = full_text.replace("**", "")
                
                if "TITLE:" in clean_text:
                    title_line = clean_text.split("TITLE:")[1].split("\n")[0].strip()
                    if "|" in title_line:
                        parts = title_line.split("|", 1)
                        st.session_state.recipe_title = parts[0].strip()
                        st.session_state.recipe_title_eng = parts[1].strip()
                    else:
                        st.session_state.recipe_title = title_line.strip()
                        st.session_state.recipe_title_eng = title_line.strip()
                else:
                    st.session_state.recipe_title = "Ləziz Yemək"
                    st.session_state.recipe_title_eng = "Delicious Meal"

                st.session_state.ai_response = full_text
            except Exception as e:
                st.error(f"Xəta: {e}")

# ====================================================================
# 6. NƏTİCƏNİN GÖSTƏRİLMƏSİ
# ====================================================================
if st.session_state.ai_response:
    st.markdown("---")
    
    if st.session_state.user_image:
        st.image(st.session_state.user_image, caption="📸 Sizin təqdim etdiyiniz ərzaqlar")
    
    # --- YENİ: UNSPLASH İLƏ İLDIRIM SÜRƏTLİ ŞƏKİL ---
    if st.session_state.recipe_title_eng:
        img_url = get_image_url(st.session_state.recipe_title_eng)
        
        st.image(img_url, caption=f"📸 Unsplash bazasından tapılmış real vizual: {st.session_state.recipe_title}")
    # -----------------------------------------------

    # Allergik xəbərdarlıq
    if allergiyalar or xususi_allergiya:
        allergy_info = ", ".join(allergiyalar) + (f", {xususi_allergiya}" if xususi_allergiya else "")
        st.markdown(
            f'<div class="allergy-warning">ℹ️ Bu resept sizin <b>{allergy_info}</b> allergiyanız nəzərə alınaraq hazırlanmışdır.</div>',
            unsafe_allow_html=True)

    # Resepti göstər
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    
    text_to_show = st.session_state.ai_response
    text_to_show = re.sub(r'.*TITLE:.*\n?', '', text_to_show).strip()
        
    st.markdown(text_to_show)
    st.markdown('</div>', unsafe_allow_html=True)

    st.download_button("📥 Resepti Yadda Saxla", st.session_state.ai_response, "resept.txt")

# Footer
st.markdown('<div class="footer">Azərbaycan mətbəxi & AI texnologiyası</div>', unsafe_allow_html=True)
