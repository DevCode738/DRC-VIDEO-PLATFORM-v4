#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# DRC VIDEO PLATFORM - TELEGRAM BOT WRAPPER
# /v command triggers full 4-stage pipeline

import os, sys, asyncio, logging, datetime
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, filters

# Import the video platform engine
sys.path.insert(0, "/opt/drcbot")
from video_platform import generate_short, OUTPUT_DIR, LOG_DIR

TG_BOT_TOKEN = "8811380378:AAFZPBXhCtzOYfSQBn1NEFOEeclQynozH6s"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("DRC_BOT")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome = ("🔥 DRC VIDEO PLATFORM 🔥\n\nYo " + str(user.first_name) +
               "! anonymous ka bot aa gaya!\n\n🎬 /v - Generate 10s viral short\n"
               "⚡ 4-Stage AI Pipeline:\n"
               "  1. Groq Script\n"
               "  2. OpenRouter JSON\n"
               "  3. AI Voiceover\n"
               "  4. MoviePy Render\n\n"
               "🎯 9:16 | 10s | 24 FPS | Ultrafast\n"
               "Try /v now! 🚀")
    keyboard = [
        [InlineKeyboardButton("🎬 Generate /v", callback_data="generate")],
    ]
    await update.message.reply_text(welcome, reply_markup=InlineKeyboardMarkup(keyboard))

async def v_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id
    prog = await update.message.reply_text("⏳ Stage 1: Groq script generation...")

    try:
        # Run pipeline
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = str(OUTPUT_DIR / ("short_" + str(uid) + "_" + ts + ".mp4"))

        await prog.edit_text("⏳ Stage 1: Groq script... ✅\n⏳ Stage 2: OpenRouter JSON...")

        # Import and run
        import video_platform
        result = video_platform.generate_short(output_path=out_path)

        if result and os.path.exists(result):
            await prog.edit_text("✅ Stage 4: Render complete! Sending video...")
            sz = os.path.getsize(result) / (1024 * 1024)
            with open(result, "rb") as v:
                cap = ("🎬 AI Generated Short\n"
                       "⚡ 4-Stage Pipeline | 9:16 | 10s\n"
                       "📦 " + str(round(sz, 1)) + "MB\n"
                       "👑 DRC | anonymous")
                await update.message.reply_video(video=v, caption=cap, supports_streaming=True)
            await prog.delete()
            os.remove(result)
            logger.info("[DONE] Video sent to user " + str(uid))
        else:
            await prog.edit_text("❌ Generation failed. Check server logs.")

    except Exception as e:
        logger.error("Bot error: " + str(e))
        await prog.edit_text("❌ Error: " + str(e)[:200])

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "generate":
        await q.edit_message_text("📤 Type /v to generate your short!")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Error: " + str(context.error))

def main():
    logger.info("DRC VIDEO PLATFORM BOT STARTING | anonymous | 24/7")
    app = Application.builder().token(TG_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("v", v_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_error_handler(error_handler)
    logger.info("BOT RUNNING - /v triggers 4-stage pipeline")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
