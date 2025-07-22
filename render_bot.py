#!/usr/bin/env python3
"""
Main file to launch the Telegram bot on Render.com or locally using .env
"""
import os
import logging
from telebot import TeleBot
from keep_alive import keep_alive
from dotenv import load_dotenv

# Chargement des variables d’environnement à partir d’un fichier .env
load_dotenv()

# Initialisation du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Récupération du token
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN is not set! (from environment or .env)")
    exit(1)

# Création du bot
bot = TeleBot(TOKEN)

# Lancement de la surveillance keep_alive
keep_alive.start_monitor()

# Commande /start de test
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🤖 Bot en ligne et opérationnel!")

# Boucle principale
try:
    logger.info("✅ Bot démarré...")
    bot.infinity_polling()
except Exception as e:
    logger.exception("❌ Erreur dans le bot : %s", e)
