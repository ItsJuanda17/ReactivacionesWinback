"""Rutas compartidas del proyecto, resueltas desde la raíz del repositorio.

Permite levantar la API con `uvicorn main:app` desde el directorio `api/` sin que
las rutas relativas a `data/` y `ml/models/` se rompan.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / 'data' / 'winback.db'
MODELS_DIR = ROOT / 'ml' / 'models'
