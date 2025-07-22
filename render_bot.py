import os
import threading
import logging
from telebot import TeleBot
from dotenv import load_dotenv
from flask import Flask

# Chargement des variables d’environnement
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Récupération du token
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN is not set!")
    exit(1)

# Création du bot
bot = TeleBot(TOKEN)

# Commande /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ Bot en ligne et opérationnel !")

# Fonction de démarrage du bot
def start_bot():
    logger.info("✅ Bot démarré...")
    bot.infinity_polling()

# Serveur Flask pour que Render garde le service actif
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot en ligne (Flask) !"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Exécution des deux en parallèle
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    start_bot()
