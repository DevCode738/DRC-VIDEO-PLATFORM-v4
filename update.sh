#!/bin/bash
cd /opt/drcbot
pkill -9 -f bot.py
# Backup old
mv video_platform.py video_platform_old.py 2>/dev/null
# Copy new
cp /root/video_platform_v4.py video_platform.py
# Restart
nohup python3 bot.py > logs/bot.log 2>&1 &
echo "Updated and restarted!"
sleep 3
tail -n 10 logs/bot.log
