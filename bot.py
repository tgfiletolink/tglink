import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from utils.database import db
from utils.stream_server import start_web_server
import logging

logging.basicConfig(level=logging.INFO)

app = Client(
    "file_link_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="handlers")
)

@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    user_id = message.from_user.id
    
    # Check for referral
    text = message.text
    if len(text.split()) > 1:
        referrer_id = text.split()[1]
        if referrer_id.isdigit() and int(referrer_id) != user_id:
            # Add referral points
            success = db.add_referral(user_id, int(referrer_id))
            if success:
                try:
                    await client.send_message(
                        int(referrer_id), 
                        "🎉 **New Referral!** One person joined using your link. You got **+10 Daily Limit**!"
                    )
                except: pass

    welcome_text = (
        "👋 **Welcome to the Premium File Link Bot!**\n\n"
        "Send me any file and I'll give you a direct download link.\n\n"
        "📜 **Menu:**\n"
        "• /my - Check your stats & referral link\n"
        "• /help - How to use this bot\n"
        "• /about - Developer info"
    )
    
    await message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 My Stats", callback_data="my_stats"), InlineKeyboardButton("📢 Channel", url=f"https://t.me/{Config.FORCE_SUB_CHANNEL.replace('@', '')}")],
            [InlineKeyboardButton("🛠 Support", url=Config.SUPPORT_LINK)]
        ])
    )

@app.on_message(filters.command("my") & filters.private)
async def my_stats_cmd(client, message):
    await show_user_stats(client, message.from_user.id, message)

@app.on_callback_query(filters.regex("my_stats"))
async def my_stats_callback(client, callback_query):
    await show_user_stats(client, callback_query.from_user.id, callback_query.message, edit=True)

async def show_user_stats(client, user_id, message, edit=False):
    extra_limit, total_ref = db.get_user_data(user_id) or (0, 0)
    bot_username = (await client.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start={user_id}"
    
    stats_text = (
        "👤 **User Statistics**\n\n"
        f"🎁 Bonus Limit: `{extra_limit}`\n"
        f"👥 Total Referrals: `{total_ref}`\n"
        f"📅 Daily Base Limit: `{Config.DAILY_LIMIT}`\n"
        f"📊 Total Daily Limit: `{Config.DAILY_LIMIT + extra_limit}`\n\n"
        f"🔗 **Your Referral Link:**\n`{ref_link}`\n\n"
        "*(Share this link and get +10 limit for each referral!)*"
    )
    
    if edit:
        await message.edit_text(stats_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_home")]]))
    else:
        await message.reply_text(stats_text)

@app.on_message(filters.command("help") & filters.private)
async def help_command(client, message):
    help_text = (
        "❓ **How to use this Bot?**\n\n"
        "1️⃣ Forward or Upload any file to this chat.\n"
        "2️⃣ Wait for the bot to generate a link.\n"
        "3️⃣ Tap on **Download Now** to get your file.\n\n"
        "💡 **Tip:** If you reach your daily limit, refer friends using /my to increase it!"
    )
    await message.reply_text(help_text)

@app.on_callback_query(filters.regex("back_home"))
async def back_home_callback(client, callback_query):
    await callback_query.message.delete()
    await start_command(client, callback_query.message)

async def main():
    await app.start()
    await start_web_server(app)
    print("Bot is fully online with Referrals and UI!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
