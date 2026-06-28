# agent/main.py — Serveur FastAPI + Webhook WhatsApp
# Sefa Bien-être

import os
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
from agent.brain import generer_reponse
from agent.memory import initialiser_db, sauvegarder_message, obtenir_historique
from agent.providers import obtenir_fournisseur

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("sefa")
fournisseur = obtenir_fournisseur()

APP_URL = os.getenv("APP_URL", "https://sefa-agent.onrender.com")


async def keep_alive():
    """Ping toutes les 10 min pour éviter que Render s'endorme."""
    import httpx
    await asyncio.sleep(60)
    while True:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(f"{APP_URL}/")
                logger.info(f"Keep-alive: {r.status_code}")
        except Exception as e:
            logger.warning(f"Keep-alive échoué: {e}")
        await asyncio.sleep(600)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialiser_db()
    logger.info("Sefa Bien-être démarré ✓")
    asyncio.create_task(keep_alive())
    yield


app = FastAPI(title="Sefa Bien-être", version="1.0.0", lifespan=lifespan)


@app.get("/")
async def health():
    return {"status": "ok", "agent": "Sefa", "service": "Sefa Bien-être"}


@app.get("/webhook")
async def webhook_get(request: Request):
    r = await fournisseur.valider_webhook(request)
    if r is not None:
        return PlainTextResponse(str(r))
    return {"status": "ok"}


@app.post("/webhook")
async def webhook_post(request: Request):
    try:
        messages = await fournisseur.parser_webhook(request)
        for msg in messages:
            if msg.est_propre or not msg.texte:
                continue
            logger.info(f"Message de {msg.telephone}: {msg.texte[:60]}")
            historique = await obtenir_historique(msg.telephone)
            reponse = await generer_reponse(msg.texte, historique)
            await sauvegarder_message(msg.telephone, "user", msg.texte)
            await sauvegarder_message(msg.telephone, "assistant", reponse)
            succes = await fournisseur.envoyer_message(msg.telephone, reponse)
            logger.info(f"Envoyé à {msg.telephone}: {'✓' if succes else '✗'}")
    except Exception as e:
        logger.error(f"Erreur webhook: {e}", exc_info=True)
    return {"status": "ok"}
