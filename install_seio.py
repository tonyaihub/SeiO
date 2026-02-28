import os

# Структура проекта и содержимое файлов
project_structure = {
    "SeiO/requirements.txt": """streamlit
pandas
sqlalchemy
openai
python-dotenv
apscheduler
moviepy
pytrends
plotly
matplotlib
reportlab
tweepy
facebook-sdk
requests
duckduckgo-search
beautifulsoup4
fake-useragent
textstat
nltk
deepl
""",
    "SeiO/.env": """# Rename to .env and fill in your keys
OPENAI_API_KEY=
ELEVENLABS_API_KEY=
HEYGEN_API_KEY=
RUNWAY_API_KEY=
DEEPL_API_KEY=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHANNEL_ID=
""",
    "SeiO/app.py": """import streamlit as st
import pandas as pd
from modules.database import get_plan
from modules.localization import t

st.set_page_config(page_title="SeiO AI", page_icon="🧿", layout="wide")

# Init Language
if 'language' not in st.session_state:
    st.session_state['language'] = 'ua'

st.markdown(\"\"\"
<style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    .metric-card { background-color: #262730; padding: 20px; border-radius: 10px; }
</style>
\"\"\", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🌐 Language")
    selected_lang = st.selectbox(
        "Choose / Оберіть", 
        ('ua', 'en', 'ru'), 
        format_func=lambda x: "🇺🇦 Українська" if x == 'ua' else ("🇬🇧 English" if x == 'en' else "🇷🇺 Русский"),
        index=0
    )
    if st.session_state['language'] != selected_lang:
        st.session_state['language'] = selected_lang
        st.rerun()
    st.info(f"SeiO v2.0 (2026 Edition) | {selected_lang.upper()}")

# --- MAIN ---
st.title(t("title"))

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric(t("menu_planner"), "12")
with col2: st.metric("Published", "28")
with col3: st.metric("Traffic", "+14%")
with col4: st.metric("Engagement", "4.8%")

st.subheader("📅 Activity")
df = get_plan()
if not df.empty:
    st.dataframe(df.head(5), use_container_width=True)
else:
    st.info("No active plans.")
""",
    "SeiO/modules/__init__.py": "",
    "SeiO/modules/database.py": """import sqlite3
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

Base = declarative_base()
engine = create_engine('sqlite:///seio_db.sqlite', connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)
session = Session()

class ContentPlan(Base):
    __tablename__ = 'content_plan'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.now)
    topic = Column(String)
    platform = Column(String)
    status = Column(String)
    content_text = Column(Text)
    media_path = Column(String)

class Settings(Base):
    __tablename__ = 'settings'
    key = Column(String, primary_key=True)
    value = Column(String)

Base.metadata.create_all(engine)

def add_plan(date, topic, platform):
    new_post = ContentPlan(date=date, topic=topic, platform=platform, status="Planned")
    session.add(new_post)
    session.commit()

def get_plan():
    return pd.read_sql(session.query(ContentPlan).statement, session.bind)

def save_setting(key, value):
    setting = session.query(Settings).filter_by(key=key).first()
    if setting:
        setting.value = value
    else:
        setting = Settings(key=key, value=value)
        session.add(setting)
    session.commit()

def get_setting(key):
    setting = session.query(Settings).filter_by(key=key).first()
    return setting.value if setting else None
""",
    "SeiO/modules/generator.py": """import openai
import os
import json
import streamlit as st
from dotenv import load_dotenv
from modules.database import get_setting

load_dotenv()

def get_api_key():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        key = get_setting("openai_api_key")
    return key

def get_language_instruction():
    lang = st.session_state.get('language', 'ua')
    if lang == 'ua':
        return \"\"\"
        ВАЖЛИВО: Пиши живою, сучасною українською мовою.
        1. Уникай русизмів, кальок та пасивних конструкцій.
        2. Використовуй питомі українські слова ('застосунок', 'наживо', 'спільнота').
        3. Стиль має бути природнім, як у топових українських медіа (The Village Україна, Forbes UA).
        \"\"\"
    elif lang == 'ru':
        return "Write in Russian. Use modern marketing terminology."
    else:
        return "Write in English (US). Use engaging, active voice."

def generate_article(topic, niche, tone):
    api_key = get_api_key()
    if not api_key: return "Error: No API Key"
    
    client = openai.OpenAI(api_key=api_key)
    lang_rules = get_language_instruction()
    
    prompt = f\"\"\"
    {lang_rules}
    Task: Write a comprehensive SEO-optimized article about '{topic}' for the '{niche}' niche.
    Tone: {tone}.
    Structure: H1, Meta Desc, Intro, Key Points (H2, H3), Comparison Table (Markdown), Conclusion.
    Length: ~1000 words. Output: Markdown.
    \"\"\"
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are a professional copywriter."}, 
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def generate_image(prompt):
    api_key = get_api_key()
    if not api_key: return None
    client = openai.OpenAI(api_key=api_key)
    try:
        response = client.images.generate(
            model="dall-e-3", prompt=prompt, size="1024x1024", quality="standard", n=1
        )
        return response.data[0].url
    except: return None

def repurpose_content_ai(source_text, tone):
    api_key = get_api_key()
    if not api_key: return {"error": "No API Key"}
    
    client = openai.OpenAI(api_key=api_key)
    lang_rules = get_language_instruction()
    
    system_prompt = f\"\"\"
    You are an expert SMM Manager. {lang_rules}
    Repurpose source text into 4 distinct formats within a JSON object:
    1. "telegram": Markdown post for Telegram (max 800 chars).
    2. "twitter_thread": Array of strings (tweets).
    3. "facebook": Structured post.
    4. "shorts_script": 30-sec video script.
    \"\"\"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user", "content": f"Source: {source_text}\\nTone: {tone}"}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}
""",
    "SeiO/modules/localization.py": """import streamlit as st

TRANSLATIONS = {
    "en": {
        "title": "SeiO: AI Content Commander",
        "menu_planner": "📅 Planner",
        "menu_generator": "✨ Generator",
        "menu_trends": "🚀 Trends",
        "menu_settings": "⚙️ Settings",
        "gen_title": "✨ AI Content Factory",
        "tab_article": "📝 SEO Article",
        "tab_video": "🎬 Shorts/Reels",
        "tab_img": "🎨 Images",
        "tab_recycle": "♻️ Repurposing",
        "btn_generate": "Generate",
        "topic_label": "Topic / Keyword",
        "niche_label": "Niche",
        "tone_label": "Tone of Voice",
        "serp_toggle": "🕵️ Competitor Analysis (Skyscraper)",
        "pub_header": "📢 Multi-posting",
        "pub_btn": "🚀 Publish",
        "settings_title": "⚙️ Settings & Brand Kit",
        "lang_select": "Interface Language",
        "deepl_label": "DeepL API Key (for pro translation)",
        "error_api": "API Key missing",
        "success_saved": "Settings saved!",
    },
    "ua": {
        "title": "SeiO: AI Центр Керування",
        "menu_planner": "📅 Планувальник",
        "menu_generator": "✨ Генератор",
        "menu_trends": "🚀 Тренди",
        "menu_settings": "⚙️ Налаштування",
        "gen_title": "✨ Фабрика Контенту",
        "tab_article": "📝 SEO Стаття",
        "tab_video": "🎬 Відео (Shorts)",
        "tab_img": "🎨 Зображення",
        "tab_recycle": "♻️ Переробка (Recycle)",
        "btn_generate": "Згенерувати",
        "topic_label": "Тема / Ключове слово",
        "niche_label": "Ніша",
        "tone_label": "Тон голосу",
        "serp_toggle": "🕵️ Аналіз конкурентів (Skyscraper)",
        "pub_header": "📢 Мульти-постинг",
        "pub_btn": "🚀 Опублікувати",
        "settings_title": "⚙️ Налаштування та Бренд",
        "lang_select": "Мова інтерфейсу",
        "deepl_label": "DeepL API Key (для ідеального перекладу)",
        "error_api": "Немає ключа API",
        "success_saved": "Налаштування збережено!",
    },
    "ru": {
        "title": "SeiO: AI Центр Управления",
        "menu_planner": "📅 Планировщик",
        "menu_generator": "✨ Генератор",
        "menu_trends": "🚀 Тренды",
        "menu_settings": "⚙️ Настройки",
        "gen_title": "✨ Фабрика Контента",
        "tab_article": "📝 SEO Статья",
        "tab_video": "🎬 Видео (Shorts)",
        "tab_img": "🎨 Изображения",
        "tab_recycle": "♻️ Ресайклинг",
        "btn_generate": "Сгенерировать",
        "topic_label": "Тема / Ключове слово",
        "niche_label": "Ниша",
        "tone_label": "Тон голосу",
        "serp_toggle": "🕵️ Анализ конкурентів (Skyscraper)",
        "pub_header": "📢 Мульти-постинг",
        "pub_btn": "🚀 Опубликовать",
        "settings_title": "⚙️ Настройки и Бренд",
        "lang_select": "Язык интерфейса",
        "deepl_label": "DeepL API Key (для перевода)",
        "error_api": "Нет ключа API",
        "success_saved": "Настройки сохранены!",
    }
}

def t(key):
    lang = st.session_state.get('language', 'ua')
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)
""",
    "SeiO/modules/seo_analyzer.py": """from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import openai
from modules.database import get_setting
import streamlit as st

def search_competitors(query, max_results=3):
    results = []
    try:
        with DDGS() as ddgs:
            # Region ua-uk for Ukraine priority
            ddgs_gen = ddgs.text(query, region='wt-wt', safesearch='off', timelimit='y', max_results=max_results)
            for r in ddgs_gen:
                results.append({"title": r['title'], "href": r['href'], "body": r['body']})
    except Exception as e:
        print(f"Search Error: {e}")
        return []
    return results

def scrape_article_structure(url):
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200: return f"Error: Status {response.status_code}"
        soup = BeautifulSoup(response.text, 'html.parser')
        structure = []
        h1 = soup.find('h1')
        if h1: structure.append(f"H1: {h1.get_text(strip=True)}")
        for tag in soup.find_all(['h2', 'h3']):
            structure.append(f"{tag.name.upper()}: {tag.get_text(strip=True)}")
        return "\\n".join(structure[:20])
    except Exception as e: return f"Scrape Error: {str(e)}"

def generate_skyscraper_article(topic, niche, tone):
    competitors = search_competitors(f"{topic} {niche} blog", max_results=3)
    if not competitors: return "❌ No competitors found.", ""

    competitor_analysis = ""
    for i, comp in enumerate(competitors):
        structure = scrape_article_structure(comp['href'])
        competitor_analysis += f"\\n--- Competitor {i+1}: {comp['title']} ---\\nURL: {comp['href']}\\nStructure:\\n{structure}\\n"

    api_key = get_setting("openai_api_key")
    client = openai.OpenAI(api_key=api_key)
    
    lang_instr = st.session_state.get('language', 'ua')
    
    system_prompt = f\"\"\"
    You are an Elite SEO Copywriter using the "Skyscraper Technique".
    Target Language: {lang_instr}
    
    Competitors Analysis:
    {competitor_analysis}
    
    Instructions:
    1. Analyze competitors' structures. Identify GAPS.
    2. Create a better article covering everything they missed.
    3. Include "Key Takeaways" table and FAQ.
    4. Output in Markdown. Tone: {tone}.
    \"\"\"

    try:
        response = client.chat.completions.create(
            model="gpt-4o", messages=[{"role": "system", "content": system_prompt}]
        )
        return response.choices[0].message.content, competitor_analysis
    except Exception as e:
        return f"GPT Error: {str(e)}", ""
""",
    "SeiO/modules/seo_checker.py": """import textstat
import re
import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

def calculate_readability(text):
    if not text: return 0
    return textstat.flesch_reading_ease(text)

def calculate_keyword_density(text, keyword):
    if not text or not keyword: return 0.0, 0
    clean_text = re.sub(r'[^\\w\\s]', '', text.lower())
    clean_keyword = keyword.lower().strip()
    words = clean_text.split()
    total_words = len(words)
    if total_words == 0: return 0.0, 0
    keyword_count = clean_text.count(clean_keyword)
    density = (keyword_count / total_words) * 100
    return round(density, 2), keyword_count

def check_metadata_length(title, description):
    t_len = len(title) if title else 0
    d_len = len(description) if description else 0
    title_status = "✅ Perfect" if 50 <= t_len <= 60 else ("⚠️ Short" if t_len < 50 else "❌ Long")
    desc_status = "✅ Perfect" if 150 <= d_len <= 160 else ("⚠️ Short" if d_len < 150 else "❌ Long")
    return {"title_len": t_len, "title_status": title_status, "desc_len": d_len, "desc_status": desc_status}
""",
    "SeiO/modules/social_manager.py": """import tweepy
import facebook
import os
import requests
from modules.database import get_setting

class SocialManager:
    def __init__(self):
        self.tw_consumer_key = get_setting("twitter_consumer_key")
        self.tw_consumer_secret = get_setting("twitter_consumer_secret")
        self.tw_access_token = get_setting("twitter_access_token")
        self.tw_access_secret = get_setting("twitter_access_secret")
        self.fb_token = get_setting("facebook_page_token")
        self.tg_bot_token = get_setting("telegram_bot_token")
        self.tg_channel_id = get_setting("telegram_channel_id")

    def post_to_twitter(self, text, media_path=None):
        try:
            if not self.tw_consumer_key: return "❌ Twitter: No keys."
            auth = tweepy.OAuth1UserHandler(self.tw_consumer_key, self.tw_consumer_secret, self.tw_access_token, self.tw_access_secret)
            api = tweepy.API(auth)
            client = tweepy.Client(consumer_key=self.tw_consumer_key, consumer_secret=self.tw_consumer_secret, access_token=self.tw_access_token, access_token_secret=self.tw_access_secret)
            
            media_id = None
            if media_path and os.path.exists(media_path):
                media = api.media_upload(filename=media_path)
                media_id = media.media_id
            
            if media_id: client.create_tweet(text=text, media_ids=[media_id])
            else: client.create_tweet(text=text)
            return "✅ Twitter: Published!"
        except Exception as e: return f"❌ Twitter Error: {str(e)}"

    def post_to_facebook(self, text, media_path=None):
        try:
            if not self.fb_token: return "❌ Facebook: No token."
            graph = facebook.GraphAPI(access_token=self.fb_token)
            if media_path and os.path.exists(media_path):
                graph.put_photo(image=open(media_path, 'rb'), message=text)
            else:
                graph.put_object(parent_object='me', connection_name='feed', message=text)
            return "✅ Facebook: Published!"
        except Exception as e: return f"❌ Facebook Error: {str(e)}"

    def post_to_telegram(self, text, media_path=None):
        if not self.tg_bot_token or not self.tg_channel_id: return "❌ Telegram: Settings missing."
        try:
            base_url = f"https://api.telegram.org/bot{self.tg_bot_token}"
            if media_path and os.path.exists(media_path):
                ext = os.path.splitext(media_path)[1].lower()
                method = "sendVideo" if ext in ['.mp4', '.mov'] else "sendPhoto"
                key = 'video' if ext in ['.mp4', '.mov'] else 'photo'
                files = {key: open(media_path, 'rb')}
                data = {"chat_id": self.tg_channel_id, "caption": text, "parse_mode": "Markdown"}
                resp = requests.post(f"{base_url}/{method}", data=data, files=files)
            else:
                data = {"chat_id": self.tg_channel_id, "text": text, "parse_mode": "Markdown"}
                resp = requests.post(f"{base_url}/sendMessage", data=data)
            
            if resp.status_code == 200: return "✅ Telegram: Published!"
            else: return f"❌ Telegram API Error: {resp.text}"
        except Exception as e: return f"❌ Telegram Conn Error: {str(e)}"

def publish_content(platforms, text, media_path=None):
    manager = SocialManager()
    results = []
    if "Telegram" in platforms: results.append(manager.post_to_telegram(text, media_path))
    if "X (Twitter)" in platforms: results.append(manager.post_to_twitter(text, media_path))
    if "Facebook" in platforms: results.append(manager.post_to_facebook(text, media_path))
    return results
""",
    "SeiO/modules/translator.py": """import deepl
from modules.database import get_setting

def translate_with_deepl(text, target_lang="UK"):
    api_key = get_setting("deepl_api_key")
    if not api_key: return {"error": "❌ DeepL API Key not set"}
    try:
        translator = deepl.Translator(api_key)
        result = translator.translate_text(text, target_lang=target_lang)
        return result.text
    except Exception as e: return f"DeepL Error: {str(e)}"
""",
    "SeiO/modules/video_engine.py": """import time
import requests
from modules.database import get_setting

class VideoAI:
    def __init__(self):
        self.heygen_key = get_setting("heygen_api_key")
        self.runway_key = get_setting("runway_api_key")

    def generate_heygen_avatar(self, script, avatar_id="default", voice_id="en-US-JennyNeural"):
        if not self.heygen_key: return {"error": "❌ No HeyGen Key"}
        url = "https://api.heygen.com/v2/video/generate"
        headers = {"X-Api-Key": self.heygen_key, "Content-Type": "application/json"}
        real_avatar = avatar_id if avatar_id != "default" else "Daisy-4e3a46"
        payload = {
            "video_inputs": [{"character": {"type": "avatar", "avatar_id": real_avatar}, 
                              "voice": {"type": "text", "input_text": script, "voice_id": voice_id}}],
            "dimension": {"width": 1080, "height": 1920}
        }
        try:
            resp = requests.post(url, headers=headers, json=payload)
            if resp.status_code != 200: return {"error": resp.text}
            video_id = resp.json().get("data", {}).get("video_id")
            return self._poll_heygen(video_id, headers)
        except Exception as e: return {"error": str(e)}

    def _poll_heygen(self, video_id, headers):
        for _ in range(60):
            time.sleep(5)
            resp = requests.get(f"https://api.heygen.com/v1/video_status.get?video_id={video_id}", headers=headers)
            status = resp.json().get("data", {}).get("status")
            if status == "completed": return {"url": resp.json()["data"]["video_url"]}
            if status == "failed": return {"error": "HeyGen Failed"}
        return {"error": "Timeout"}

    def generate_runway_broll(self, prompt):
        if not self.runway_key: return {"error": "❌ No Runway Key"}
        time.sleep(3) # Mock
        return {"error": "⚠️ Runway API Beta: Enterprise only."}

def generate_script_for_video(topic):
    return f"🔥 Hook: {topic} is crazy!\\n🎥 Value: Here is why...\\n🚀 CTA: Follow for more!"

def create_short_video(topic, style):
    time.sleep(2)
    return "MoviePy: Video rendered locally."
""",
    "SeiO/modules/trends.py": """# Trends Logic
from pytrends.request import TrendReq
def get_trends():
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        return pytrends.trending_searches(pn='united_states').head(10)
    except: return None
""",
    "SeiO/pages/1_📅_Planner.py": """import streamlit as st
from datetime import datetime
from modules.database import add_plan, get_plan
from modules.localization import t

st.title(t("menu_planner"))
col1, col2 = st.columns([1, 2])
with col1:
    st.subheader("Add Task")
    topic = st.text_input(t("topic_label"))
    platform = st.multiselect("Platforms", ["Telegram", "Instagram", "TikTok", "YouTube", "X"])
    date = st.date_input("Date")
    if st.button("Add"):
        for p in platform: add_plan(datetime.combine(date, datetime.min.time()), topic, p)
        st.success("Planned!")
        st.rerun()

with col2:
    st.subheader("Calendar")
    df = get_plan()
    if not df.empty:
        st.data_editor(df[['date', 'topic', 'platform', 'status']], use_container_width=True)
""",
    "SeiO/pages/2_✨_Generator.py": """import streamlit as st
import os
import json
from modules.localization import t
from modules.generator import generate_article, generate_image, repurpose_content_ai
from modules.seo_analyzer import generate_skyscraper_article
from modules.seo_checker import calculate_readability, calculate_keyword_density, check_metadata_length
from modules.video_engine import VideoAI, create_short_video, generate_script_for_video
from modules.translator import translate_with_deepl
from modules.database import get_setting
from modules.social_manager import publish_content

st.title(t("gen_title"))
brand_color = get_setting("brand_color") or "#FF4B4B"
brand_tone = get_setting("brand_tone") or "Professional"

if 'repurposed_data' not in st.session_state: st.session_state['repurposed_data'] = None
if 'current_article' not in st.session_state: st.session_state['current_article'] = ""

tab1, tab2, tab3, tab4 = st.tabs([t("tab_article"), t("tab_video"), t("tab_img"), t("tab_recycle")])

# --- TAB 1: SEO ARTICLE ---
with tab1:
    st.header(t("tab_article"))
    c1, c2 = st.columns([3, 1])
    with c1: topic = st.text_input(t("topic_label"), "AI 2026")
    with c2: niche = st.text_input(t("niche_label"), "Tech")
    
    use_serp = st.toggle(t("serp_toggle"), False)
    use_deepl = st.checkbox("🇬🇧->🇺🇦 DeepL Translate", False)
    
    with st.expander("Meta Settings"):
        meta_title = st.text_input("SEO Title", f"{topic} Guide")
        meta_desc = st.text_area("Meta Desc", f"All about {topic}")

    if st.button(t("btn_generate"), type="primary"):
        with st.spinner("AI Working..."):
            if use_serp:
                art, debug = generate_skyscraper_article(topic, niche, brand_tone)
                with st.expander("Analysis"): st.text(debug)
            else:
                art = generate_article(topic, niche, brand_tone)
            
            if use_deepl:
                art = translate_with_deepl(art)
            
            st.session_state['current_article'] = art

    if st.session_state['current_article']:
        st.divider()
        ce, cm = st.columns([2, 1])
        with ce:
            edited = st.text_area("Editor", st.session_state['current_article'], height=600)
            st.session_state['current_article'] = edited
        with cm:
            st.subheader("📊 SEO Score")
            den, cnt = calculate_keyword_density(edited, topic)
            read = calculate_readability(edited)
            meta = check_metadata_length(meta_title, meta_desc)
            st.metric("Density", f"{den}%", f"{cnt} keywords")
            st.metric("Readability", read)
            st.text(f"Title: {meta['title_status']}")
            st.text(f"Desc: {meta['desc_status']}")

# --- TAB 2: VIDEO ---
with tab2:
    st.header("🎬 Video 2.0")
    mode = st.radio("Mode", ["🧩 Simple", "🗣️ Avatar (HeyGen)", "🎥 Cinematic (Runway)"], horizontal=True)
    v_topic = st.text_input("Prompt / Topic")
    
    if mode.startswith("🧩") and st.button("Render Simple"):
        st.success(create_short_video(v_topic, "Modern"))
        
    elif mode.startswith("🗣️"):
        script = st.text_area("Script", "Hello world!")
        if st.button("Generate Avatar"):
            vai = VideoAI()
            with st.spinner("HeyGen Processing..."):
                res = vai.generate_heygen_avatar(script)
                if "url" in res: st.video(res["url"])
                else: st.error(res["error"])

# --- TAB 3: IMAGE ---
with tab3:
    i_prompt = st.text_input("Image Prompt")
    if st.button("Generate"):
        url = generate_image(f"{i_prompt}, {brand_tone}, {brand_color}")
        if url: st.image(url)

# --- TAB 4: RECYCLE ---
with tab4:
    src = st.text_area("Source Text")
    if st.button("Recycle"):
        with st.spinner("Processing..."):
            st.session_state['repurposed_data'] = repurpose_content_ai(src, brand_tone)
    
    if st.session_state['repurposed_data']:
        data = st.session_state['repurposed_data']
        with st.expander("Telegram Draft", True):
            tg_txt = st.text_area("TG", data.get("telegram", ""))
            if st.button("Post TG"): 
                st.success(publish_content(["Telegram"], tg_txt)[0])

# --- GLOBAL PUBLISH ---
st.divider()
st.header(t("pub_header"))
col_p1, col_p2 = st.columns([2, 1])
with col_p1:
    pt = st.text_area("Post Text", "New content!")
    uf = st.file_uploader("Media", type=['png','jpg','mp4'])
with col_p2:
    plats = st.multiselect("Platforms", ["Telegram", "X (Twitter)", "Facebook"], default=["Telegram"])
    if st.button(t("pub_btn"), type="primary"):
        m_path = None
        if uf:
            if not os.path.exists("assets"): os.makedirs("assets")
            m_path = f"assets/{uf.name}"
            with open(m_path, "wb") as f: f.write(uf.getbuffer())
        
        with st.spinner("Posting..."):
            res = publish_content(plats, pt, m_path)
            for r in res: st.success(r) if "✅" in r else st.error(r)
""",
    "SeiO/pages/3_🚀_Trends.py": """import streamlit as st
from pytrends.request import TrendReq
st.title("🚀 Trends")
try:
    pytrends = TrendReq(hl='en-US')
    st.subheader("🔥 Google Search Trends")
    st.dataframe(pytrends.trending_searches(pn='united_states').head(10))
except: st.error("Google Trends API Rate Limit. Try again later.")
""",
    "SeiO/pages/9_⚙️_Settings.py": """import streamlit as st
from modules.database import save_setting, get_setting
from modules.localization import t

st.title(t("settings_title"))

st.subheader("🌐 DeepL")
d_key = st.text_input("DeepL Key", value=get_setting("deepl_api_key") or "", type="password")
if st.button("Save DeepL"): save_setting("deepl_api_key", d_key)

st.divider()
st.subheader("🔐 AI Keys")
o_key = st.text_input("OpenAI Key", value=get_setting("openai_api_key") or "", type="password")
h_key = st.text_input("HeyGen Key", value=get_setting("heygen_api_key") or "", type="password")
if st.button("Save AI"): 
    save_setting("openai_api_key", o_key)
    save_setting("heygen_api_key", h_key)

st.divider()
st.subheader("✈️ Telegram")
t_tok = st.text_input("Bot Token", value=get_setting("telegram_bot_token") or "", type="password")
t_cid = st.text_input("Channel ID", value=get_setting("telegram_channel_id") or "")
if st.button("Save TG"): 
    save_setting("telegram_bot_token", t_tok)
    save_setting("telegram_channel_id", t_cid)

st.divider()
st.subheader("🎨 Brand Kit")
bc = st.color_picker("Color", get_setting("brand_color") or "#000000")
bt = st.text_input("Tone", get_setting("brand_tone") or "Professional")
if st.button("Save Brand"): 
    save_setting("brand_color", bc)
    save_setting("brand_tone", bt)
"""
}

def create_project():
    for path, content in project_structure.items():
        # Create dirs
        dir_name = os.path.dirname(path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        # Write file
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Created: {path}")

    print("\\n✅ SUCCESS! SeiO Project created.")
    print("👉 1. cd SeiO")
    print("👉 2. pip install -r requirements.txt")
    print("👉 3. streamlit run app.py")

if __name__ == "__main__":
    create_project()
