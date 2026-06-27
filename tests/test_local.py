import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()
from agent.brain import generer_reponse
from agent.memory import initialiser_db, sauvegarder_message, obtenir_historique, effacer_historique

TELEPHONE_TEST = 'test-local-sefa'

async def main():
    await initialiser_db()
    print()
    print('=' * 55)
    print('   Sefa Bien-etre - Test Local')
    print('   Agent de soutien en sante mentale')
    print('=' * 55)
    print("  Commandes : 'effacer' | 'quitter'")
    print('-' * 55)
    print()
    while True:
        try:
            message = input('Toi   : ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nTest termine.'); break
        if not message: continue
        if message.lower() == 'quitter': print('Test termine.'); break
        if message.lower() == 'effacer':
            await effacer_historique(TELEPHONE_TEST)
            print('[Historique efface]'); continue
        historique = await obtenir_historique(TELEPHONE_TEST)
        print('Sefa  : ', end='', flush=True)
        reponse = await generer_reponse(message, historique)
        print(reponse, '\n')
        await sauvegarder_message(TELEPHONE_TEST, 'user', message)
        await sauvegarder_message(TELEPHONE_TEST, 'assistant', reponse)

if __name__ == '__main__':
    asyncio.run(main())
