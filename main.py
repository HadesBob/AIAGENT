from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Wczytanie zmiennych środowiskowych (np. GOOGLE_API_KEY) z pliku .env
load_dotenv()

app = FastAPI(
    title="Generator Diet AI",
    description="API do generowania spersonalizowanych diet z użyciem Google Gemini",
    version="1.0.0"
)

# Przykładowy schemat Pydantic dla danych wejściowych
class ProfilStartowy(BaseModel):
    waga: float
    cel: str

@app.get("/")
def sprawdz_status():
    return {"status": "działa", "wiadomosc": "API Generatora Diet jest gotowe!"}

@app.post("/test-profilu")
def test_pydantic(profil: ProfilStartowy):
    return {
        "wiadomosc": "Odebrano dane!", 
        "twoja_waga": profil.waga, 
        "twoj_cel": profil.cel
    }