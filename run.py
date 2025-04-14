import subprocess
import sys
import time
import webbrowser
from threading import Thread

def run_backend():
    subprocess.run([sys.executable, "fastapi_backend.py"])

def run_game():
    subprocess.run([sys.executable, "game.py"])

if __name__ == "__main__":
    # Démarrer le backend dans un thread séparé
    backend_thread = Thread(target=run_backend)
    backend_thread.daemon = True  # Le thread se terminera quand le programme principal se termine
    backend_thread.start()

    # Attendre un peu pour que le backend démarre
    time.sleep(2)

    # Ouvrir le navigateur avec l'interface web du leaderboard
    webbrowser.open('http://localhost:8000')

    # Démarrer le jeu
    run_game() 