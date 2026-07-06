# 💙 Sefa Bien-être

**Agent IA de soutien en santé mentale, accessible via WhatsApp, pour l'Afrique de l'Ouest.**

Sefa Bien-être permet à toute personne disposant de WhatsApp d'échanger avec un assistant IA bienveillant, disponible pour écouter, orienter et accompagner sur des questions de bien-être mental — sans barrière d'accès technique ou financière.

##  Le problème résolu

L'accès à un premier niveau de soutien en santé mentale reste limité en Afrique de l'Ouest, que ce soit par manque de structures, de moyens, ou simplement de premier contact accessible à tout moment. Sefa Bien-être utilise un canal déjà présent dans la vie quotidienne — WhatsApp — pour offrir une écoute IA immédiate, en français.

##  Comment ça fonctionne

1. L'utilisateur envoie un message via WhatsApp au numéro dédié
2. L'agent IA (Groq / Llama 3.3 70B) analyse la demande et répond de façon empathique et adaptée
3. L'historique de conversation est conservé pour assurer un suivi cohérent dans le temps

##  Stack technique

- **Backend** : FastAPI (Python)
- **IA** : Groq API (Llama 3.3 70B)
- **Base de données** : SQLite (migration vers PostgreSQL prévue pour la persistance long terme)
- **Canal utilisateur** : Meta WhatsApp Cloud API
- **Déploiement** : Render

##  État actuel du projet

- ✅ Agent déployé en production, opérationnel sur WhatsApp (`+221 78 896 28 56`)
- ✅ Onboarding Meta Business finalisé, génération de token système utilisateur
- Migration SQLite → PostgreSQL pour une persistance robuste de l'historique des conversations

##  Installation et test local

<details>
<summary>Cliquer pour déplier les instructions</summary>

### Prérequis
- Python 3.11+
- Un compte [Groq](https://console.groq.com) pour la clé API
- Un compte Meta for Developers avec accès WhatsApp Cloud API

### Installation
```bash
git clone https://github.com/kine-seye/sefa-agent
cd sefa-agent
python3 -m venv venv
source venv/bin/activate  # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration
Renseigne tes clés API (Groq, WhatsApp Cloud API) dans le fichier de configuration approprié.

### Lancement
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

</details>

##  Auteure

**Kiné Seye** — Data Scientist & AI Developer, Dakar, Sénégal
[LinkedIn](https://www.linkedin.com/in/kine-seye-b513b13ba) · [GitHub](https://github.com/kine-seye)
