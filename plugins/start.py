# Developed by ARGON telegram: @REACTIVEARGON
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.decorator import task
from bot.logger import LOGGER
from database import full_userbase, add_user

log = LOGGER(__name__)

START_IMG = "https://i.ibb.co/RGJnsfC6/monkey-d-luffy-red-3840x2160-24473.png"

START_TEXT = """
<b>⚡ Auto Rename Bot</b>

I am the <b>Ultimate Anime Automation Tool</b>.
Capable of high-speed encoding and seamless file management.

<blockquote>🚀 <b>Power Features:</b>
• <b>Fast Encoding:</b> Optimized FFmpeg presets
• <b>Smart Queue:</b> Auto-resume & persistence
• <b>Format Support:</b> MKV, MP4, AVI & more</blockquote>

<b>Ready to level up your workflow?</b>
"""

HELP_TEXT = """
<blockquote><b>🛠️ Command Arsenal:</b>

<code>/start</code> - Initialize System
<code>/help</code> - Access Manual
<code>/queue</code> - View Operations
<code>/cancel</code> - Abort Task
<code>/stats</code> - System Metrics</blockquote>

<b>Need backup?</b> Check the support channel.
"""

ABOUT_TEXT = """
<b>🤖 System Information</b>

<b>Version:</b> <code>2.0.0 (Stable)</code>
<b>Engine:</b> <code>Pyrogram + FFmpeg</code>

<blockquote>🔗 <b>Links:</b>
• <a href="https://t.me/fair_bots">Main Channel</a>
• <a href="https://t.me/reactiveargon">Developer</a>
• <a href="https://t.me/fair_bot_support">Support Group</a></blockquote>
"""

TUTORIAL_TEXT = """
<b>🚀 Quick Start Guide</b>

<blockquote><b>1. Send a Video</b>
Simply forward or upload a video file to the bot.

<b>2. Choose Settings</b>
Use the <code>/settings</code> command to configure:
• <b>Resolution:</b> 1080p, 720p, etc.
• <b>Codec:</b> x264, x265 (HEVC)
• <b>Watermark:</b> Add your custom branding

<b>3. Relax</b>
The bot will process your video and send it back!</blockquote>

<i>Tip: Use /queue to check progress.</i>
"""

FEATURES_TEXT = """
<b>🚀 Argons Encoder: The Ultimate Video Automation Bot</b>

<blockquote>Transform your Telegram workflow with professional-grade encoding! 🎬

<b>✨ Key Features:</b>

• <b>Smart Queue:</b> Auto-resume & persistence ⚡
• <b>Pro Quality:</b> FFmpeg power with custom presets 🎞️
• <b>Total Control:</b> Watermarks, metadata & admin panel 🛡️

<i>Fast, stable, and fully customizable.</i> 🌟

Developed by @REACTIVEARGON</blockquote>
"""


@Client.on_message(filters.command("start"))
@task
async def start(client, message, query=False):
    if not query:
        from database import present_user
        user_id = message.from_user.id
        if not await present_user(user_id):
            await add_user(user_id)

            # Log New User
            try:
                from bot.config import LOG_CHANNEL
                user = message.from_user
                user_link = f"<a href='tg://user?id={user_id}'>{user.first_name}</a>"
                username = f"@{user.username}" if user.username else "No Username"

                await client.send_message(
                    LOG_CHANNEL,
                    f"🆕 <b>New User Started Bot</b>\n\n"
                    f"👤 <b>User:</b> {user_link} (<code>{user_id}</code>)\n"
                    f"🏷️ <b>Username:</b> {username}"
                )
            except Exception as e:
                log.error(f"Failed to send new user log: {e}")

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🚀 Quick Start", callback_data="cb_tutorial"),
                InlineKeyboardButton("📚 Help", callback_data="cb_help"),
                InlineKeyboardButton("ℹ️ About", callback_data="cb_about"),
            ],
            [
                InlineKeyboardButton("📊 Stats", callback_data="cb_stats"),
                InlineKeyboardButton("❌ Close", callback_data="cb_close"),
            ],
        ]
    )

    if query:
        await message.edit_caption(caption=START_TEXT, reply_markup=buttons)
    else:
        await message.reply_photo(
            photo=START_IMG, caption=START_TEXT, reply_markup=buttons
        )


@Client.on_message(filters.command("help"))
async def help_command(client, message):
    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 Back", callback_data="cb_start")]]
    )
    await message.reply_text(text=HELP_TEXT, reply_markup=buttons)


@Client.on_message(filters.command("stats"))
async def stats_command(client, message):
    users = await full_userbase()
    total_users = len(users)

    stats_text = (
        f"<b>📊 System Metrics</b>\n\n"
        f"<blockquote>👥 <b>Active Users:</b> <code>{total_users}</code>\n"
        "⚡ <b>Uptime:</b> <code>100%</code></blockquote>"
    )

    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("❌ Close", callback_data="cb_close")]]
    )

    await message.reply_text(text=stats_text, reply_markup=buttons)


@Client.on_message(filters.command("features"))
async def features_command(client, message):
    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("❌ Close", callback_data="cb_close")]]
    )
    await message.reply_text(text=FEATURES_TEXT, reply_markup=buttons)


@Client.on_callback_query(filters.regex("^cb_"))
async def handle_callbacks(client, callback_query: CallbackQuery):
    data = callback_query.data
    message = callback_query.message
    is_photo = bool(message.photo)

    if data == "cb_start":
        if is_photo:
            await start(client, message, query=True)
        else:
            await message.delete()
            await start(client, message, query=False)

    elif data == "cb_help":
        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Back", callback_data="cb_start")]]
        )
        if is_photo:
            await message.edit_caption(caption=HELP_TEXT, reply_markup=buttons)
        else:
            await message.edit_text(text=HELP_TEXT, reply_markup=buttons)

    elif data == "cb_about":
        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Back", callback_data="cb_start")]]
        )
        if is_photo:
            await message.edit_caption(caption=ABOUT_TEXT, reply_markup=buttons)
        else:
            await message.edit_text(text=ABOUT_TEXT, reply_markup=buttons)

    elif data == "cb_tutorial":
        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Back", callback_data="cb_start")]]
        )
        if is_photo:
            await message.edit_caption(caption=TUTORIAL_TEXT, reply_markup=buttons)
        else:
            await message.edit_text(text=TUTORIAL_TEXT, reply_markup=buttons)

    elif data == "cb_stats":
        users = await full_userbase()
        total_users = len(users)

        stats_text = (
            f"<b>📊 System Metrics</b>\n\n"
            f"<blockquote>👥 <b>Active Users:</b> <code>{total_users}</code>\n"
            "⚡ <b>Uptime:</b> <code>100%</code></blockquote>"
        )

        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Back", callback_data="cb_start")]]
        )
        if is_photo:
            await message.edit_caption(caption=stats_text, reply_markup=buttons)
        else:
            await message.edit_text(text=stats_text, reply_markup=buttons)

    elif data == "cb_close":
        await message.delete()

    await callback_query.answer()
