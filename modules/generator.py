
import openai
import os
import json
from dotenv import load_dotenv
from modules.database import get_setting
import streamlit as st # Для доступа к выбранному языку

load_dotenv()

def get_api_key():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        key = get_setting("openai_api_key")
    return key

def get_language_instruction():
    """Возвращает системный промпт для выбранного языка"""
    lang = st.session_state.get('language', 'ua')
    
    if lang == 'ua':
        return """
        ВАЖЛИВО: Пиши живою, сучасною українською мовою.
        1. Уникай русизмів, кальок та пасивних конструкцій.
        2. Використовуй питомі українські слова (наприклад: 'застосунок' замість 'додаток', 'листування' замість 'переписки').
        3. Звертання до читача: на 'Ти' або 'Ви' залежно від тону, але послідовно.
        4. Стиль має бути природнім, як у топових українських медіа (The Village Україна, Forbes UA).
        """
    elif lang == 'ru':
        return "Write in Russian. Use modern marketing terminology."
    else:
        return "Write in English (US). Use engaging, active voice."

def generate_article(topic, niche, tone):
    api_key = get_api_key()
    if not api_key: return "Error: No API Key"
    
    client = openai.OpenAI(api_key=api_key)
    
    # Добавляем языковую инструкцию
    lang_rules = get_language_instruction()
    
    prompt = f"""
    {lang_rules}
    
    Task: Write a comprehensive SEO-optimized article about '{topic}' for the '{niche}' niche.
    Tone: {tone}.
    Structure:
    1. Catchy H1 Title
    2. SEO Meta Description
    3. Introduction with hook
    4. Key points (H2, H3)
    5. Comparison table (Markdown)
    6. Conclusion
    Length: ~1000 words. Output: Markdown.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are a professional copywriter."}, 
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# ... (Остальные функции repurpose и image остаются аналогичными, 
# просто добавь {lang_rules} в начало их промптов)
