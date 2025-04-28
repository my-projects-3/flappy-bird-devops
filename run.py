import subprocess
import sys

def run_game():
    subprocess.run([sys.executable, "game.py"])

if __name__ == "__main__":
    # Démarrer uniquement le jeu sans le backend
    print("Lancement du jeu Flappy Bird avec MongoDB Atlas...")
    run_game()