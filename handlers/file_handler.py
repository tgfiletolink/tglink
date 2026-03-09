import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from config import Config
from utils.database import db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@Client.on_message(filters.private & filters.media)
async def handle_file(client: Client, message: Message):
    """
    Main handler for processing incoming media files with features.
    """
    user_id = message.from_user.id
    
    try:
        # 1. Force Subscription Check
        if Config.FORCE_SUB_CHANNEL:
            try:
                await client.get_chat_member(Config.FORCE_SUB_CHANNEL, user_id)
            except UserNotParticipant:
                channel_url = f"https://t.me/{Config.FORCE_SUB_CHANNEL.replace('@', '')}"
                return await message.reply_text(
                    "❌ **Access Denied!**\n\n"
                    "You must join our update channel to use this bot. "
                    "After joining, try sending the file again.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("📢 Join Channel", url=channel_url)
                    ]])
                )
            except Exception as e:
                logger.error(f"Force sub error: {e}")

        # 2. Daily Limit Check
        # Admin has unlimited access
        is_admin = (user_id == Config.ADMIN_ID)
        allowed, current_count = db.check_user(user_id, Config.DAILY_LIMIT)
        
        if not allowed and not is_admin:
            return await message.reply_text(
                f"⚠️ **Daily Limit Reached!**\n\n"
                f"You have used your daily limit of **{Config.DAILY_LIMIT}** files. "
                "Please try again tomorrow!"
            )

        # 3. Stylish Processing Message
        status_msg = await message.reply_text("🔄 **Initializing...**")
        await asyncio.sleep(0.6)
        await status_msg.edit_text("⚙️ **Extracting File Metadata...**")
        await asyncio.sleep(0.6)
        await status_msg.edit_text("🔗 **Generating Secure Streaming Link...**")

        # 4. Identification
        media = (
            message.video or message.document or message.audio or 
            message.photo or message.voice or message.animation
        )
        file_id = media.file_id
        file_name = getattr(media, "file_name", "Media File")

        # 5. Link Generation
        base = Config.DOMAIN.rstrip('/')
        if not base.startswith("http") and base:
            base = f"https://{base}"
        
        if not base:
            base = f"http://localhost:{Config.PORT}"

        streaming_link = f"{base}/download/{file_id}?chat={message.chat.id}&msg={message.id}"

        # 6. Final Result
        usage_text = "Unlimited" if is_admin else f"{current_count}/{Config.DAILY_LIMIT}"
        
        response_text = (
            "✅ **Link Generated Successfully!**\n\n"
            f"📂 **File:** `{file_name}`\n"
            f"📊 **Today's Usage:** `{usage_text}`\n\n"
            f"🚀 **Direct Download Link:**\n"
            f"`{streaming_link}`"
        )
        
        await status_msg.edit_text(
            # We use an inline button for a cleaner look
            response_text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📥 Download Now", url=streaming_link)
            ]])
        )

    except Exception as e:
        logger.error(f"Error handling file: {e}")
        await message.reply_text("❌ An error occurred while processing the file.")

@Client.on_message(filters.command("stats") & filters.user(Config.ADMIN_ID))
async def stats_handler(client, message):
    """Admin only: Check total users"""
    total = db.get_total_users()
    await message.reply_text(f"📊 **Bot Statistics:**\n\nTotal Users: `{total}`")
