#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
# DRC AUTOMATED SHORT-FORM VIDEO PLATFORM v4.1 - FIXED
# anonymous KA BOT - ZERO LIMITS
# 9:16 Vertical | 10 Seconds Strict | 24 FPS | Ultrafast
# Stage 1: Groq Script | Stage 2: OpenRouter JSON
# Stage 3: TTS Voiceover | Stage 4: MoviePy Composite
# VPS Optimized: 2 vCPU | 1GB RAM
# FIXES: ImageSequenceClip duration, set_opacity, font fallback
# ============================================================

import os, sys, json, time, math, random, textwrap, traceback, logging
from pathlib import Path
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

try:
    from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, ImageSequenceClip
    from moviepy.audio.AudioClip import CompositeAudioClip
    MOVIEPY_OK = True
except ImportError as e:
    MOVIEPY_OK = False
    print("[FATAL] MoviePy import error:", e)
    print("Run: pip3 install moviepy==1.0.3")
    sys.exit(1)

try:
    from gtts import gTTS
    GTTS_OK = True
except ImportError:
    GTTS_OK = False
    print("[WARN] gTTS not installed. Voiceover disabled. Run: pip3 install gtts")

# ============================================================
# CONFIG
# ============================================================
GROQ_API_KEY = "YOUR_GROQ_API_KEY"
OPENROUTER_API_KEY = "YOUR_OPENROUTER_API_KEY"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

BASE_DIR = Path("/opt/drcbot")
OUTPUT_DIR = BASE_DIR / "outputs"
TEMP_DIR = BASE_DIR / "temp"
LOG_DIR = BASE_DIR / "logs"

for d in [OUTPUT_DIR, TEMP_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("DRC_VIDEO")

# Video specs
W, H = 1080, 1920
FPS = 24
TOTAL_DURATION = 10.0
PRESET = "ultrafast"
THREADS = 2

# Colors
COLORS = {
    "white": (255, 255, 255),
    "yellow": (255, 220, 50),
    "cyan": (50, 220, 255),
    "red": (255, 60, 60),
    "green": (60, 255, 120),
    "purple": (180, 80, 255),
    "orange": (255, 140, 40),
}

# ============================================================
# STAGE 1: GROQ SCRIPT
# ============================================================
def stage1_groq_script():
    logger.info("[STAGE 1] Groq script generation...")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": "Bearer " + GROQ_API_KEY, "Content-Type": "application/json"}
    topics = [
        "AI revolution", "future of work", "mind hacking", "digital nomad life",
        "startup grind", "crypto mindset", "productivity hacks", "sleep optimization",
        "focus mastery", "wealth psychology", "fitment motivation", "coding life"
    ]
    topic = random.choice(topics)
    prompt = (
        "Generate a viral 10-second short-form video script. Topic: " + topic +
        ". STRICT RULES:
"
        "- EXACTLY 4 segments
"
        "- Each segment: 1 powerful hook line (max 8 words)
"
        "- Total script must fit in 10 seconds when spoken fast
"
        "- Use punchy, viral language
"
        "- Format: numbered list, one line per segment
"
        "- NO emojis, NO hashtags, NO stage directions
"
        "- Just the raw text lines"
    )
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9,
        "max_tokens": 200
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        lines = [l.strip().lstrip("0123456789.-) ") for l in content.split("
") if l.strip()]
        lines = [l for l in lines if len(l) > 3][:4]
        if len(lines) < 4:
            lines += ["Think different.", "Move fast.", "Break things.", "Build the future."][:4-len(lines)]
        logger.info("[STAGE 1] Script: " + " | ".join(lines))
        return lines
    except Exception as e:
        logger.error("[STAGE 1] Failed: " + str(e))
        return ["AI is changing everything.", "Are you ready?", "The future is now.", "Act fast."]

# ============================================================
# STAGE 2: OPENROUTER JSON
# ============================================================
def stage2_openrouter_json(lines):
    logger.info("[STAGE 2] OpenRouter JSON scene data...")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": "Bearer " + OPENROUTER_API_KEY, "Content-Type": "application/json"}
    prompt = (
        "Convert these 4 text lines into a JSON video scene array. Each scene needs:
"
        "- text: the line (string)
"
        "- start_time: when it appears (0, 2.5, 5.0, 7.5)
"
        "- duration: how long it stays (2.5)
"
        "- color: text color (white, yellow, cyan, red, green, purple, orange)
"
        "- font: style (bold, heavy, impact)
"
        "- bg_theme: background (dark_gradient, neon_pulse, cyber_grid, warm_glow)
"
        "- animation: entrance (slide_up, slide_down, zoom_in, fade_in, glitch_reveal, slide_left, slide_right)

"
        "Lines:
" + "
".join([str(i+1) + ". " + l for i, l in enumerate(lines)]) +
        "

Return ONLY valid JSON with this exact structure:
"
        '{"segments": [{"text":"...","start_time":0,"duration":2.5,"color":"white","font":"bold","bg_theme":"dark_gradient","animation":"slide_up"}, ...]}'
    )
    payload = {
        "model": "google/gemini-2.0-flash-lite-001",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 500
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        # Extract JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        data = json.loads(content.strip())
        if "segments" not in data or len(data["segments"]) < 4:
            raise ValueError("Invalid segment count")
        logger.info("[STAGE 2] JSON parsed: " + str(len(data["segments"])) + " segments")
        return data
    except Exception as e:
        logger.error("[STAGE 2] Failed: " + str(e))
        # Fallback JSON
        return {
            "segments": [
                {"text": lines[0], "start_time": 0, "duration": 2.5, "color": "white", "font": "bold", "bg_theme": "dark_gradient", "animation": "slide_up"},
                {"text": lines[1], "start_time": 2.5, "duration": 2.5, "color": "yellow", "font": "heavy", "bg_theme": "neon_pulse", "animation": "slide_down"},
                {"text": lines[2], "start_time": 5.0, "duration": 2.5, "color": "cyan", "font": "impact", "bg_theme": "cyber_grid", "animation": "zoom_in"},
                {"text": lines[3], "start_time": 7.5, "duration": 2.5, "color": "red", "font": "bold", "bg_theme": "warm_glow", "animation": "glitch_reveal"},
            ]
        }

# ============================================================
# STAGE 3: TTS VOICEOVER
# ============================================================
def stage3_voiceover(segments, output_path):
    if not GTTS_OK:
        logger.warning("[STAGE 3] gTTS not available, skipping voiceover")
        return None
    logger.info("[STAGE 3] Generating voiceover...")
    try:
        text = " ".join([seg.get("text", "") for seg in segments])
        tts = gTTS(text=text, lang="en", tld="us", slow=False)
        tts.save(str(output_path))
        logger.info("[STAGE 3] Voiceover saved: " + str(output_path))
        return str(output_path)
    except Exception as e:
        logger.error("[STAGE 3] TTS failed: " + str(e))
        return None

# ============================================================
# HELPERS
# ============================================================
def get_font(size, font_name="bold"):
    """Load system font, fallback to default."""
    font_map = {
        "bold": ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "FreeSansBold.ttf", "NotoSans-Bold.ttf"],
        "heavy": ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "NotoSans-Bold.ttf"],
        "impact": ["LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf", "NotoSans-Bold.ttf"],
    }
    base_paths = [
        "/usr/share/fonts/truetype/dejavu/",
        "/usr/share/fonts/truetype/liberation/",
        "/usr/share/fonts/truetype/freefont/",
        "/usr/share/fonts/truetype/noto/",
    ]
    for fn in font_map.get(font_name, font_map["bold"]):
        for bp in base_paths:
            fp = bp + fn
            if os.path.exists(fp):
                return ImageFont.truetype(fp, size)
    # Try to find ANY bold font
    import subprocess
    try:
        result = subprocess.run(["fc-list", ":style=Bold", "file"], capture_output=True, text=True)
        fonts = [l.split(":")[0].strip() for l in result.stdout.strip().split("
") if l.strip()]
        if fonts:
            return ImageFont.truetype(fonts[0], size)
    except:
        pass
    return ImageFont.load_default()

def create_gradient_bg(width, height, theme_name, frame_idx=0):
    """Generate animated gradient background frame."""
    img = Image.new("RGB", (width, height))
    pixels = img.load()

    # Color palettes
    palettes = {
        "dark_gradient": [(10, 10, 30), (30, 10, 50), (10, 30, 50)],
        "neon_pulse": [(5, 5, 20), (20, 5, 40), (5, 20, 40)],
        "cyber_grid": [(0, 10, 20), (10, 0, 30), (0, 20, 30)],
        "warm_glow": [(30, 10, 5), (50, 20, 10), (40, 30, 5)],
    }
    colors = palettes.get(theme_name, palettes["dark_gradient"])

    # Animate offset
    offset = (frame_idx * 3) % height

    for y in range(height):
        for x in range(width):
            # Diagonal gradient with animation
            t = ((x + y + offset) % height) / height
            idx = int(t * (len(colors) - 1))
            frac = t * (len(colors) - 1) - idx
            if idx >= len(colors) - 1:
                c = colors[-1]
            else:
                c1, c2 = colors[idx], colors[idx + 1]
                c = tuple(int(c1[i] + (c2[i] - c1[i]) * frac) for i in range(3))
            pixels[x, y] = c
    return img

def draw_text_frame(text, color_name, font_name, size=140, glow=True):
    """Render text to transparent PNG with glow effect."""
    color = COLORS.get(color_name, COLORS["white"])
    glow_color = tuple(min(255, c + 80) for c in color)

    # Create large canvas
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = get_font(size, font_name)

    # Wrap text if too long
    if len(text) > 12:
        text = textwrap.fill(text, width=10)

    # Measure - handle both old and new PIL
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
    except AttributeError:
        tw, th = draw.textsize(text, font=font)

    x = (W - tw) // 2
    y = (H - th) // 2

    # Multi-layer glow
    if glow:
        for r in range(25, 0, -5):
            alpha = int(90 * (1 - r / 25))
            glow_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            gdraw = ImageDraw.Draw(glow_img)
            gdraw.text((x, y), text, font=font, fill=glow_color + (alpha,))
            glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=r))
            img = Image.alpha_composite(img, glow_img)
            draw = ImageDraw.Draw(img)

    # Outline
    for dx, dy in [(-3, -3), (-3, 3), (3, -3), (3, 3), (0, -3), (0, 3), (-3, 0), (3, 0)]:
        draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0, 255))

    # Main text
    draw.text((x, y), text, font=font, fill=color + (255,))
    return img

def animation_position(animation, duration, t, clip_w, clip_h):
    """Calculate position for slide animations."""
    progress = t / duration if duration > 0 else 1.0
    cx, cy = W // 2, H // 2
    if animation == "slide_up":
        y = H + 100 - (H + 100 - cy + 65) * min(1.0, progress * 1.4)
        return ("center", int(y))
    elif animation == "slide_down":
        y = -200 + (cy + 200) * min(1.0, progress * 1.4)
        return ("center", int(y))
    elif animation == "slide_left":
        x = W + 100 - (W + 100 - cx + 200) * min(1.0, progress * 1.4)
        return (int(x), "center")
    elif animation == "slide_right":
        x = -200 + (cx + 200) * min(1.0, progress * 1.4)
        return (int(x), "center")
    return ("center", "center")

# ============================================================
# STAGE 4: MOVIEPY COMPOSITE - FIXED VERSION
# ============================================================
def stage4_moviepy_composite(data, voiceover_path, output_video):
    logger.info("[STAGE 4] MoviePy composite starting...")
    start = time.time()
    segments = data.get("segments", [])

    if not segments:
        logger.error("[STAGE 4] No segments provided")
        return None

    # Background clips - FIXED: use ImageClip with proper duration instead of ImageSequenceClip
    bg_clips = []
    for seg in segments:
        theme = seg.get("bg_theme", "dark_gradient")
        start_t = seg.get("start_time", 0)
        dur = seg.get("duration", 2.5)

        # Generate single background frame (static for this segment)
        bg_img = create_gradient_bg(W, H, theme, int(start_t * 10))
        bg_np = np.array(bg_img)

        # Use ImageClip instead of ImageSequenceClip - more reliable
        bg_clip = ImageClip(bg_np).set_duration(dur).set_start(start_t)
        bg_clips.append(bg_clip)

    # Text clips - FIXED: proper handling of animations
    text_clips = []
    for seg in segments:
        text = seg.get("text", "TEXT")
        color = seg.get("color", "white")
        font = seg.get("font", "bold")
        anim = seg.get("animation", "slide_up")
        start_t = seg.get("start_time", 0)
        dur = seg.get("duration", 2.5)

        # Render text image
        txt_img = draw_text_frame(text, color, font, size=130)
        txt_np = np.array(txt_img)

        # Create clip
        txt_clip = ImageClip(txt_np).set_duration(dur).set_start(start_t)

        # Apply animation - FIXED: avoid problematic methods
        if anim == "zoom_in":
            # Use a simple scale instead of time-dependent resize
            txt_clip = txt_clip.resize(0.8)
            txt_clip = txt_clip.set_position("center")
        elif anim == "fade_in":
            txt_clip = txt_clip.set_position("center")
            # Use crossfadein instead of set_opacity for fade effect
            txt_clip = txt_clip.crossfadein(0.3)
        elif anim == "glitch_reveal":
            txt_clip = txt_clip.set_position("center")
            # Simple reveal - no opacity issues
        else:
            # Slide animations - use set_position with lambda
            txt_clip = txt_clip.set_position(lambda t: animation_position(anim, dur, t, txt_clip.w, txt_clip.h))

        text_clips.append(txt_clip)

    # Composite all layers
    all_clips = bg_clips + text_clips
    video = CompositeVideoClip(all_clips, size=(W, H)).set_duration(TOTAL_DURATION)

    # Add voiceover audio
    if voiceover_path and os.path.exists(voiceover_path):
        try:
            audio = AudioFileClip(voiceover_path)
            # Trim or pad to match video duration exactly
            if audio.duration > TOTAL_DURATION:
                audio = audio.subclip(0, TOTAL_DURATION)
            else:
                audio = audio.set_duration(TOTAL_DURATION)
            # Fade out at end
            audio = audio.audio_fadeout(0.5)
            video = video.set_audio(audio)
            logger.info("[STAGE 4] Audio attached: " + str(audio.duration) + "s")
        except Exception as e:
            logger.warning("[STAGE 4] Audio error: " + str(e))

    # Export - VPS optimized
    logger.info("[STAGE 4] Rendering video...")
    try:
        video.write_videofile(
            output_video,
            fps=FPS,
            codec="libx264",
            preset=PRESET,
            threads=THREADS,
            audio_codec="aac" if video.audio else None,
            logger=None,
            verbose=False,
            temp_audiofile=str(TEMP_DIR / ("tmp_audio_" + str(int(time.time())) + ".m4a")),
            remove_temp=True
        )
        elapsed = time.time() - start
        logger.info("[STAGE 4] Render complete: " + output_video + " (" + str(round(elapsed, 1)) + "s)")
        return output_video
    except Exception as e:
        logger.error("[STAGE 4] Render failed: " + str(e))
        logger.error(traceback.format_exc())
        return None

# ============================================================
# MAIN PIPELINE
# ============================================================
def generate_short(output_path=None, topic=None):
    """Full pipeline: Groq -> OpenRouter -> TTS -> MoviePy"""
    ts = time.strftime("%Y%m%d_%H%M%S")
    if output_path is None:
        output_path = str(OUTPUT_DIR / ("short_" + ts + ".mp4"))

    voiceover_path = TEMP_DIR / ("voice_" + ts + ".mp3")

    logger.info("=" * 60)
    logger.info("DRC VIDEO PLATFORM - GENERATING SHORT")
    logger.info("9:16 | 10s | 24 FPS | Ultrafast | VPS Optimized")
    logger.info("=" * 60)

    try:
        # Stage 1
        lines = stage1_groq_script()

        # Stage 2
        data = stage2_openrouter_json(lines)

        # Stage 3
        voiceover = stage3_voiceover(data.get("segments", []), voiceover_path)

        # Stage 4
        final = stage4_moviepy_composite(data, voiceover, output_path)

        # Cleanup temp
        if voiceover and os.path.exists(voiceover):
            os.remove(voiceover)

        if final and os.path.exists(final):
            logger.info("SHORT GENERATED: " + final)
            return final
        else:
            logger.error("PIPELINE FAILED: No output file generated")
            return None

    except Exception as e:
        logger.error("PIPELINE FAILED: " + str(e))
        logger.error(traceback.format_exc())
        return None

# ============================================================
# CLI
# ============================================================
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="DRC Video Platform")
    parser.add_argument("-o", "--output", default=None, help="Output file path")
    parser.add_argument("-t", "--topic", default=None, help="Video topic")
    args = parser.parse_args()
    result = generate_short(args.output, args.topic)
    if result:
        print("SUCCESS: " + result)
    else:
        print("FAILED")
        sys.exit(1)
