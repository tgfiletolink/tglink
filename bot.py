import asyncio
from pyrogram import Client, filters
from config import Config
from handlers.file_handler import handle_file
from utils.stream_server import start_web_server
import logging

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

app = Client(
    "file_link_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="handlers")
)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "👋 **Welcome to the Large File Link Bot!**\n\n"
        "Send or forward any media file (even up to 2GB), "
        "and I'll provide a high-speed direct download link.\n\n"
        "**Features:**\n"
        "✅ Fast streaming processing\n"
        "✅ Supports 2GB+ files\n"
        "✅ No 20MB limitation\n\n"
        "Give it a try!"
    )

@app.on_message(filters.media)
async def media_handler(client, message):
    await handle_file(client, message)

async def main():
    await app.start()
    # Start the streaming server
    await start_web_server(app)
    # Keep the bot running
    await asyncio.Event().wait()

if __name__ == "__main__":
    print("Bot and Stream Server are starting...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
