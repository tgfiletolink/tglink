import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.link_generator import LinkGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_file(client: Client, message: Message):
    """
    Main handler for processing incoming media files.
    """
    try:
        # 1. Detection
        media_types = ["video", "audio", "document", "photo", "voice", "animation", "sticker", "video_note"]
        file_id = None
        file_name = "media_file"
        
        for m_type in media_types:
            media = getattr(message, m_type, None)
            if media:
                # If photo, it's a list, we take the last (highest resolutions)
                if m_type == "photo":
                    file_id = media.file_id
                    file_name = f"photo_{file_id[:8]}.jpg"
                else:
                    file_id = getattr(media, "file_id", None)
                    file_name = getattr(media, "file_name", f"{m_type}_{file_id[:8]}")
                break

        if not file_id:
            return

        # 2. Inform user
        status_msg = await message.reply_text("Processing your file...")

        # 3. Generate Streaming Link
        # We use our own DOMAIN/PORT and provide context (chat and msg id)
        base = Config.DOMAIN if Config.DOMAIN else f"http://localhost:{Config.PORT}"
        # Ensure DOMAIN has https if it's Railway
        if "railway.app" in base and not base.startswith("http"):
            base = f"https://{base}"
        
        streaming_link = f"{base}/download/{file_id}?chat={message.chat.id}&msg={message.id}"

        # 4. Result
        response_text = (
            "✅ **Link Generated!**\n\n"
            "**Your Direct Download Link (Fast & Large File Support):**\n"
            f"`{streaming_link}`\n\n"
            "🚀 **Supports up to 2GB!** Safe and encrypted."
        )
        await status_msg.edit_text(response_text)

    except Exception as e:
        logger.error(f"Error handling file: {e}")
        await message.reply_text("An error occurred while processing your request.")
