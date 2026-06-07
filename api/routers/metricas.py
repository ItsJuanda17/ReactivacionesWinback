# GET /metricas — comparación de modelos (RF-02)
import json
from fastapi import APIRouter, HTTPException
from config import MODELS_DIR

router = APIRouter()


@router.get("")
def obtener_metricas():
    """Devuelve las métricas comparativas (accuracy, precision, recall, f1, roc_auc)."""
    path = MODELS_DIR / 'metricas.json'
    if not path.exists():
        raise HTTPException(404, "Métricas no disponibles. Ejecuta ml/train_models.py primero.")
    with open(path, encoding='utf-8') as f:
        return json.load(f)
