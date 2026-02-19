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
st.subheader("🐦 X (Twitter) API")
st.markdown("Нужен API v2 с правами `write`.")
tw_cons_key = st.text_input("Consumer Key", value=get_setting("twitter_consumer_key") or "", type="password")
tw_cons_sec = st.text_input("Consumer Secret", value=get_setting("twitter_consumer_secret") or "", type="password")
tw_acc_tok = st.text_input("Access Token", value=get_setting("twitter_access_token") or "", type="password")
tw_acc_sec = st.text_input("Access Token Secret", value=get_setting("twitter_access_secret") or "", type="password")

if st.button("Сохранить Twitter ключи"):
    save_setting("twitter_consumer_key", tw_cons_key)
    save_setting("twitter_consumer_secret", tw_cons_sec)
    save_setting("twitter_access_token", tw_acc_tok)
    save_setting("twitter_access_secret", tw_acc_sec)
    st.success("Ключи Twitter сохранены")

st.divider()
st.subheader("📘 Facebook Graph API")
st.markdown("Нужен `Page Access Token` (не User Token).")
fb_token = st.text_input("Page Access Token", value=get_setting("facebook_page_token") or "", type="password")
fb_page = st.text_input("Page ID", value=get_setting("facebook_page_id") or "")

if st.button("Сохранить Facebook ключи"):
    save_setting("facebook_page_token", fb_token)
    save_setting("facebook_page_id", fb_page)
    st.success("Ключи Facebook сохранены")


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
