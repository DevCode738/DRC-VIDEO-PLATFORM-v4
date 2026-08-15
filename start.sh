#!/bin/bash
cd /opt/drcbot
pkill -9 -f bot.py
rm -f logs/*
nohup python3 bot.py > logs/bot.log 2>&1 &
echo "Bot started!"
sleep 3
ps aux | grep "python3 /opt/drcbot/bot.py" | grep -v grep
tail -n 15 logs/bot.log
