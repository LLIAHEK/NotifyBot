import asyncio
import os 
import json
import logging
from telethon import TelegramClient, events
from dotenv import load_dotenv

#adding logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
TARGET_CHAT = int(os.getenv('Target_Chat'))
REPOST_CHAT = int(os.getenv('Repost_Chat'))
print(TARGET_CHAT)
print(BOT_TOKEN)

def load_keywords():
    try:
        with open("Keywords.json","r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return list(data.keys())
    except FileNotFoundError:
        logger.error("No json file")
    except Exception as e:
        logger.error(f"error when loading Keywords:{e}")
        return []

KEYWORDS = load_keywords()
print(KEYWORDS)

client = TelegramClient('NotifyBotSession', int(API_ID), API_HASH)

@client.on(events.NewMessage(chats=TARGET_CHAT))
async def handler(event):
    if not event.text:
        return
    text_lower = event.raw_text.lower()

    for word in KEYWORDS:
        if word.lower() in text_lower:
            try:
                sender = await event.get_sender()

                first_name = sender.first_name or ""
                last_name = sender.last_name or ""
                username = f"@{sender.username}" if sender.username else "No username"
                user_id = sender.id
                info_header = (
                    f"Founded message with Keyword\n"
                    f"Sender's names: [{first_name} {last_name}](tg://user?id={user_id})\n"
                    f"Login:{username}\n"
                    f"ID: '{user_id}'\n"
                )

#recending message originaly text
                await client.forward_messages(REPOST_CHAT, event.message)

#sending user info

                await client.send_message(REPOST_CHAT,f"{info_header}\n\n{event.text}",link_preview=False)
                logger.info(f"Message resended to:{REPOST_CHAT}")
                break
            except Exception as e:
                logger.error(f"Error when reposting:{e}")

async def main():
    await client.start(bot_token=BOT_TOKEN)
    print(f"Bot already working and listenning chat: {TARGET_CHAT}")
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped from Keyboard")
