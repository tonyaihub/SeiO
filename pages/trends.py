import streamlit as st
from pytrends.request import TrendReq
import pandas as pd

st.title("🚀 Тренды в реальном времени")

try:
    pytrends = TrendReq(hl='en-US', tz=360)
    st.subheader("🔥 Google Trends (Daily)")
    
    # Получаем тренды для демонстрации
    trending_searches_df = pytrends.trending_searches(pn='united_states')
    st.dataframe(trending_searches_df.head(10), use_container_width=True)
    
    st.subheader("Анализ интереса по ключевому слову")
    kw = st.text_input("Введите тему для анализа", "AI Tools")
    if kw:
        pytrends.build_payload([kw], timeframe='today 12-m')
        interest_over_time_df = pytrends.interest_over_time()
        st.line_chart(interest_over_time_df[kw])
        
        if st.button(f"Создать контент про '{kw}'"):
            st.switch_page("pages/2_✨_Generator.py")
            
except Exception as e:
    st.error(f"Не удалось загрузить тренды (Google API limitation): {e}")
    st.info("Попробуйте позже или используйте VPN.")
