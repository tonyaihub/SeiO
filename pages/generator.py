import streamlit as st
from modules.generator import generate_article, generate_image
from modules.video_engine import generate_script_for_video, create_short_video
from modules.database import get_setting

st.title("✨ AI Content Factory")

# Brand Kit Loader
brand_color = get_setting("brand_color") or "#FF4B4B"
brand_tone = get_setting("brand_tone") or "Professional & Friendly"

tab1, tab2, tab3 = st.tabs(["📝 SEO Статья", "🎬 Shorts/Reels", "🎨 Изображения"])

with tab1:
    st.header("Генерация SEO-статьи")
    topic = st.text_input("Тема статьи", "Как использовать AI в 2026 году")
    niche = st.text_input("Ниша", "Marketing")
    
    if st.button("Сгенерировать статью"):
        with st.spinner("AI пишет статью, анализирует ключи..."):
            article = generate_article(topic, niche, brand_tone)
            st.markdown(article)
            st.download_button("Скачать Markdown", article, "article.md")

with tab2:
    st.header("Генератор Видео (Shorts/Reels/TikTok)")
    v_topic = st.text_input("Тема видео")
    
    if st.button("1. Создать сценарий"):
        script = generate_script_for_video(v_topic)
        st.text_area("Сценарий", script, height=200)
    
    if st.button("2. Сгенерировать Видео (Render)"):
        with st.spinner("Рендеринг видео (ElevenLabs TTS + Stock)..."):
            # Здесь вызов тяжелой функции
            res = create_short_video(v_topic, "Modern")
            st.success(res)
            # st.video(res) # Если бы файл реально создавался

with tab3:
    st.header("AI Изображения (DALL·E 3)")
    img_prompt = st.text_input("Описание картинки")
    if st.button("Создать"):
        with st.spinner("Рисуем..."):
            url = generate_image(f"{img_prompt}, style: {brand_tone}, primary color: {brand_color}")
            if url:
                st.image(url)
