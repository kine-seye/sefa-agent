# agent/brain.py — Cerveau de Sefa avec Groq (gratuit et rapide)
# Sefa Bien-etre

import os
import yaml
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("sefa")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"  # Meilleur modele gratuit Groq


def _cfg():
    try:
        with open("config/prompts.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}


def charger_system_prompt() -> str:
    return _cfg().get("system_prompt", "Tu es Sefa, assistant bienveillant en sante mentale. Reponds en francais avec empathie.")


def msg_erreur() -> str:
    return _cfg().get("error_message", "Je rencontre un souci technique. Reessaie dans quelques instants.")


def msg_fallback() -> str:
    return _cfg().get("fallback_message", "Je n'ai pas bien compris. Tu peux reformuler ?")


async def generer_reponse(message: str, historique: list) -> str:
    if not message or len(message.strip()) < 2:
        return msg_fallback()

    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY manquante dans .env")
        return msg_erreur()

    # Construire les messages au format OpenAI (compatible Groq)
    messages = [{"role": "system", "content": charger_system_prompt()}]

    for msg in historique:
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": message})

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.8,
        "max_tokens": 1024,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                GROQ_URL,
                json=payload,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                }
            )

            if r.status_code != 200:
                logger.error(f"Erreur Groq API: {r.status_code} — {r.text}")
                return msg_erreur()

            data = r.json()
            reponse = data["choices"][0]["message"]["content"]
            logger.info(f"Reponse Groq generee ({len(reponse)} caracteres)")
            return reponse

    except Exception as e:
        logger.error(f"Erreur Groq: {e}")
        return msg_erreur()
