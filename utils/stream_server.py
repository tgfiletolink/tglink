import math
import logging
from aiohttp import web
from pyrogram import Client
from pyrogram.types import Message
from config import Config

logger = logging.getLogger(__name__)

async def media_streamer(request):
    """
    Handles the HTTP request and streams the media from Telegram to the user.
    """
    file_id = request.match_info.get("file_id")
    client = request.app["bot"]
    
    try:
        # We need a message object to stream. Since we only have file_id, 
        # normally we'd store the message_id in a DB. 
        # For simplicity in this 'instant' bot, we will use a cache or 
        # assume the user sent it recently. 
        # A better way: the link includes message_id and chat_id.
        chat_id = request.query.get("chat")
        msg_id = request.query.get("msg")
        
        if not chat_id or not msg_id:
            return web.Response(text="Direct link needs context. Please use the link provided by the bot.", status=400)
        
        message: Message = await client.get_messages(int(chat_id), int(msg_id))
        
        media = (
            message.video or message.document or message.audio or 
            message.photo or message.voice or message.animation
        )
        
        if not media:
            return web.Response(text="Media not found.", status=404)

        file_size = getattr(media, "file_size", 0)
        file_name = getattr(media, "file_name", "file")
        mime_type = getattr(media, "mime_type", "application/octet-stream")

        # Set headers for download
        headers = {
            "Content-Type": mime_type,
            "Content-Length": str(file_size),
            "Content-Disposition": f'attachment; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        }

        response = web.StreamResponse(headers=headers)
        await response.prepare(request)

        # Stream chunks from Telegram
        async for chunk in client.stream_media(message, limit=0):
            await response.write(chunk)

        await response.write_eof()
        return response

    except Exception as e:
        logger.error(f"Streaming error: {e}")
        return web.Response(text=f"Error: {e}", status=500)

async def start_web_server(bot_client):
    app = web.Application()
    app["bot"] = bot_client
    app.router.add_get("/download/{file_id}", media_streamer)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", Config.PORT)
    await site.start()
    logger.info(f"Web server started on port {Config.PORT}")
