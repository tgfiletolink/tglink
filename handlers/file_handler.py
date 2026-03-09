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

def humanbytes(size):
    """Formats bytes into human readable format"""
    if not size: return "Unknown"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

@Client.on_message(filters.private & filters.media)
async def handle_file(client: Client, message: Message):
    """
    Enhanced UI handler for media files.
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
                    "🛑 **Access Denied!**\n\n"
                    "You must join our update channel to use this bot. "
                    "This helps us keep the service alive!",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("📢 Join Update Channel", url=channel_url)
                    ]])
                )
            except Exception as e:
                logger.error(f"Force sub error: {e}")

        # 2. Daily Limit Check
        is_admin = (user_id == Config.ADMIN_ID)
        allowed, current_count, total_limit = db.check_user(user_id, Config.DAILY_LIMIT)
        
        if not allowed and not is_admin:
            return await message.reply_text(
                f"⚠️ **Daily Limit Exceeded!**\n\n"
                f"Your limit: `{total_limit}` files/day.\n"
                "To get more limit, refer your friends using `/my` link!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🎁 Get More Limit", callback_data="get_limit")
                ]])
            )

        # 3. Stylish Processing
        status_msg = await message.reply_text("🚀 **Initializing...**")
        await asyncio.sleep(0.5)
        await status_msg.edit_text("🛰 **Processing on Telegram Servers...**")

        # 4. Identification
        media = (
            message.video or message.document or message.audio or 
            message.photo or message.voice or message.animation
        )
        file_id = media.file_id
        file_name = getattr(media, "file_name", "Media_File")
        file_size = getattr(media, "file_size", 0)
        readable_size = humanbytes(file_size)

        # 5. Link Generation
        base = Config.DOMAIN.rstrip('/')
        if not base.startswith("http") and base:
            base = f"https://{base}"
        
        if not base:
            base = f"http://localhost:{Config.PORT}"

        streaming_link = f"{base}/download/{file_id}?chat={message.chat.id}&msg={message.id}"

        # 6. Beautiful UI Result
        usage_text = "♾ Unlimited" if is_admin else f"{current_count} / {total_limit}"
        
        response_text = (
            "✅ **Link Generated Successfully!**\n\n"
            f"📄 **File Name:** `{file_name}`\n"
            f"⚖️ **File Size:** `{readable_size}`\n"
            f"📊 **Usage Today:** `{usage_text}`\n\n"
            f"🔗 **Download Link:**\n"
            f"`{streaming_link}`\n\n"
            f"✨ **Created by:** {Config.DEVELOPER}"
        )
        
        await status_msg.edit_text(
            response_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📥 High Speed Download", url=streaming_link)],
                [InlineKeyboardButton("🛠 Support", url=Config.SUPPORT_LINK), InlineKeyboardButton("👥 Refer Friends", callback_data="get_limit")]
            ])
        )

    except Exception as e:
        logger.error(f"Error handling file: {e}")
        await message.reply_text("❌ **An error occurred.** Please try again or contact support.")

@Client.on_callback_query(filters.regex("get_limit"))
async def get_limit_callback(client, callback_query):
    user_id = callback_query.from_user.id
    bot_username = (await client.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start={user_id}"
    
    text = (
        "🎁 **Referral Program**\n\n"
        "Refer a friend and get **+10 Daily Limit** for each person who joins!\n\n"
        f"🔗 **Your Referral Link:**\n`{ref_link}`"
    )
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[
        InlineKeyboardButton("🔙 Back", callback_data="back_to_main")
    ]]))

@Client.on_callback_query(filters.regex("back_to_main"))
async def back_to_main(client, callback_query):
    await callback_query.message.delete()
