#!/usr/bin/env python3
"""
Production bot for Render.com deployment - Updated 2025
"""
import os
import logging
import sys
import signal
import re
import json
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes
from compteur import get_compteurs, update_compteurs, reset_compteurs_canal
from style import afficher_compteurs_canal

# Track processed messages per channel
processed_messages = set()

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
style_affichage = 1
app_instance = None

def save_bot_status(running, message=None, error=None):
    """Save status to file"""
    status = {
        "running": running,
        "last_message": message,
        "error": error
    }
    try:
        with open("bot_status.json", "w") as f:
            json.dump(status, f)
    except Exception as e:
        logger.error(f"Could not save status: {e}")

def is_message_processed(message_key):
    """Check if message was already processed"""
    return message_key in processed_messages

def mark_message_processed(message_key):
    """Mark message as processed"""
    processed_messages.add(message_key)

def load_processed_messages():
    """Load processed messages from file"""
    global processed_messages
    try:
        with open("processed_messages.json", "r") as f:
            processed_messages = set(json.load(f))
    except:
        processed_messages = set()

def save_processed_messages():
    """Save processed messages to file"""
    try:
        with open("processed_messages.json", "w") as f:
            json.dump(list(processed_messages), f)
    except:
        pass

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    logger.info("Shutting down bot gracefully...")
    save_bot_status(False, "Bot stopped")
    if app_instance:
        app_instance.stop()
    sys.exit(0)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages and edited messages"""
    global style_affichage

    try:
        msg = update.message or update.channel_post or update.edited_channel_post or update.edited_message
        if not msg or not msg.text:
            return

        text = msg.text
        chat_id = msg.chat_id

        is_edited = update.edited_channel_post or update.edited_message

        logger.info(f"Channel {chat_id}: {'[EDITED] ' if is_edited else ''}{text[:80]}")

        match_numero = re.search(r"#n(\d+)", text)
        if not match_numero:
            match = re.search(r'\(([^()]*)\)', text)
            if not match:
                return
            contenu = match.group(1)
            cartes = re.findall(r"[❤️♦️♣️♠️]", contenu)
            update_compteurs(chat_id, cartes)
            mark_message_processed(text)
            await context.bot.send_message(chat_id=chat_id, text=afficher_compteurs_canal(chat_id, style_affichage))
        else:
            match = re.search(r"#n\d+\s*\(([^()]*)\)", text)
            if not match:
                return
            contenu = match.group(1)
            cartes = re.findall(r"[❤️♦️♣️♠️]", contenu)
            update_compteurs(chat_id, cartes)
            mark_message_processed(text)
            await context.bot.send_message(chat_id=chat_id, text=afficher_compteurs_canal(chat_id, style_affichage))

    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        save_bot_status(False, error=str(e))


# =============================
# FLASK + WEBHOOK POUR RENDER
# =============================
from flask import Flask, request
import telegram

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Ex: "https://ton-bot.onrender.com/"

bot = telegram.Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

# Ajoute ici les handlers
application.add_handler(MessageHandler(filters.TEXT, handle_message))

app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put(update)
    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "Bot en ligne."

def start_webhook():
    application.bot.set_webhook(url=f"{WEBHOOK_URL}{TOKEN}")
    application.run_polling()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    PORT = int(os.environ.get("PORT", 8443))
    start_webhook()
    app.run(host="0.0.0.0", port=PORT)
