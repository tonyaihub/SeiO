def post_to_telegram(self, text, media_path=None):
    """Публикация в Telegram канал"""
    bot_token = get_setting("telegram_bot_token")
    channel_id = get_setting("telegram_channel_id") # Например @my_channel
    
    if not bot_token or not channel_id:
        return "❌ Telegram: Нет токена или ID канала."

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": channel_id, "text": text, "parse_mode": "Markdown"}
    
    try:
        if media_path:
            # Отправка фото
            url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            with open(media_path, "rb") as f:
                files = {"photo": f}
                resp = requests.post(url, data={"chat_id": channel_id, "caption": text}, files=files)
        else:
            # Только текст
            resp = requests.post(url, data=data)
            
        if resp.status_code == 200:
            return "✅ Telegram: Опубликовано!"
        else:
            return f"❌ Telegram Error: {resp.text}"
    except Exception as e:
        return f"❌ Telegram Exception: {str(e)}"
