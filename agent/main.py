import os, logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
from agent.brain import generer_reponse
from agent.memory import initialiser_db, sauvegarder_message, obtenir_historique
from agent.providers import obtenir_fournisseur

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger('sefa')
fournisseur = obtenir_fournisseur()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialiser_db()
    logger.info('Sefa Bien-etre demarre')
    yield

app = FastAPI(title='Sefa Bien-etre', version='1.0.0', lifespan=lifespan)

@app.get('/')
async def health():
    return {'status': 'ok', 'agent': 'Sefa'}

@app.get('/webhook')
async def webhook_get(request: Request):
    r = await fournisseur.valider_webhook(request)
    if r is not None:
        return PlainTextResponse(str(r))
    return {'status': 'ok'}

@app.post('/webhook')
async def webhook_post(request: Request):
    try:
        messages = await fournisseur.parser_webhook(request)
        for msg in messages:
            if msg.est_propre or not msg.texte:
                continue
            historique = await obtenir_historique(msg.telephone)
            reponse = await generer_reponse(msg.texte, historique)
            await sauvegarder_message(msg.telephone, 'user', msg.texte)
            await sauvegarder_message(msg.telephone, 'assistant', reponse)
            await fournisseur.envoyer_message(msg.telephone, reponse)
    except Exception as e:
        logger.error(f'Erreur webhook: {e}', exc_info=True)
    return {'status': 'ok'}
