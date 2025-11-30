# Developed by ARGON telegram: @REACTIVEARGON
import os
import time
from pathlib import Path

from pyrogram import Client, filters
from pyrogram.types import Message

from bot.func.encode import encode, safe_download_media
from bot.logger import LOGGER

log = LOGGER(__name__)


async def check_and_process_video_document(message: Message) -> dict:
    """
    Enhanced function that returns detailed information about the video document
    """
    result = {
        "is_video_document": False,
        "is_encodable": False,
        "file_info": {},
        "encoding_ready": False,
    }

    # Check if message has video or document
    if not message.document and not message.video:
        log.info("Message has no document or video attachment")
        return result

    # Get the media object (prioritize video over document)
    doc = message.video if message.video else message.document
    result["is_video_document"] = True

    log.info(f"Processing media: type={'video' if message.video else 'document'}")

    # Collect file information
    result["file_info"] = {
        "file_name": getattr(doc, "file_name", None) or f"video_{int(time.time())}.mp4",
        "file_size": getattr(doc, "file_size", 0),
        "mime_type": getattr(doc, "mime_type", ""),
        "file_id": getattr(doc, "file_id", ""),
        "duration": getattr(doc, "duration", 0),
        "width": getattr(doc, "width", 0),
        "height": getattr(doc, "height", 0),
    }

    log.info(f"File info: {result['file_info']}")

    # Check if it's encodable
    encodable_formats = {
        ".mp4",
        ".avi",
        ".mov",
        ".mkv",
        ".wmv",
        ".flv",
        ".webm",
        ".m4v",
        ".3gp",
        ".ogv",
        ".ts",
        ".mts",
        ".m2ts",
        ".vob",
        ".asf",
        ".rm",
        ".rmvb",
    }

    # Check by extension
    file_name = result["file_info"]["file_name"]
    if file_name:
        ext = os.path.splitext(file_name)[1].lower()
        if ext in encodable_formats:
            result["is_encodable"] = True
            log.info(f"File is encodable by extension: {ext}")

    # Check by MIME type
    mime_type = result["file_info"]["mime_type"]
    if mime_type and mime_type.startswith("video/"):
        result["is_encodable"] = True
        log.info(f"File is encodable by MIME type: {mime_type}")

    # Additional checks for encoding readiness
    if result["is_encodable"]:
        # Check file size (reasonable limits for encoding)
        max_size = 2 * 1024 * 1024 * 1024  # 2GB limit
        file_size = result["file_info"]["file_size"]
        if 0 < file_size <= max_size:
            result["encoding_ready"] = True
            log.info(
                f"File is ready for encoding (size: {file_size / (1024*1024):.2f} MB)"
            )

    return result


@Client.on_message(
    (filters.private) & (filters.document | filters.video | filters.audio)
)
async def enhanced_document_handler(client: Client, message: Message):
    """
    Enhanced document handler with detailed video analysis and proper error handling
    """
    user_id = message.from_user.id
    log.info(f"Processing document/video from user {user_id}")

    # Log to Channel
    try:
        from bot.config import LOG_CHANNEL
        user = message.from_user
        user_link = f"<a href='tg://user?id={user_id}'>{user.first_name}</a>"
        await client.send_message(
            LOG_CHANNEL,
            f"📥 <b>File Received</b>\n\n"
            f"👤 <b>User:</b> {user_link} (<code>{user_id}</code>)\n"
            f"📄 <b>File:</b> <code>{getattr(message.document or message.video, 'file_name', 'Unknown')}</code>"
        )
    except Exception as e:
        log.error(f"Failed to send log to channel: {e}")

    # Initialize variables for cleanup
    download_file_path = None
    download_msg = None

    try:
        # Analyze the video document
        video_info = await check_and_process_video_document(message)
        log.info(f"Video analysis result: {video_info}")

        if not video_info["is_video_document"]:
            await message.reply_text("📄 This is not a video document.")
            return

        if not video_info["is_encodable"]:
            await message.reply_text(
                "⚠️ **Video Document Detected**\n\n"
                "This appears to be a video file, but it may not be suitable for encoding due to:\n"
                "• Unsupported format\n"
                "• File too large (>2GB)\n"
                "• Missing metadata\n\n"
                f"**File Info:**\n"
                f"📁 Name: `{video_info['file_info']['file_name']}`\n"
                f"📏 Size: `{video_info['file_info']['file_size'] / (1024*1024):.2f} MB`\n"
                f"🏷️ Type: `{video_info['file_info']['mime_type']}`"
            )
            return

        if not video_info["encoding_ready"]:
            await message.reply_text(
                "❌ **Video Not Ready for Encoding**\n\n"
                "The video file is not ready for encoding. Please check:\n"
                "• File size is within limits\n"
                "• File is not corrupted\n"
                "• Proper video format"
            )
            return

        # Video is ready for encoding
        # Create download path
        downloads_dir = Path("downloads")
        downloads_dir.mkdir(exist_ok=True)

        file_name = video_info["file_info"]["file_name"]
        # Sanitize filename
        safe_filename = "".join(
            c for c in file_name if c.isalnum() or c in (" ", "-", "_", ".")
        ).strip()
        if not safe_filename:
            safe_filename = f"video_{int(time.time())}.mp4"

        download_file_path = downloads_dir / safe_filename
        log.info(f"Download path: {download_file_path}")

        # Start download
        download_msg = await message.reply_text("📥 **Downloading...**")
        downloaded_path = await safe_download_media(
            client, message, str(download_file_path), download_msg
        )

        if not downloaded_path:
            await download_msg.edit("❌ **Download Failed**")
            return

        # Start encoding
        # FFmpeg command is now generated dynamically based on user settings in bot/func/encode.py
        # We pass an empty string or placeholder as it's ignored/overridden internally.

        if not os.path.exists(downloaded_path):
            await download_msg.edit("❌ **Error:** File not found after download.")
            return

        await encode(
            ffmpeg_cmd="", # Ignored, uses User Settings
            input_file=downloaded_path,
            client=client,
            user_id=user_id,
            message=download_msg,
            chat_id=message.chat.id,
            message_id=message.id,
        )

    except Exception as e:
        log.error(f"Unexpected error in document handler for user {user_id}: {e}")
        if download_msg:
            await download_msg.edit(f"❌ **Error:** {str(e)}")
        else:
            await message.reply_text(f"❌ **Error:** {str(e)}")

        # Cleanup if we failed before queuing (and file exists but wasn't queued)
        # If queued, encode function handles cleanup
        if download_file_path and os.path.exists(download_file_path):
            # We only clean up here if we didn't reach the encode call or it failed immediately
            # But encode returns a dict, so we can check success?
            # For now, let's just leave it, as encode handles its own cleanup
            # if it fails internally.
            try:
                os.remove(download_file_path)
                log.info(f"Cleaned up file after error: {download_file_path}")
            except Exception as cleanup_error:
                log.error(
                    f"Failed to cleanup file {download_file_path}: {cleanup_error}"
                )
