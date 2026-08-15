DRC VIDEO PLATFORM - v4 FIX DEPLOY
===================================

FIX FOR: crossfadein / set_opacity error
ERROR: TypeError: unsupported operand type(s) for *: function and float
CAUSE: MoviePy 1.0.3 set_opacity() only accepts float, not lambda
FIX: Replaced crossfadein() with set_opacity(0.95) for fade_in and glitch_reveal

DEPLOY:
1. scp -P 22577 DRC_VIDEO_PLATFORM_v4.zip root@0.tcp.in.ngrok.io:/root/
2. ssh root@0.tcp.in.ngrok.io -p 22577
3. cd /root && unzip DRC_VIDEO_PLATFORM_v4.zip -d /opt/drcbot/
4. cd /opt/drcbot && chmod +x *.sh
5. ./install.sh  (if not already installed)
6. ./start.sh

OR QUICK UPDATE (if already deployed):
1. scp -P 22577 video_platform_v4.py root@0.tcp.in.ngrok.io:/root/
2. ssh root@0.tcp.in.ngrok.io -p 22577
3. cd /opt/drcbot && cp /root/video_platform_v4.py video_platform.py
4. pkill -9 -f bot.py
5. nohup python3 bot.py > logs/bot.log 2>&1 &

TELEGRAM:
  /v - Generate 10s AI short
  /start - Welcome

CLI TEST:
  cd /opt/drcbot
  python3 video_platform.py -o outputs/test.mp4

TROUBLESHOOT:
  tail -n 50 logs/bot.log
  python3 -m py_compile video_platform.py

===================================
