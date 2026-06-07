# Winback MVP — Coomeva Medicina Prepagada

MVP funcional del **Proyecto Reactivaciones Winback** (requerimiento MP-FT-1358, proveedor ICESI).
Demuestra un pipeline completo de reactivación de clientes desertados: datos sintéticos →
modelos predictivos → arquetipos → explicabilidad → API → dashboard y chatbot.

**Costo total: $0** (stack 100% gratuito y open source).

---

## Arquitectura

```
Datos sintéticos (Faker)  →  Capa ML (scikit-learn / XGBoost / SHAP)
        │                              │
        ▼                              ▼
   SQLite (winback.db)          modelos .pkl + JSON
        └──────────────┬───────────────┘
                       ▼
              API FastAPI (Python)
                       │
        ┌──────────────┴──────────────┐
        ▼                              ▼
 Dashboard React + Recharts      Chatbot Widget React
```

## Stack

| Componente | Tecnología |
|---|---|
| ML / API | Python 3.11+ · FastAPI |
| Modelos | scikit-learn · XGBoost |
| Explicabilidad | SHAP |
| Datos sintéticos | Faker · pandas · numpy |
| Base de datos | SQLite |
| Frontend | React 18 · Vite · Recharts |
| Despliegue | Render (backend) · Vercel (frontend) |

## Requisitos funcionales cubiertos

- **RF-01** Modelo predictivo de probabilidad de reactivación.
- **RF-02** Comparación de múltiples modelos (LogReg, RandomForest, XGBoost).
- **RF-03** Segmentación en arquetipos (K-Means).
- **RF-04** Prototipo de chatbot conversacional (flujo winback).
- **RF-05** Explicabilidad del modelo (SHAP).

---

## Ejecución local (demo instantánea)

```bash
# 1. Entorno
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r api/requirements.txt

# 2. Generar datos, consolidar y entrenar modelos
python data/generate_synthetic.py     # 6 tablas sintéticas
python ml/build_features.py           # dataset analítico consolidado (RF-01)
python ml/train_models.py             # entrena y compara modelos (RF-02)
python ml/clustering.py               # arquetipos con estrategia (RF-03)
python ml/explainability.py           # importancia SHAP (RF-05)

# 3. Levantar API
cd api && uvicorn main:app --reload --port 8000

# 4. Levantar frontend (otro terminal)
cd frontend && npm install && npm run dev
# → http://localhost:5173
```

API Docs (Swagger): http://localhost:8000/docs

---

## Estructura del repositorio

```
winback-mvp/
├── .claude/         # Plan maestro e instrucciones para Claude Code
├── data/            # Generador de datos sintéticos + SQLite
├── ml/              # Entrenamiento, clustering y explicabilidad
├── api/             # FastAPI (routers: prospectos, metricas, arquetipos, chatbot)
├── frontend/        # React + Vite dashboard y chatbot
└── README.md
```

Frontend (multipágina): Landing · Dashboard (KPIs, comparación de modelos, ranking
con filtros) · Arquetipos · Modelo (métricas, SHAP, ficha técnica) · Chatbot.

Documentación metodológica completa (RF-05) en `docs/METODOLOGIA.md`.
