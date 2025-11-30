# Developed by ARGON telegram: @REACTIVEARGON
import os
import shlex
from bot.logger import LOGGER
from typing import Dict, List

log = LOGGER(__name__)


def validate_ffmpeg_command(cmd: str) -> bool:
    """
    Validates a custom FFmpeg command for safety.
    Blocks usage of -i (input) and -y (overwrite) as these are handled by the bot.
    """
    try:
        args = shlex.split(cmd)
        forbidden_flags = ["-i", "-y"]

        for arg in args:
            if arg in forbidden_flags:
                return False

        # Basic check to ensure it's not empty or just whitespace
        if not cmd.strip():
            return False

        return True
    except Exception:
        return False

def prepare_watermark_assets(user_id: int, settings: Dict):
    """
    Checks for watermark assets in settings and restores them to disk if missing.
    Updates settings with local paths.
    """
    wm = settings.get("watermark", {})

    # Ensure directories
    if not os.path.exists("watermarks"):
        os.makedirs("watermarks")
    if not os.path.exists("watermarks/fonts"):
        os.makedirs("watermarks/fonts")

    # Restore Image
    if "image_data" in wm:
        image_path = os.path.join(os.getcwd(), "watermarks", f"{user_id}.png")
        if not os.path.exists(image_path):
            try:
                with open(image_path, "wb") as f:
                    f.write(wm["image_data"])
                log.info(f"Restored watermark image for user {user_id}")
            except Exception as e:
                log.error(f"Failed to restore watermark image: {e}")

        # Update path in settings to ensure it points to the restored file
        wm["image_path"] = image_path

    # Restore Font
    if "font_data" in wm:
        font_path = f"watermarks/fonts/{user_id}.ttf"
        if not os.path.exists(font_path):
            try:
                with open(font_path, "wb") as f:
                    f.write(wm["font_data"])
                log.info(f"Restored custom font for user {user_id}")
            except Exception as e:
                log.error(f"Failed to restore custom font: {e}")

def prepare_thumbnail(user_id: int, settings: Dict) -> str:
    """
    Checks for thumbnail in settings and restores it to disk if missing.
    Returns the path to the thumbnail if it exists, else None.
    """
    if "thumbnail" in settings:
        # Ensure directory
        if not os.path.exists("watermarks"):
            os.makedirs("watermarks")

        thumb_path = os.path.join(os.getcwd(), "watermarks", f"thumb_{user_id}.jpg")

        if not os.path.exists(thumb_path):
            try:
                with open(thumb_path, "wb") as f:
                    f.write(settings["thumbnail"])
                log.info(f"Restored thumbnail for user {user_id}")
            except Exception as e:
                log.error(f"Failed to restore thumbnail: {e}")
                return None

        return thumb_path
    return None

def generate_watermark_filter(settings: Dict, for_preview: bool = False) -> str:
    """
    Generates the FFmpeg filter string for watermarks.
    """
    wm_settings = settings.get("watermark", {})
    wm_type = wm_settings.get("type", "none")

    if wm_type == "none":
        return ""

    position = wm_settings.get("position", "top-right")
    opacity = float(wm_settings.get("opacity", 0.5))

    # Timing
    timing_mode = wm_settings.get("timing_mode", "always")
    start_time = float(wm_settings.get("start_time", 0))
    end_time = float(wm_settings.get("end_time", 0))
    interval_duration = float(wm_settings.get("interval_duration", 5))
    interval_period = float(wm_settings.get("interval_period", 30))

    enable_expr = ""
    if timing_mode == "range":
        enable_expr = f":enable='between(t,{start_time},{end_time})'"
    elif timing_mode == "interval":
        # Show for 'interval_duration' seconds every 'interval_period' seconds
        # mod(t, period) < duration
        enable_expr = f":enable='lt(mod(t,{interval_period}),{interval_duration})'"

    # Margins
    margins = wm_settings.get("margins", {})
    m_top = margins.get("top", 10)
    m_bottom = margins.get("bottom", 10)
    m_left = margins.get("left", 10)
    m_right = margins.get("right", 10)

    if position == "top-left":
        x, y = f"{m_left}", f"{m_top}"
    elif position == "top-right":
        x, y = f"w-tw-{m_right}", f"{m_top}"
    elif position == "bottom-left":
        x, y = f"{m_left}", f"h-th-{m_bottom}"
    elif position == "bottom-right":
        x, y = f"w-tw-{m_right}", f"h-th-{m_bottom}"

    credit_text = ""
    if for_preview:
        # Add Credit Text (Developed by Argon) only for preview
        credit_text = ",drawtext=fontfile='bot/fonts/Roboto-Regular.ttf':text='Developed by Argon':fontsize=24:fontcolor=black:x=w-tw-10:y=h-th-10"

    if wm_type == "text":
        text = wm_settings.get("text", "AutoAnimePro")
        font_size = int(wm_settings.get("font_size", 24))
        border_opacity = float(wm_settings.get("border_opacity", 0.5))

        # Font Selection
        user_id = settings.get("user_id")
        font_path = "bot/fonts/Roboto-Regular.ttf" # Default

        if user_id:
            custom_font = f"watermarks/fonts/{user_id}.ttf"
            if os.path.exists(custom_font):
                font_path = custom_font

        # Italic, Semi-transparent text with dark semi-transparent box border
        # fontcolor=white@opacity
        # box=1:boxcolor=black@border_opacity:boxborderw=5

        # Escape text for drawtext
        text = text.replace("'", "").replace(":", "\\:")

        return (
            f"drawtext=fontfile='{font_path}':text='{text}':fontsize={font_size}:fontcolor=white@{opacity}:"
            f"x={x}:y={y}:box=1:boxcolor=black@{border_opacity}:boxborderw=5{enable_expr}"
            f"{credit_text}"
        )

    elif wm_type == "image":
        image_path = wm_settings.get("image_path", "")
        if not image_path:
            return ""

        log.info(f"Watermark Image Path: {image_path}")
        log.info(f"Exists: {os.path.exists(image_path)}")
        log.info(f"CWD: {os.getcwd()}")

        scale = float(wm_settings.get("scale", 0.1)) # Scale relative to video width?
        # Actually easier to just scale the overlay input
        # We need a complex filter graph for image overlay
        # [0:v][1:v] overlay...
        # But here we are returning a filter string for -vf.
        # So we use the 'movie' filter source.

        # movie=filename [wm]; [wm] colorchannelmixer=aa=opacity [wm_trans]; [in][wm_trans] overlay=x:y
        # Note: 'movie' filter path needs to be escaped properly

        # For simplicity in this function, we return the filter chain part.
        # However, 'movie' filter is tricky with windows paths.
        # Let's try to use forward slashes.
        # Try to use relative path to avoid double-prefix issues
        try:
            image_path = os.path.relpath(image_path, os.getcwd())
        except ValueError:
            pass # Keep absolute if on different drive

        image_path = image_path.replace("\\", "/")

        # Resize image first?
        # scale=iw*scale:-1

        # Ensure RGBA format for opacity to work on all image types
        return (
            f"movie='{image_path}',scale=iw*{scale}:-1,format=rgba,colorchannelmixer=aa={opacity}[wm];"
            f"[0:v][wm]overlay=x={x.replace('tw', 'w').replace('th', 'h')}:y={y.replace('tw', 'w').replace('th', 'h')}{enable_expr}"
            f"{credit_text}"
        )

    return ""


def generate_ffmpeg_cmd(
    settings: Dict, input_file: str, output_base: str, thumbnail_path: str = None
) -> List[Dict[str, str]]:
    """
    Generates a list of FFmpeg commands based on user settings.
    Supports multiple resolutions.

    Returns a list of dicts:
    [
        {"cmd": "ffmpeg ...", "output_file": "/path/to/output_1080p.mp4", "suffix": "1080p"},
        ...
    ]
    """
    video_settings = settings.get("video", {})
    audio_settings = settings.get("audio", {})
    meta_settings = settings.get("metadata", {})

    # Watermark Filter
    wm_filter = generate_watermark_filter(settings)

    crf = video_settings.get("crf", "23")
    preset = video_settings.get("preset", "medium")
    codec = video_settings.get("codec", "mpeg4")
    resolutions = video_settings.get("resolution", ["1080p"])

    # Ensure resolutions is a list
    if isinstance(resolutions, str):
        resolutions = [resolutions]

    audio_bitrate = audio_settings.get("bitrate", "128k")
    title = meta_settings.get("title", "")
    author = meta_settings.get("author", "")

    commands = []

    for res in resolutions:
        # Determine scale filter
        scale_filter = ""
        if res == "1080p":
            scale_filter = "scale=-2:1080"
        elif res == "720p":
            scale_filter = "scale=-2:720"
        elif res == "480p":
            scale_filter = "scale=-2:480"
        elif res == "360p":
            scale_filter = "scale=-2:360"

        # Combine filters
        video_filters = []
        if wm_filter:
            if "movie=" in wm_filter:
                if scale_filter:
                    wm_filter_adjusted = wm_filter.replace("[0:v]", "[scaled]")
                    video_filters.append(f"{scale_filter} [scaled]; {wm_filter_adjusted}")
                else:
                    video_filters.append(wm_filter)
            else:
                # Text watermark (simple filter)
                if scale_filter:
                    video_filters.append(scale_filter)
                video_filters.append(wm_filter)
        else:
            if scale_filter:
                video_filters.append(scale_filter)

        # Build command
        cmd = ["ffmpeg"]
        cmd.extend(["-i", input_file])

        if thumbnail_path:
            cmd.extend(["-i", thumbnail_path])

        # Map streams
        # Map streams
        is_complex = video_filters and any("movie=" in f for f in video_filters)

        if not is_complex:
            cmd.extend(["-map", "0:v?"])

        cmd.extend(["-map", "0:a?", "-map", "0:s?"])

        if thumbnail_path:
            cmd.extend(["-map", "1"])
            cmd.extend(["-c:v:1", "png"])
            cmd.extend(["-disposition:v:1", "attached_pic"])

        if video_filters:
            if any("movie=" in f for f in video_filters):
                 cmd.extend(["-filter_complex", ",".join(video_filters)])
            else:
                 cmd.extend(["-vf", ",".join(video_filters)])

        # Video
        cmd.extend(["-c:v", codec])
        cmd.extend(["-crf", str(crf)])
        cmd.extend(["-preset", preset])

        # Audio (AAC for compatibility)
        cmd.extend(["-c:a", "aac"])
        cmd.extend(["-b:a", audio_bitrate])

        # Subtitles (Copy for MKV)
        cmd.extend(["-c:s", "copy"])

        # Metadata
        # Smart Defaults (Branding)
        bot_username = "AutoAnimeProBot" # Fallback

        # Global Defaults
        global_meta = meta_settings.get("global", {}).copy()
        if "title" not in global_meta: global_meta["title"] = "Encoded by @AutoAnimeProBot"
        if "artist" not in global_meta: global_meta["artist"] = "@AutoAnimeProBot"
        if "encoded_by" not in global_meta: global_meta["encoded_by"] = "@AutoAnimeProBot"

        for key, value in global_meta.items():
            if value:
                cmd.extend(["-metadata", f"{key}={value}"])

        # Video Stream Defaults
        video_meta = meta_settings.get("video", {}).copy()
        if "title" not in video_meta: video_meta["title"] = "Encoded by @AutoAnimeProBot"
        if "handler_name" not in video_meta: video_meta["handler_name"] = "AutoAnimeProBot"

        for key, value in video_meta.items():
            if value:
                cmd.extend(["-metadata:s:v", f"{key}={value}"])

        # Audio Stream Defaults
        audio_meta = meta_settings.get("audio", {}).copy()
        if "title" not in audio_meta: audio_meta["title"] = "Encoded by @AutoAnimeProBot"
        if "handler_name" not in audio_meta: audio_meta["handler_name"] = "AutoAnimeProBot"

        for key, value in audio_meta.items():
            if value:
                cmd.extend(["-metadata:s:a", f"{key}={value}"])

        # Subtitle Stream Defaults
        # Do NOT default functional tags like language/forced/default
        subtitle_meta = meta_settings.get("subtitle", {}).copy()
        if "title" not in subtitle_meta: subtitle_meta["title"] = "Encoded by @AutoAnimeProBot"
        if "handler_name" not in subtitle_meta: subtitle_meta["handler_name"] = "AutoAnimeProBot"

        for key, value in subtitle_meta.items():
            if value:
                cmd.extend(["-metadata:s:s", f"{key}={value}"])

        # Join command
        cmd_str = shlex.join(cmd)

        # Output filename
        # If multiple resolutions, append suffix
        suffix = f"_{res}" if len(resolutions) > 1 else ""
        output_path = f"{output_base}{suffix}.mkv"

        commands.append({"cmd": cmd_str, "output_file": output_path, "suffix": res})

    return commands
