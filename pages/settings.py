import streamlit as st
from modules.database import save_setting, get_setting

st.title("⚙️ Настройки и Бренд-кит")

st.subheader("🔐 API Ключи")
st.warning("Ключи сохраняются локально в зашифрованной БД. Не передавайте файл .db третьим лицам.")

openai_key = st.text_input("OpenAI API Key", value=get_setting("openai_api_key") or "", type="password")
elevenlabs_key = st.text_input("ElevenLabs API Key", value=get_setting("elevenlabs_key") or "", type="password")

if st.button("Сохранить ключи"):
    save_setting("openai_api_key", openai_key)
    save_setting("elevenlabs_key", elevenlabs_key)
    st.success("Сохранено!")

st.divider()

st.subheader("🎨 Бренд-кит")
col1, col2 = st.columns(2)
with col1:
    b_color = st.color_picker("Основной цвет бренда", get_setting("brand_color") or "#000000")
with col2:
    b_tone = st.selectbox("Tone of Voice", 
                          ["Professional", "Friendly", "Sarcastic", "Luxurious", "Educational"],
                          index=0)

if st.button("Обновить бренд-кит"):
    save_setting("brand_color", b_color)
    save_setting("brand_tone", b_tone)
    st.success("Бренд-кит обновлен!")
