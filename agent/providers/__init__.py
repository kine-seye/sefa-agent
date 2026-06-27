import os
from agent.providers.base import FournisseurWhatsApp

def obtenir_fournisseur() -> FournisseurWhatsApp:
    f = os.getenv('WHATSAPP_PROVIDER', '').lower()
    if f == 'meta':
        from agent.providers.meta import FournisseurMeta
        return FournisseurMeta()
    elif f == 'twilio':
        from agent.providers.twilio import FournisseurTwilio
        return FournisseurTwilio()
    raise ValueError(f"WHATSAPP_PROVIDER invalide: '{f}'. Utilise: meta ou twilio")
