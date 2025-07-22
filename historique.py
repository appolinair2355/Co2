import psycopg2
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def deja_traite(channel_id, message_id):
    """Vérifie si un message a déjà été traité"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM processed_messages WHERE channel_id = %s AND message_id = %s",
        (channel_id, message_id),
    )
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result is not None

def enregistrer_message(channel_id, message_id):
    """Enregistre un message comme traité"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO processed_messages (channel_id, message_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
        (channel_id, message_id),
    )
    conn.commit()
    cur.close()
    conn.close()
