import os, logging, httpx
from fastapi import Request
from agent.providers.base import FournisseurWhatsApp, MessageEntrant

logger = logging.getLogger('sefa')

class FournisseurMeta(FournisseurWhatsApp):
    def __init__(self):
        self.access_token    = os.getenv('META_ACCESS_TOKEN')
        self.phone_number_id = os.getenv('META_PHONE_NUMBER_ID')
        self.verify_token    = os.getenv('META_VERIFY_TOKEN', 'sefa-verify-2026')

    async def valider_webhook(self, request: Request):
        p = request.query_params
        if p.get('hub.mode') == 'subscribe' and p.get('hub.verify_token') == self.verify_token:
            return int(p.get('hub.challenge'))
        return None

    async def parser_webhook(self, request: Request) -> list[MessageEntrant]:
        body = await request.json()
        msgs = []
        for entry in body.get('entry', []):
            for change in entry.get('changes', []):
                for msg in change.get('value', {}).get('messages', []):
                    if msg.get('type') == 'text':
                        msgs.append(MessageEntrant(
                            telephone=msg.get('from',''), texte=msg.get('text',{}).get('body',''),
                            message_id=msg.get('id',''), est_propre=False))
        return msgs

    async def envoyer_message(self, telephone: str, message: str) -> bool:
        if not self.access_token or not self.phone_number_id:
            return False
        url = f'https://graph.facebook.com/v21.0/{self.phone_number_id}/messages'
        async with httpx.AsyncClient() as client:
            r = await client.post(url,
                headers={'Authorization': f'Bearer {self.access_token}', 'Content-Type': 'application/json'},
                json={'messaging_product':'whatsapp','to':telephone,'type':'text','text':{'body':message}})
            return r.status_code == 200
