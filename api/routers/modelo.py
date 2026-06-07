# GET /modelo/importancia-variables — importancia de variables vía SHAP (RF-05)
import json
from fastapi import APIRouter, HTTPException
from config import MODELS_DIR

router = APIRouter()


@router.get("/importancia-variables")
def importancia_variables():
    """Sirve los valores SHAP precalculados (importancia global de variables)."""
    path = MODELS_DIR / 'shap_values.json'
    if not path.exists():
        raise HTTPException(404, "SHAP no disponible. Ejecuta ml/explainability.py primero.")
    with open(path, encoding='utf-8') as f:
        return json.load(f)
