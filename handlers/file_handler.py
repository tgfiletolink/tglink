import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_file(client, message: Message):
    try:
        # Detection
        media = (
            message.video or message.document or message.audio or 
            message.photo or message.voice or message.animation
        )
        
        if not media:
            return

        file_id = getattr(media, "file_id", None)
        if not file_id:
            return

        status_msg = await message.reply_text("Processing your file...")

        # Domain calculation
        base = Config.DOMAIN
        if not base:
            # Fallback for testing
            base = "localhost:8080"
            
        # Ensure correct protocol
        if not base.startswith("http"):
            base = f"https://{base}"
        
        # Strip trailing slash if any
        base = base.rstrip('/')

        streaming_link = f"{base}/download/{file_id}?chat={message.chat.id}&msg={message.id}"

        response_text = (
            "✅ **Link Generated!**\n\n"
            "**Download Link:**\n"
            f"`{streaming_link}`\n\n"
            "🚀 **Large File Support Active**"
        )
        await status_msg.edit_text(response_text)

    except Exception as e:
        logger.error(f"Handler Error: {e}")
        # Try to inform the user about the specific error for debugging
        await message.reply_text(f"Error: {str(e)}")
