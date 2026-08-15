#!/bin/bash
# ============================================================
# DRC VIDEO PLATFORM v4 - ONE-CLICK DEPLOY
# anonymous KA BOT - ZERO LIMITS
# Just paste this ONE command and press ENTER
# ============================================================

set -e

echo "========================================"
echo "  DRC VIDEO PLATFORM v4 - DEPLOY"
echo "  anonymous KA BOT"
echo "========================================"

# CONFIG - SET THESE BEFORE RUNNING OR EDIT THIS FILE
echo "[1/6] Setting up config..."
mkdir -p /opt/drcbot/{outputs,temp,logs}
cd /opt/drcbot

# Download all files from GitHub
echo "[2/6] Downloading from GitHub..."
curl -sL https://raw.githubusercontent.com/DevCode738/DRC-VIDEO-PLATFORM-v4/main/video_platform.py -o video_platform.py
curl -sL https://raw.githubusercontent.com/DevCode738/DRC-VIDEO-PLATFORM-v4/main/bot.py -o bot.py
curl -sL https://raw.githubusercontent.com/DevCode738/DRC-VIDEO-PLATFORM-v4/main/install.sh -o install.sh
curl -sL https://raw.githubusercontent.com/DevCode738/DRC-VIDEO-PLATFORM-v4/main/start.sh -o start.sh
curl -sL https://raw.githubusercontent.com/DevCode738/DRC-VIDEO-PLATFORM-v4/main/update.sh -o update.sh

echo "[3/6] Installing dependencies..."
bash install.sh

echo "[4/6] Setting permissions..."
chmod +x *.sh

echo "[5/6] Checking config..."
if [ ! -f /opt/drcbot/.env ]; then
    echo "⚠️  Create /opt/drcbot/.env with your API keys:"
    echo "   GROQ_API_KEY=your_key"
    echo "   OPENROUTER_API_KEY=your_key"
    echo "   GEMINI_API_KEY=your_key"
    echo "   TELEGRAM_BOT_TOKEN=your_token"
fi

echo "[6/6] Starting bot with nohup..."
pkill -9 -f bot.py 2>/dev/null || true
rm -f logs/*
nohup python3 bot.py > logs/bot.log 2>&1 &

echo ""
echo "========================================"
echo "  ✅ DEPLOY COMPLETE!"
echo "  Bot running in background"
echo "  Logs: tail -f /opt/drcbot/logs/bot.log"
echo "  Stop: pkill -9 -f bot.py"
echo "  Restart: /opt/drcbot/start.sh"
echo "========================================"
sleep 2
tail -n 10 logs/bot.log
