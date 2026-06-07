# GET /arquetipos — perfiles de los clusters K-Means (RF-03)
import json
from fastapi import APIRouter, HTTPException
from config import MODELS_DIR

router = APIRouter()


@router.get("")
def obtener_arquetipos():
    """Devuelve los 4 arquetipos comerciales con su perfil agregado."""
    path = MODELS_DIR / 'arquetipos.json'
    if not path.exists():
        raise HTTPException(404, "Arquetipos no disponibles. Ejecuta ml/clustering.py primero.")
    with open(path, encoding='utf-8') as f:
        return json.load(f)
