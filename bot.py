from pyrogram import Client, filters
from config import Config
from handlers.file_handler import handle_file
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
    plugins=dict(root="handlers") # We will register them manually or use plugins
)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "👋 **Welcome to the File Link Bot!**\n\n"
        "Send or forward any media file (Video, Audio, Document, etc.), "
        "and I'll instantly provide a direct Telegram download link for you.\n\n"
        "**Features:**\n"
        "✅ Fast processing\n"
        "✅ Forwarded & Uploaded files\n"
        "✅ No file storage locally\n\n"
        "Give it a try!"
    )

@app.on_message(filters.media)
async def media_handler(client, message):
    await handle_file(client, message)

if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
