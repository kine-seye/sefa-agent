import os, logging, base64, httpx
from fastapi import Request
from agent.providers.base import FournisseurWhatsApp, MessageEntrant

logger = logging.getLogger('sefa')

class FournisseurTwilio(FournisseurWhatsApp):
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token  = os.getenv('TWILIO_AUTH_TOKEN')
        self.numero      = os.getenv('TWILIO_PHONE_NUMBER')

    async def parser_webhook(self, request: Request) -> list[MessageEntrant]:
        form   = await request.form()
        texte  = form.get('Body', '')
        tel    = form.get('From', '').replace('whatsapp:', '')
        msg_id = form.get('MessageSid', '')
        if not texte:
            return []
        return [MessageEntrant(telephone=tel, texte=texte, message_id=msg_id, est_propre=False)]

    async def envoyer_message(self, telephone: str, message: str) -> bool:
        if not all([self.account_sid, self.auth_token, self.numero]):
            logger.warning('Variables Twilio manquantes dans .env')
            return False
        url  = f'https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json'
        auth = base64.b64encode(f'{self.account_sid}:{self.auth_token}'.encode()).decode()
        async with httpx.AsyncClient() as client:
            r = await client.post(url,
                headers={'Authorization': f'Basic {auth}'},
                data={'From': f'whatsapp:{self.numero}', 'To': f'whatsapp:{telephone}', 'Body': message})
            return r.status_code == 201
