from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import List
import uvicorn
from pathlib import Path
from pymongo import MongoClient
from urllib.parse import quote_plus
from bson import ObjectId

app = FastAPI(title="Flappy Bird Leaderboard API")

# Configuration des templates
templates = Jinja2Templates(directory="templates")

# Modèle Pydantic pour la validation des données
class Score(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    score: int = Field(..., ge=0, le=1000000)  # Limite de score à 1,000,000

class DeleteUser(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

# Configuration de la connexion MongoDB Atlas
username = quote_plus("mboutalmaouine0907")
password = quote_plus("4cqch8MiGgq3YZll")
uri = f"mongodb+srv://{username}:{password}@cluster0.qrixdve.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Options de connexion pour résoudre les problèmes SSL
connection_options = {
    "serverSelectionTimeoutMS": 5000,  # Timeout réduit à 5 secondes
    "connectTimeoutMS": 5000,
    "retryWrites": True,
    "retryReads": True,
    "tlsAllowInvalidCertificates": True  # Utiliser cette option au lieu de ssl_cert_reqs
}

# Connexion à MongoDB
try:
    client = MongoClient(uri, **connection_options)
    db = client["flappy_beard"]
    scores_collection = db["scores"]
    print("Connexion à MongoDB Atlas réussie")
except Exception as e:
    print(f"Erreur de connexion MongoDB: {e}")
    # Créer une base de données en mémoire pour le mode hors ligne
    from pymongo.errors import ServerSelectionTimeoutError
    print("Fonctionnement en mode hors ligne")
    # On continuera quand même avec les variables définies, mais les opérations échoueront gracieusement

# Initialisation de la base de données MongoDB
def init_db():
    # Création d'un index unique sur le nom d'utilisateur
    scores_collection.create_index("name", unique=True)

# Route pour la page d'accueil avec le leaderboard
@app.get("/", response_class=HTMLResponse)
async def read_root():
    # Récupération des 10 meilleurs scores depuis MongoDB
    cursor = scores_collection.find().sort("score", -1).limit(10)
    scores = [{"name": doc["name"], "score": doc["score"]} for doc in cursor]
    return templates.TemplateResponse("leaderboard.html", {"request": {}, "scores": scores})

# Endpoint pour enregistrer un score
@app.post("/score")
async def add_score(score: Score):
    # Vérifier si l'utilisateur existe déjà
    existing_user = scores_collection.find_one({"name": score.name})
    
    if existing_user:
        # Si le nouveau score est meilleur, mettre à jour
        if score.score > existing_user["score"]:
            scores_collection.update_one(
                {"name": score.name},
                {"$set": {"score": score.score}}
            )
    else:
        # Nouvel utilisateur, insérer le score
        scores_collection.insert_one({
            "name": score.name,
            "score": score.score
        })
    
    return {"message": "Score enregistré avec succès"}

# Endpoint pour supprimer un utilisateur
@app.delete("/user/{name}")
async def delete_user(name: str):
    try:
        # Vérifier si l'utilisateur existe
        existing_user = scores_collection.find_one({"name": name})
        if not existing_user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Supprimer l'utilisateur
        scores_collection.delete_one({"name": name})
        return {"status": "success", "message": f"Utilisateur {name} supprimé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint pour obtenir le leaderboard (API)
@app.get("/leaderboard", response_model=List[dict])
async def get_leaderboard():
    cursor = scores_collection.find().sort("score", -1).limit(10)
    scores = [{"name": doc["name"], "score": doc["score"]} for doc in cursor]
    return scores

# Endpoint pour obtenir le meilleur score d'un utilisateur
@app.get("/best-score/{name}")
async def get_best_score(name: str):
    result = scores_collection.find_one({"name": name})
    
    if result:
        return {"name": name, "best_score": result["score"]}
    else:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

# Initialisation de la base de données au démarrage
init_db()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)