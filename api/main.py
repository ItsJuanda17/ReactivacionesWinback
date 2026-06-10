import os
import sqlite3
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import DB_PATH
from routers import prospectos, metricas, arquetipos, chatbot, modelo, analitica, gestiones

# Orígenes permitidos: por defecto el frontend local (Vite). En prod, define
# CORS_ORIGINS con los dominios reales separados por coma (ej. el de Vercel).
_DEFAULT_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
ALLOWED_ORIGINS = [
    o.strip() for o in os.environ.get("CORS_ORIGINS", _DEFAULT_ORIGINS).split(",") if o.strip()
]

TABLAS_REQUERIDAS = {
    'prospectos', 'utilizaciones', 'nps_historial',
    'manifestaciones', 'siniestralidad', 'gestiones_reactivacion',
}


def _verificar_base_de_datos() -> None:
    """Falla rápido y con un mensaje claro si el pipeline de datos no se ha corrido.

    Evita el 500 críptico 'no such table: prospectos': SQLite crea un archivo .db
    vacío al conectarse, así que la única forma de saber que faltan datos es revisar
    las tablas explícitamente al arrancar.
    """
    if not DB_PATH.exists():
        existentes = set()
    else:
        conn = sqlite3.connect(DB_PATH)
        try:
            existentes = {
                r[0] for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
        finally:
            conn.close()

    faltantes = TABLAS_REQUERIDAS - existentes
    if faltantes:
        sys.exit(
            "\n[ERROR DE ARRANQUE] La base de datos no tiene las tablas requeridas: "
            f"{', '.join(sorted(faltantes))}.\n"
            f"  Base esperada: {DB_PATH}\n"
            "  Ejecuta el pipeline de datos desde la raíz del repo antes de levantar la API:\n"
            "    python data/generate_synthetic.py\n"
            "    python ml/build_features.py\n"
            "    python ml/train_models.py\n"
            "    python ml/clustering.py\n"
            "    python ml/explainability.py\n"
        )


_verificar_base_de_datos()

app = FastAPI(title="Winback MVP API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prospectos.router, prefix="/prospectos", tags=["prospectos"])
app.include_router(metricas.router, prefix="/metricas", tags=["metricas"])
app.include_router(arquetipos.router, prefix="/arquetipos", tags=["arquetipos"])
app.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])
app.include_router(modelo.router, prefix="/modelo", tags=["modelo"])
app.include_router(analitica.router, prefix="/analitica", tags=["analitica"])
app.include_router(gestiones.router, prefix="/gestiones", tags=["gestiones"])


@app.get("/")
def root():
    return {"service": "Winback MVP API", "version": "1.0", "docs": "/docs"}
