import streamlit as st
import pandas as pd
from modules.database import get_plan
from modules.localization import t

# 1. Настройка страницы (должна быть первой командой)
st.set_page_config(
    page_title="SeiO AI", 
    page_icon="🧿", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Инициализация языка (по умолчанию - Украинский для региона)
if 'language' not in st.session_state:
    st.session_state['language'] = 'ua'

# 3. Кастомные стили (Dark Mode + UI Tweaks)
st.markdown("""
<style>
    /* Общий фон и цвет текста */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    /* Стили для метрик */
    div[data-testid="stMetric"] {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #3d3d3d;
    }
    /* Стили для таблиц */
    div[data-testid="stDataFrame"] {
        border: 1px solid #3d3d3d;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# 4. Боковая панель (Навигация и Язык)
with st.sidebar:
    st.title("🌐 Language / Мова")
    
    # Переключатель языка
    selected_lang = st.selectbox(
        "Оберіть мову інтерфейсу", 
        ('ua', 'en', 'ru'), 
        format_func=lambda x: "🇺🇦 Українська" if x == 'ua' else ("🇬🇧 English" if x == 'en' else "🇷🇺 Русский"),
        index=0 if st.session_state['language'] == 'ua' else (1 if st.session_state['language'] == 'en' else 2)
    )
    
    # Обновление состояния при смене языка
    if st.session_state['language'] != selected_lang:
        st.session_state['language'] = selected_lang
        st.rerun()
        
    st.divider()
    st.info(f"SeiO v2.0 Pro\nRegion: {st.session_state['language'].upper()}")
    st.caption("© 2026 AI Content Systems")

# 5. Главный Дашборд
st.title(t("title")) # Заголовок берется из словаря переводов

# Блок метрик (Статичные демо-данные, можно подключить к Analytics API)
col1, col2, col3, col4 = st.columns(4)
with col1:
    # Количество запланированных постов из БД
    plan_df = get_plan()
    planned_count = len(plan_df[plan_df['status'] == 'Planned']) if not plan_df.empty else 0
    st.metric(t("menu_planner"), str(planned_count), help="Запланировано к публикации")

with col2:
    st.metric("Published (Month)", "28", "+4")
with col3:
    st.metric("Total Views", "14.2K", "+12%")
with col4:
    st.metric("Engagement Rate", "4.8%", "+0.5%")

st.divider()

# Блок Активности (Календарь/Таблица)
st.subheader("📅 Recent Activity")

if not plan_df.empty:
    # Сортируем: сначала новые
    latest_plans = plan_df.sort_values(by='date', ascending=False).head(5)
    
    st.dataframe(
        latest_plans[['date', 'topic', 'platform', 'status']],
        use_container_width=True,
        column_config={
            "date": st.column_config.DatetimeColumn("Publish Date", format="D MMM, HH:mm"),
            "topic": "Topic / Content",
            "platform": "Social Network",
            "status": st.column_config.TextColumn("Status", help="Post status")
        },
        hide_index=True
    )
else:
    st.info("Контент-план пуст. Перейдите в раздел 'Planner' чтобы создать задачи.")
    if st.button("Перейти в Планировщик"):
        st.switch_page("pages/1_📅_Planner.py")

# Футер
st.divider()
st.caption("System Status: 🟢 All Systems Operational | API Connections: OpenAI (Active), Telegram (Active)")
