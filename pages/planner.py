import streamlit as st
from datetime import datetime
from modules.database import add_plan, get_plan

st.title("📅 Контент-планировщик")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Добавить задачу")
    topic = st.text_input("Тема / Ключевое слово")
    platform = st.multiselect("Платформы", ["Blog", "Instagram", "TikTok", "YouTube Shorts", "X (Twitter)"])
    date = st.date_input("Дата публикации")
    time = st.time_input("Время")
    
    if st.button("Добавить в план"):
        full_date = datetime.combine(date, time)
        for plat in platform:
            add_plan(full_date, topic, plat)
        st.success(f"Запланировано: {topic}")
        st.rerun()

with col2:
    st.subheader("Календарь публикаций")
    df = get_plan()
    if not df.empty:
        # Simple drag-and-drop replacement: Data Editor
        edited_df = st.data_editor(
            df[['date', 'topic', 'platform', 'status']],
            num_rows="dynamic",
            use_container_width=True
        )
