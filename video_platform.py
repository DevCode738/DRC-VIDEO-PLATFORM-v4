#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
# DRC AUTOMATED SHORT-FORM VIDEO PLATFORM
# anonymous KA BOT - ZERO LIMITS
# 9:16 Vertical | 10 Seconds Strict | 24 FPS | Ultrafast
# Stage 1: Groq Script | Stage 2: OpenRouter JSON
# Stage 3: TTS Voiceover | Stage 4: MoviePy Composite
# VPS Optimized: 2 vCPU | 1GB RAM
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
W, H = 1080, 1920      # 9:16 vertical
FPS = 24               # strict 24 FPS
TOTAL_DURATION = 10.0  # strict 10 seconds
PRESET = "ultrafast"   # VPS optimized
THREADS = 2            # match 2 vCPU

# Color palette
COLORS = {
    "blood_red": (180, 20, 20),
    "neon_cyan": (0, 255, 255),
    "electric_purple": (138, 43, 226),
    "gold": (255, 215, 0),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "dark_gray": (20, 20, 20),
    "fire_orange": (255, 100, 0),
}

BG_THEMES = {
    "dark_gradient": [(10, 10, 15), (30, 30, 40), (15, 15, 25)],
    "red_storm": [(20, 0, 0), (60, 0, 0), (30, 0, 0)],
    "purple_haze": [(15, 0, 20), (40, 0, 50), (25, 0, 35)],
    "blue_depth": [(0, 10, 20), (0, 30, 50), (0, 15, 30)],
}

# ============================================================
# STAGE 1: GROQ - Generate Punchy Personal Struggle Script
# ============================================================
def stage1_groq_script():
    logger.info("[STAGE 1] Groq script generation...")
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": "Bearer " + GROQ_API_KEY, "Content-Type": "application/json"}
        prompt = """Write a highly engaging, punchy 10-second personal struggle/motivation script for a vertical short video.
Rules:
- Total spoken words: 15-20 words max (fits 10 seconds)
- 4 distinct punchy segments
- Each segment: 3-5 words, highly emotional
- Theme: overcoming struggle, pain to power
- Style: raw, aggressive, inspiring
- NO emojis, NO hashtags

Return ONLY the 4 lines, one per line. No extra text."""
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 256,
            "temperature": 0.9
        }
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"].strip()
        lines = [l.strip("-\"'• ") for l in text.split("\n") if l.strip() and len(l.strip()) > 2]
        lines = lines[:4]
        if len(lines) < 4:
            lines += ["I BROKE", "I BLED", "I ROSE", "I WON"][:4-len(lines)]
        logger.info("[STAGE 1] Script: " + " | ".join(lines))
        return lines
    except Exception as e:
        logger.error("[STAGE 1 ERROR] " + str(e))
        return ["I BROKE", "I BLED", "I ROSE", "I WON"]

# ============================================================
# STAGE 2: OpenRouter - Structure into JSON Schema
# ============================================================
def stage2_openrouter_json(lines):
    logger.info("[STAGE 2] OpenRouter JSON structuring...")
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": "Bearer " + OPENROUTER_API_KEY,
            "Content-Type": "application/json",
            "HTTP-Referer": "https://anonymous.bot",
            "X-Title": "DRC Video Platform"
        }
        script_text = " | ".join(lines)
        prompt = """Convert this 4-segment script into a strict JSON schema for video generation.
Each segment gets exactly 2.5 seconds. Total 10 seconds.

Available animations: slide_up, slide_down, slide_left, slide_right, zoom_in, fade_in, glitch_reveal
Available fonts: bold, heavy, impact
Available colors: blood_red, neon_cyan, electric_purple, gold, white, fire_orange
Available bg_themes: dark_gradient, red_storm, purple_haze, blue_depth

Return ONLY valid JSON. No markdown, no explanations.

Schema:
{
  "title": "video title",
  "segments": [
    {"text": "line1", "start_time": 0.0, "duration": 2.5, "color": "white", "font": "bold", "animation": "slide_up", "bg_theme": "dark_gradient"},
    {"text": "line2", "start_time": 2.5, "duration": 2.5, "color": "blood_red", "font": "heavy", "animation": "zoom_in", "bg_theme": "red_storm"},
    {"text": "line3", "start_time": 5.0, "duration": 2.5, "color": "neon_cyan", "font": "bold", "animation": "slide_right", "bg_theme": "purple_haze"},
    {"text": "line4", "start_time": 7.5, "duration": 2.5, "color": "gold", "font": "impact", "animation": "fade_in", "bg_theme": "blue_depth"}
  ]
}

Script: """ + script_text
        payload = {
            "model": "openai/gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 512
        }
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"]
        # Extract JSON
        start = text.find("{")
        end = text.rfind("}") + 1
        data = json.loads(text[start:end])
        # Validate and fix timing
        for i, seg in enumerate(data.get("segments", [])):
            seg["start_time"] = round(i * 2.5, 1)
            seg["duration"] = 2.5
        logger.info("[STAGE 2] JSON structured with " + str(len(data.get("segments", []))) + " segments")
        return data
    except Exception as e:
        logger.error("[STAGE 2 ERROR] " + str(e))
        # Fallback JSON
        return {
            "title": "BREAK THEN BUILD",
            "segments": [
                {"text": lines[0], "start_time": 0.0, "duration": 2.5, "color": "white", "font": "bold", "animation": "slide_up", "bg_theme": "dark_gradient"},
                {"text": lines[1], "start_time": 2.5, "duration": 2.5, "color": "blood_red", "font": "heavy", "animation": "zoom_in", "bg_theme": "red_storm"},
                {"text": lines[2], "start_time": 5.0, "duration": 2.5, "color": "neon_cyan", "font": "bold", "animation": "slide_right", "bg_theme": "purple_haze"},
                {"text": lines[3], "start_time": 7.5, "duration": 2.5, "color": "gold", "font": "impact", "animation": "fade_in", "bg_theme": "blue_depth"},
            ]
        }

# ============================================================
# STAGE 3: Voiceover - Google TTS (gTTS)
# Note: Gemini API does not provide TTS. gTTS uses Google's
# free TTS endpoint and produces high-quality MP3 voiceover.
# ============================================================
def stage3_voiceover(segments, output_mp3):
    logger.info("[STAGE 3] Generating voiceover MP3...")
    if not GTTS_OK:
        logger.warning("[STAGE 3] gTTS not available, skipping voiceover")
        return None
    try:
        full_text = ". ".join([s["text"] for s in segments])
        tts = gTTS(text=full_text, lang="en", tld="us", slow=False)
        tts.save(str(output_mp3))
        logger.info("[STAGE 3] Voiceover saved: " + str(output_mp3))
        return str(output_mp3)
    except Exception as e:
        logger.error("[STAGE 3 ERROR] " + str(e))
        return None

# ============================================================
# STAGE 4: MoviePy Composite - VPS Optimized
# ============================================================
def get_font(size, font_name="bold"):
    """Load system font, fallback to default."""
    font_map = {
        "bold": ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "FreeSansBold.ttf"],
        "heavy": ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"],
        "impact": ["LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"],
    }
    base_paths = [
        "/usr/share/fonts/truetype/dejavu/",
        "/usr/share/fonts/truetype/liberation/",
        "/usr/share/fonts/truetype/freefont/",
    ]
    for fn in font_map.get(font_name, font_map["bold"]):
        for bp in base_paths:
            fp = bp + fn
            if os.path.exists(fp):
                return ImageFont.truetype(fp, size)
    return ImageFont.load_default()

def create_gradient_bg(width, height, theme_name, frame_idx=0):
    """Create animated gradient background."""
    colors = BG_THEMES.get(theme_name, BG_THEMES["dark_gradient"])
    img = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    n = len(colors)
    phase = (frame_idx * 0.02) % n
    for y in range(height):
        t = y / height
        idx = int(phase + t * n) % n
        nxt = (idx + 1) % n
        lt = (phase + t * n) % 1.0
        c = tuple(int(a + (b - a) * lt) for a, b in zip(colors[idx], colors[nxt]))
        draw.line([(0, y), (width, y)], fill=c)
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

    # Measure
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
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
    """Return (x, y) position for animation at time t."""
    progress = t / duration if duration > 0 else 1.0
    cx = W // 2 - clip_w // 2
    cy = H // 2 - clip_h // 2

    if animation == "slide_up":
        start_y = H + 100
        end_y = cy
        y = start_y + (end_y - start_y) * min(1.0, progress * 1.5)
        return (cx, int(y))
    elif animation == "slide_down":
        start_y = -clip_h - 100
        end_y = cy
        y = start_y + (end_y - start_y) * min(1.0, progress * 1.5)
        return (cx, int(y))
    elif animation == "slide_left":
        start_x = W + 100
        end_x = cx
        x = start_x + (end_x - start_x) * min(1.0, progress * 1.5)
        return (int(x), cy)
    elif animation == "slide_right":
        start_x = -clip_w - 100
        end_x = cx
        x = start_x + (end_x - start_x) * min(1.0, progress * 1.5)
        return (int(x), cy)
    elif animation == "zoom_in":
        return (cx, cy)  # scaling handled separately
    elif animation == "fade_in":
        return (cx, cy)
    elif animation == "glitch_reveal":
        return (cx, cy)
    else:
        return (cx, cy)

def stage4_moviepy_composite(data, voiceover_path, output_video):
    logger.info("[STAGE 4] MoviePy composite starting...")
    start = time.time()
    segments = data.get("segments", [])

    # Background clips - one per segment for gradient animation
    bg_clips = []
    for seg in segments:
        theme = seg.get("bg_theme", "dark_gradient")
        start_t = seg.get("start_time", 0)
        dur = seg.get("duration", 2.5)

        # Generate background frames
        frames = []
        for fi in range(int(dur * 3)):
            bg_img = create_gradient_bg(W, H, theme, fi + int(start_t * 10))
            frames.append(np.array(bg_img))

        bg_clip = ImageSequenceClip(frames, fps=3).set_duration(dur).set_start(start_t)
        bg_clips.append(bg_clip)

    # Text clips
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

        # Apply animation
        if anim == "zoom_in":
            txt_clip = txt_clip.resize(lambda t: 0.6 + 0.4 * min(1.0, t / (dur * 0.6)))
            txt_clip = txt_clip.set_position("center")
        elif anim == "fade_in":
            txt_clip = txt_clip.set_position("center")
            txt_clip = txt_clip.set_opacity(0.95)
        elif anim == "glitch_reveal":
            txt_clip = txt_clip.set_position("center")
            txt_clip = txt_clip.set_opacity(0.95)
        else:
            # Slide animations
            def pos_func(t, a=anim, d=dur):
                progress = t / d if d > 0 else 1.0
                cx, cy = W // 2, H // 2
                if a == "slide_up":
                    y = H + 100 - (H + 100 - cy + 65) * min(1.0, progress * 1.4)
                    return ("center", int(y))
                elif a == "slide_down":
                    y = -200 + (cy + 200) * min(1.0, progress * 1.4)
                    return ("center", int(y))
                elif a == "slide_left":
                    x = W + 100 - (W + 100 - cx + 200) * min(1.0, progress * 1.4)
                    return (int(x), "center")
                elif a == "slide_right":
                    x = -200 + (cx + 200) * min(1.0, progress * 1.4)
                    return (int(x), "center")
                return ("center", "center")
            txt_clip = txt_clip.set_position(lambda t: pos_func(t))

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
    video.write_videofile(
        output_video,
        fps=FPS,
        codec="libx264",
        preset=PRESET,
        threads=THREADS,
        audio_codec="aac" if video.audio else None,
        logger=None,
        temp_audiofile=str(TEMP_DIR / "tmp_audio.m4a"),
        remove_temp=True
    )
    video.close()

    elapsed = time.time() - start
    logger.info("[STAGE 4] Render complete in " + str(round(elapsed, 1)) + "s: " + output_video)
    return output_video

# ============================================================
# MAIN ORCHESTRATOR
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

        logger.info("✅ SHORT GENERATED: " + final)
        return final

    except Exception as e:
        logger.error("PIPELINE FAILED: " + str(e))
        logger.error(traceback.format_exc())
        return None

# ============================================================
# CLI / DIRECT RUN
# ============================================================
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="DRC Automated Video Platform")
    parser.add_argument("--output", "-o", default=None, help="Output video path")
    parser.add_argument("--topic", "-t", default=None, help="Optional topic hint")
    args = parser.parse_args()

    result = generate_short(output_path=args.output, topic=args.topic)
    if result:
        print("\n🎬 VIDEO READY: " + result)
        # Print file size
        sz = os.path.getsize(result) / (1024 * 1024)
        print("📦 Size: " + str(round(sz, 1)) + " MB")
    else:
        print("\n❌ Generation failed. Check logs.")
        sys.exit(1)
