#!/bin/bash

echo "🧹 Killing all existing 'fridaygpt' screen sessions..."

# List all screen sessions with 'fridaygpt' in their name and kill them
screen -ls | grep 'fridaygpt' | awk '{print $1}' | while read session; do
    echo "🔪 Killing session: $session"
    screen -S "${session}" -X quit
done

# final kill
ps aux | grep main.py | grep -v grep | awk '{print $2}' | xargs kill -9

echo "✅ All old sessions terminated."

echo "🚀 Starting a new screen session for FRIDAYGPT..."

# Start a fresh screen session named 'fridaygpt' and run the bot
screen -dmS fridaygpt bash -c 'cd ~/FridayGPT && source venv/bin/activate && python main.py'

echo "🎉 FRIDAYGPT has been restarted inside a clean screen session."
echo "💻 To attach: screen -r fridaygpt"
