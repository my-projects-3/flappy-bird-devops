from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import sqlite3
from typing import List
import uvicorn
from pathlib import Path

app = FastAPI(title="Flappy Bird Leaderboard API")

# Configuration des templates
templates = Jinja2Templates(directory="templates")

# Modèle Pydantic pour la validation des données
class Score(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    score: int = Field(..., ge=0, le=1000000)  # Limite de score à 1,000,000

class DeleteUser(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

# Initialisation de la base de données SQLite
def init_db():
    conn = sqlite3.connect('scores.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scores
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  score INTEGER NOT NULL,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                  UNIQUE(name))''')
    conn.commit()
    conn.close()

# Route pour la page d'accueil avec le leaderboard
@app.get("/", response_class=HTMLResponse)
async def read_root():
    conn = sqlite3.connect('scores.db')
    c = conn.cursor()
    c.execute("SELECT name, score FROM scores ORDER BY score DESC LIMIT 10")
    scores = [{"name": row[0], "score": row[1]} for row in c.fetchall()]
    conn.close()
    return templates.TemplateResponse("leaderboard.html", {"request": {}, "scores": scores})

# Endpoint pour enregistrer un score
@app.post("/score")
async def add_score(score: Score):
    conn = sqlite3.connect('scores.db')
    c = conn.cursor()
    
    # Vérifier si l'utilisateur existe déjà
    c.execute("SELECT score FROM scores WHERE name = ?", (score.name,))
    existing_score = c.fetchone()
    
    if existing_score:
        # Si le nouveau score est meilleur, mettre à jour
        if score.score > existing_score[0]:
            c.execute("UPDATE scores SET score = ?, timestamp = CURRENT_TIMESTAMP WHERE name = ?", 
                     (score.score, score.name))
    else:
        # Nouvel utilisateur, insérer le score
        c.execute("INSERT INTO scores (name, score) VALUES (?, ?)", (score.name, score.score))
    
    conn.commit()
    conn.close()
    return {"message": "Score enregistré avec succès"}

# Endpoint pour supprimer un utilisateur
@app.delete("/user/{name}")
async def delete_user(name: str):
    try:
        conn = sqlite3.connect('scores.db')
        c = conn.cursor()
        
        # Vérifier si l'utilisateur existe
        c.execute("SELECT name FROM scores WHERE name = ?", (name,))
        if not c.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Supprimer l'utilisateur
        c.execute("DELETE FROM scores WHERE name = ?", (name,))
        conn.commit()
        conn.close()
        return {"status": "success", "message": f"Utilisateur {name} supprimé avec succès"}
    except Exception as e:
        if conn:
            conn.close()
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint pour obtenir le leaderboard (API)
@app.get("/leaderboard", response_model=List[dict])
async def get_leaderboard():
    conn = sqlite3.connect('scores.db')
    c = conn.cursor()
    c.execute("SELECT name, score FROM scores ORDER BY score DESC LIMIT 10")
    scores = [{"name": row[0], "score": row[1]} for row in c.fetchall()]
    conn.close()
    return scores

# Endpoint pour obtenir le meilleur score d'un utilisateur
@app.get("/best-score/{name}")
async def get_best_score(name: str):
    conn = sqlite3.connect('scores.db')
    c = conn.cursor()
    c.execute("SELECT score FROM scores WHERE name = ?", (name,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return {"name": name, "best_score": result[0]}
    else:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

# Initialisation de la base de données au démarrage
init_db()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 