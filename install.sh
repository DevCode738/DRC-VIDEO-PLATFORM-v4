#!/bin/bash
echo "========================================"
echo "  DRC VIDEO PLATFORM - INSTALLER"
echo "  anonymous KA BOT - ZERO LIMITS"
echo "========================================"

apt-get update -qq
apt-get install -y -qq ffmpeg libgl1-mesa-glx imagemagick

pip3 install moviepy==1.0.3 gtts numpy pillow requests python-telegram-bot==20.7 psutil -q

python3 -c "import moviepy; print('MoviePy:', moviepy.__version__)"
python3 -c "from gtts import gTTS; print('gTTS: OK')"
python3 -c "from PIL import Image, ImageDraw, ImageFilter, ImageFont; print('PIL: OK')"

echo ""
echo "✅ INSTALL COMPLETE"
