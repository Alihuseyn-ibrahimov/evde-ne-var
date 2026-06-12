import streamlit as st
import google.generativeai as genai
import urllib.parse
import re
import requests
from PIL import Image

# ====================================================================
# 1. AI MODELİNİN AYARLANMASI
# ====================================================================
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash')

# ====================================================================
# 2. VİZUAL DİZAYN (ŞRİFT XƏTASI HƏLL EDİLDİ)
# ====================================================================
st.set_page_config(
    page_title="Evdə Nə Var? — AI Resept Botu",
    page_icon="🍳",
    layout="wide"
)

st.markdown("""
<style>
/* DƏYİŞİKLİK: Cinzel şrifti Playfair Display ilə əvəz olundu */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

:root {
  --esas-fon: #E7EAE0;  /* Gözü dincəldən sakit adaçayı fonu */
  --qutu-fon: #F3F5F0;  /* Kontrastı qoruyan açıq ton */
  --metn-tund: #2B2C28; /* Charcoal boz */
  --metn-aciq: #7A7C75; /* İkincili mətnlər */
  --terrakota: #D36C55; /* Vurğu rəngi */
  --haşiyə: #DDE0D7;    /* Yaşıl tona uyğunlaşdırılmış incə sərhəd */
}

/* Əsas Fon */
.stApp {
  background-color: var(--esas-fon);
  font-family: 'Inter', sans-serif;
  background-image: none;
}

/* Minimalist Başlıq (Hero Block) */
.hero-block {
  background: var(--qutu-fon);
  border-radius: 16px;
  padding: 2.5rem;
  text-align: center;
  border: 1px solid var(--haşiyə);
  box-shadow: 0 10px 30px rgba(0,0,0,0.02);
  margin-bottom: 2rem;
}

.hero-title {
  /* DƏYİŞİKLİK: Yeni şrift bura tətbiq olundu */
  font-family: 'Playfair Display', serif;
  font-size: 2.4rem;
  color: var(--metn-tund);
  letter-spacing: -0.5px;
  font-weight: 700;
}

.hero-subtitle {
  color: var(--terrakota);
  font-size: 1rem;
  margin-top: 0.5rem;
  font-weight: 500;
  font-family: 'Inter', sans-serif;
}

/* Bölmə Başlıqları */
.section-title {
  /* DƏYİŞİKLİK: Yeni şrift bura tətbiq olundu */
  font-family: 'Playfair Display', serif;
  font-size: 1.3rem;
  color: var(--metn-tund);
  font-weight: 600;
  border-bottom: 1px solid var(--haşiyə);
  padding-bottom: 0.4rem;
  margin-top: 1.2rem;
  margin-bottom: 0.8rem;
}

/* Forma Qutusu */
div[data-testid="stForm"] {
  background: var(--qutu-fon) !important;
  border: 1px solid var(--haşiyə) !important;
  padding: 2.5rem !important;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.02) !important;
}

/* Yumşaq Kölgəli Şəkillər */
div[data-testid="stImage"] img {
    border-radius: 12px !important;
    border: 1px solid var(--haşiyə) !important;
    box-shadow: 0 12px 32px rgba(0,0,0,0.04) !important;
    margin-bottom: 20px;
}

/* Allergik Xəbərdarlıq (Daha Zərif) */
.allergy-warning {
    background-color: rgba(211, 108, 85, 0.05);
    border-left: 4px solid var(--terrakota);
    padding: 12px 16px;
    color: var(--terrakota);
    font-size: 0.95rem;
    border-radius: 4px 8px 8px 4px;
    margin-bottom: 15px;
}

/* Minimalist və Zövqlü Təsdiq Düyməsi */
div[data-testid="stFormSubmitButton"] button {
    background-color: var(--metn-tund) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.3s ease;
    padding: 0.5rem 1rem !important;
}
div[data-testid="stFormSubmitButton"] button:hover {
    background-color: var(--terrakota) !important;
    box-shadow: 0 4px 12px rgba(211, 108, 85, 0.2) !important;
}
</style>
""", unsafe_allow_html=True)


# ====================================================================
# 3. KÖMƏKÇİ FUNKSİYALAR
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

    default_image = "https://images.unsplash.com/photo-1495147466023-e6a92040d64a?auto=format&fit=crop&w=1024&q=80"

    try:
        UNSPLASH_API_KEY = st.secrets["UNSPLASH_API_KEY"]
        url = f"https://api.unsplash.com/search/photos?page=1&query={urllib.parse.quote(tehlukesiz_ad + ' food')}&client_id={UNSPLASH_API_KEY}&per_page=1&orientation=landscape"

        response = requests.get(url, timeout=3)
        data = response.json()

        if data.get('results') and len(data['results']) > 0:
            return data['results'][0]['urls']['regular']

    except Exception as e:
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
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Hero (İndi kiçik hərflərlə yazsanız da, olduğu kimi görünəcək və ə hərfi problem yaratmayacaq)
st.markdown('<div class="hero-block"><div class="hero-title">🍳 Evdə Nə Var?- ərzaqını yaz, mükəmməl resept verək</div><div class="hero-subtitle">Şef Əlihüseynin mətbəx sirləri</div></div>', unsafe_allow_html=True)

# Rejim
st.markdown('<div class="section-title">⚙️ Rejim seçin</div>', unsafe_allow_html=True)
rejim = st.radio("", ["🍽️ Adi Resept", "💪 İdmançı Rejimi", "👶 Uşaq Rejimi (1-2 yaş)", "🥗 Veqan/Vegetarian"], horizontal=True, label_visibility="collapsed")

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

    if "👶" in rejim:
        st.markdown('<div class="section-title">👶 Uşaq (1-2 yaş) Parametrləri</div>', unsafe_allow_html=True)
        st.info("💡 Sistem daxil etdiyiniz ərzaqları xüsusi analiz edəcək: Hansı qidaların 1-2 yaşlı uşaqlar üçün uyğun olduğu, boğulma və ya allergiya riski barədə şefin peşəkar tövsiyələrini görəcəksiniz.")

    if "🥗" in rejim:
        st.markdown('<div class="section-title">🥗 Veqan/Vegetarian Parametrləri</div>', unsafe_allow_html=True)
        st.info("💡 Sistem daxil etdiyiniz ərzaqları xüsusi analiz edəcək: Sizin üçün həm 100% veqan (heç bir heyvan mənşəli qida olmadan), həm də vegetarian (ət olmadan, lakin süd/yumurta ola bilən) iki fərqli resept və tövsiyə təqdim ediləcək.")

    submitted = st.form_submit_button("✨ Resepti və Şəkli Hazırla")

# ====================================================================
# 5. AI GENERASİYA
# ====================================================================
if submitted:
    if not erzaqlar.strip() and not cekilen_sekil:
        st.warning("⚠️ Zəhmət olmasa, ərzaqları yazın və ya şəklini çəkin!")
    else:
        st.session_state.user_image = cekilen_sekil
        st.session_state.chat_history = []

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
            5. Əgər 'Uşaq Rejimi (1-2 yaş)' seçilibsə: Daxil edilən ərzaqların 1-2 yaşlı uşaqlara uyğunluğunu analiz et. Təhlükəli (boğulma riski, çətin həzm olunan) ərzaqlar barədə valideyni xəbərdar et və onları reseptdən xaric et. Yalnız bu yaşa uyğun, sağlam, yumşaq qida resepti və tövsiyələri ver.
            6. Əgər 'Veqan/Vegetarian' seçilibsə: Veqan və vegetarian qidalanmanın fərqli anlayışlar olduğunu mütləq nəzərə al. Daxil edilən ərzaqlarla eyni anda HƏM 100% Veqan (heç bir heyvan mənşəli məhsul, süd, yumurta, bal olmayan) üçün ayrıca resept və tövsiyə yaz, HƏM DƏ Vegetarian (ət xaric, lakin süd/yumurta məhsulları istifadə edilə bilən) üçün ayrıca fərqli resept və tövsiyə yaz. Hər iki qrupun fərqini qoruyaraq mütləq iki fərqli yanaşmanı bir yerdə təqdim et.
            """

            try:
                if cekilen_sekil:
                    img = Image.open(cekilen_sekil)
                    response = model.generate_content([prompt, img])
                else:
                    response = model.generate_content(prompt)

                full_text = response.text
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

    col_img, col_vid = st.columns(2)

    with col_img:
        if st.session_state.recipe_title_eng:
            img_url = get_image_url(st.session_state.recipe_title_eng)
            st.image(img_url)

    with col_vid:
        st.markdown('<div class="section-title">📺 Hazırlanma Videosu</div>', unsafe_allow_html=True)
        st.info("Süni intellektlə canlı video generasiyası çox vaxt apardığı üçün, bu yeməyin addım-addım hazırlanma qaydasını real şeflərdən izləyə bilərsiniz.")

        if st.session_state.recipe_title_eng:
            youtube_query = urllib.parse.quote(f"{st.session_state.recipe_title_eng} recipe step by step")
            youtube_url = f"https://www.youtube.com/results?search_query={youtube_query}"

            st.link_button("▶️ YouTube-da İzlə", youtube_url, use_container_width=True)

    st.markdown("---")

    if allergiyalar or xususi_allergiya:
        allergy_info = ", ".join(allergiyalar) + (f", {xususi_allergiya}" if xususi_allergiya else "")
        st.markdown(
            f'<div class="allergy-warning">ℹ️ Bu resept sizin <b>{allergy_info}</b> allergiyanız nəzərə alınaraq hazırlanmışdır.</div>',
            unsafe_allow_html=True)

    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    text_to_show = st.session_state.ai_response
    text_to_show = re.sub(r'.*TITLE:.*\n?', '', text_to_show).strip()
    st.markdown(text_to_show)
    st.markdown('</div>', unsafe_allow_html=True)

    st.download_button("📥 Resepti Yadda Saxla", st.session_state.ai_response, "resept.txt")

    # ====================================================================
    # 7. CHATBOT BÖLMƏSİ
    # ====================================================================
    st.markdown("---")
    st.markdown('<div class="section-title">💬 Şef ilə Söhbət</div>', unsafe_allow_html=True)
    st.info("💡 Reseptlə bağlı əlavə suallarınız var? Süni intellekt şefimizdən soruşun!")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt_sual := st.chat_input("Sualınızı bura yazın..."):

        st.session_state.chat_history.append({"role": "user", "content": prompt_sual})
        with st.chat_message("user"):
            st.markdown(prompt_sual)

        with st.chat_message("assistant"):
            with st.spinner("Şef düşünür..."):

                chat_context = f"""
                Sən peşəkar və mehriban aşpazsan.
                Sən az öncə istifadəçiyə bu resepti vermisən:
                {st.session_state.ai_response}

                İstifadəçinin bu reseptlə bağlı sənə yeni sualı var: "{prompt_sual}"

                Tələblər:
                1. Yalnız istifadəçinin sualına cavab ver.
                2. Cavabın qısa, dəqiq və aydın olsun.
                3. Cavabı Azərbaycan dilində yaz.
                """

                try:
                    chat_response = model.generate_content(chat_context)
                    st.markdown(chat_response.text)
                    st.session_state.chat_history.append({"role": "assistant", "content": chat_response.text})
                except Exception as e:
                    st.error(f"Xəta yarandı: {e}")

# Footer
st.markdown('<div style="text-align: center; margin-top: 2rem; color: #7A7C75; font-size: 0.9rem;">Azərbaycan Mətbəxi & Süni İntellekt</div>', unsafe_allow_html=True)
