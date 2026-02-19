import streamlit as st
import pandas as pd
from modules.database import get_plan
# Импортируем функцию перевода
from modules.localization import t 

st.set_page_config(page_title="SeiO AI", page_icon="🧿", layout="wide")

# Инициализация языка по умолчанию
if 'language' not in st.session_state:
    st.session_state['language'] = 'ua' # Украина по умолчанию

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    .metric-card { background-color: #262730; padding: 20px; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: Language Switcher ---
with st.sidebar:
    st.title("🌐 Language")
    selected_lang = st.selectbox(
        "Choose / Оберіть", 
        ('ua', 'en', 'ru'), 
        format_func=lambda x: "🇺🇦 Українська" if x == 'ua' else ("🇬🇧 English" if x == 'en' else "🇷🇺 Русский"),
        index=0
    )
    # Обновляем состояние при смене
    if st.session_state['language'] != selected_lang:
        st.session_state['language'] = selected_lang
        st.rerun()
        
    st.info(f"SeiO v1.2 | {selected_lang.upper()}")

# --- MAIN UI (Translated) ---
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
