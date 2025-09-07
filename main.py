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

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
CHANNEL_URL = os.getenv("CHANNEL_URL")
BOT_USERNAME = os.getenv("BOT_URL")
WORKERS = int(os.getenv("WORKERS", 4))
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

app = Client("tiktok_downloader", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, workers=WORKERS)

@app.on_message(filters.command("start"))
async def start(client, message):
    kb = [
        [InlineKeyboardButton("Channel 🛡", url=CHANNEL_URL),
         InlineKeyboardButton("Repo 🔰", url="https://github.com/TerminalWarlord/TikTok-Downloader-Bot")]
    ]
    reply_markup = InlineKeyboardMarkup(kb)
    await message.reply_text(
        "Hello there, I am TikTok Downloader Bot.\n"
        "I can download TikTok videos without watermark.\n\n"
        "Developer: @JayBeeDev\n"
        "Language: Python\n"
        "Framework: Pyrogram",
        reply_markup=reply_markup
    )

@app.on_message(filters.command("help"))
async def help(client, message):
    kb = [
        [InlineKeyboardButton("Channel 🛡", url=CHANNEL_URL),
         InlineKeyboardButton("Repo 🔰", url="https://github.com/TerminalWarlord/TikTok-Downloader-Bot")]
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

    headers = {
        "x-rapidapi-host": "tiktok-info.p.rapidapi.com",
        "x-rapidapi-key": RAPIDAPI_KEY
    }
    params = {"link": url}

    try:
        response = requests.get("https://tiktok-info.p.rapidapi.com/dl/", params=params, headers=headers).json()
        video_url = response["videoLinks"]["download"]
    except Exception as e:
        await sent_msg.edit(f"❌ Failed to fetch video: {str(e)}")
        return

    file_name = f"{int(time.time())}.mp4"
    folder = str(int(time.time()))
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, file_name)

    try:
        with requests.get(video_url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("content-length", 0))
            downloaded = 0
            with open(file_path, "wb") as f:
                start_time = time.time()
                for chunk in r.iter_content(chunk_size=1024 * 1024):
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
        await sent_msg.edit(f"❌ Error during download: {str(e)}")
    finally:
        try:
            shutil.rmtree(folder)
        except:
            pass

app.run()