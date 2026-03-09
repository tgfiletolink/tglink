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

        # 3. Process
        logger.info(f"Generating link for {file_name} (ID: {file_id})")
        direct_link = await LinkGenerator.get_direct_link(file_id)

        if direct_link:
            # 4. Result
            response_text = (
                "✅ **Link Generated!**\n\n"
                "**Your Direct Download Link:**\n"
                f"`{direct_link}`\n\n"
                "⚠️ **Note:** These links generally work for files under **20MB** due to Telegram Bot API limitations. Links may expire over time."
            )
            await status_msg.edit_text(response_text)
        else:
            await status_msg.edit_text(
                "❌ **Error: Failed to generate link.**\n\n"
                "Possible reasons:\n"
                "1. The file is larger than **20MB** (Bot API limit).\n"
                "2. The file is in a private channel/group I don't have access to.\n"
                "3. Telegram's servers are temporarily slow."
            )

    except Exception as e:
        logger.error(f"Error handling file: {e}")
        await message.reply_text("An error occurred while processing your request.")
