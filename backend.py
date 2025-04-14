from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Score(BaseModel):
    name: str
    score: int

@app.post("/score")
def receive_score(score: Score):
    print(f"Received: {score.name} - {score.score}")
    return {"status": "ok"}
