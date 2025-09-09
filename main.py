# main.py
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import os
import re
import time
import shutil
import math
from progress_bar import progress, humanbytes, TimeFormatter
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Получаем данные из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/JayBeeBots")
BOT_USERNAME = os.getenv("BOT_URL", "ytiv_bot")
WORKERS = int(os.getenv("WORKERS", "4"))

# Создаём клиент
app = Client(
    "tiktok_downloader", 
    api_id=API_ID, 
    api_hash=API_HASH, 
    bot_token=BOT_TOKEN,
    workers=WORKERS,
    sleep_threshold=120  # Увеличенный таймаут
)

@app.on_message(filters.command("start"))
async def start(client, message):
    kb = [
        [InlineKeyboardButton("Channel 🛡", url=CHANNEL_URL)]
    ]
    reply_markup = InlineKeyboardMarkup(kb)
    await message.reply_text(
        "Hello there, I am TikTok Downloader Bot.\n"
        "I can download TikTok videos without watermark.\n\n"
        "Developer: @JayBeeBots\n"
        "Language: Python\n"
        "Framework: Pyrogram",
        reply_markup=reply_markup
    )

@app.on_message(filters.command("help"))
async def help(client, message):
    kb = [
        [InlineKeyboardButton("Channel 🛡", url=CHANNEL_URL)]
    ]
    reply_markup = InlineKeyboardMarkup(kb)
    await message.reply_text(
        "Send me a TikTok video link, and I'll download it without watermark!",
        reply_markup=reply_markup
    )

@app.on_message(filters.regex(r"(https?://.*tiktok\.com|https?://.*douyin\.com)"))
async def tiktok_dl(client, message):
    url = re.findall(r"(https?://[^\s]+)", message.text)[0].split("?")[0]
    sent_msg = await message.reply_text("Downloading video to server...")

    try:
        # Извлекаем video_id из URL
        if "/video/" in url:
            video_id = url.split("/video/")[1].split("?")[0]
        elif "/v/" in url:
            video_id = url.split("/v/")[1].split("?")[0]
        else:
            await sent_msg.edit("❌ Не удалось определить ID видео. Проверьте ссылку.")
            return
        
        # Используем улучшенный прямой парсинг с правильными заголовками
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36",
            "Referer": "https://www.tiktok.com/",
            "Cookie": "tt_chain_token=; tt_csrf_token=;",
            "Accept-Language": "en-US,en;q=0.9"
        }
        
        # Пробуем несколько серверов TikTok
        video_urls = [
            f"https://api-h2.tiktokv.com/aweme/v1/play/?video_id={video_id}&ratio=720p&watermark=0",
            f"https://api16-core-c-useast1a.tiktokv.com/aweme/v1/play/?video_id={video_id}&ratio=720p&watermark=0",
            f"https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/play/?video_id={video_id}&ratio=720p&watermark=0"
        ]
        
        video_url = None
        for url in video_urls:
            try:
                response = requests.head(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    video_url = url
                    break
            except Exception as e:
                print(f"Server {url} failed: {str(e)}")
                continue
        
        if not video_url:
            await sent_msg.edit("❌ Не удалось найти видео без водяного знака.")
            return
            
    except Exception as e:
        await sent_msg.edit(f"❌ Ошибка обработки ссылки: {str(e)}")
        return

    file_name = f"{int(time.time())}.mp4"
    folder = str(int(time.time()))
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, file_name)

    try:
        with requests.get(video_url, stream=True, headers=headers, timeout=30) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("content-length", 0))
            downloaded = 0
            with open(file_path, "wb") as f:
                start_time = time.time()
                for chunk in r.iter_content(chunk_size=1024 * 1024):  # 1 MB
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        await progress(downloaded, total_size, sent_msg, start_time, file_name)

        await client.send_video(
            chat_id=message.chat.id,
            video=file_path,
            caption=f"🎬 Video downloaded by @{BOT_USERNAME}",
            supports_streaming=True
        )
        await sent_msg.delete()
    except Exception as e:
        await sent_msg.edit(f"❌ Ошибка при загрузке: {str(e)}")
    finally:
        try:
            shutil.rmtree(folder)
        except:
            pass

# Запуск бота
app.run()
