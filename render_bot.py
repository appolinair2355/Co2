#!/usr/bin/env python3
"""
Bot Telegram Joker - Version complète pour Render.com
Gère les cartes, styles, historique, et webhook Flask
"""

import os
import re
import logging
from flask import Flask, request
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from compteur import get_compteurs, update_compteurs, reset_compteurs_canal
from style import afficher_compteurs_canal
from historique import deja_traite, enregistrer_message

# === Chargement des variables d’environnement ===
load_dotenv()
TOKEN = os.getenv("TOKEN")
PORT = int(os.getenv("PORT", 10000))
WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL", "https://ton-bot.onrender.com")

# === Initialisation Flask et Telegram ===
flask_app = Flask(__name__)
bot_app = Application.builder().token(TOKEN).build()

# === Logger ===
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# === Fonctions utilitaires ===

def extraire_cartes(message: str):
    match = re.search(r"\(([^()]*)\)", message)
    if not match:
        return []
    cartes = re.findall(r"[2-9JQKA10]+[♠️♦️♣️❤️♥️]", match.group(1))
    return cartes

# === Handlers ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot Joker actif !")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    reset_compteurs_canal(chat_id)
    await update.message.reply_text("♻️ Compteurs réinitialisés.")

async def changer_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or context.args[0] not in ["1", "2", "3", "4", "5"]:
        return await update.message.reply_text("Utilisation : /style [1-5]")
    chat_id = update.effective_chat.id
    style_id = int(context.args[0])
    from style import changer_style
    changer_style(chat_id, style_id)
    await update.message.reply_text(f"✅ Style changé en : {style_id}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat_id = message.chat.id
    message_id = message.message_id

    if deja_traite(chat_id, message_id):
        return

    cartes = extraire_cartes(message.text)
    if cartes:
        update_compteurs(chat_id, cartes)
        compteurs = get_compteurs(chat_id)
        texte = afficher_compteurs_canal(chat_id, compteurs)
        await message.reply_text(texte)
        enregistrer_message(chat_id, message_id)

# === Ajout des handlers ===

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("reset", reset))
bot_app.add_handler(CommandHandler("style", changer_style))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# === Flask routes ===

@flask_app.route("/")
def index():
    return "🤖 Bot Joker est en ligne !"

@flask_app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    await bot_app.process_update(update)
    return "OK"

# === Initialisation du webhook ===

async def init_webhook():
    await bot_app.bot.delete_webhook()
    url = f"{WEBHOOK_BASE_URL}/{TOKEN}"
    await bot_app.bot.set_webhook(url=url)
    logger.info(f"✅ Webhook défini : {url}")

# === Lancement du bot ===

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_webhook())
