from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import prospectos, metricas, arquetipos, chatbot, modelo, analitica

app = FastAPI(title="Winback MVP API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En prod: dominio Vercel específico
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prospectos.router, prefix="/prospectos", tags=["prospectos"])
app.include_router(metricas.router, prefix="/metricas", tags=["metricas"])
app.include_router(arquetipos.router, prefix="/arquetipos", tags=["arquetipos"])
app.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])
app.include_router(modelo.router, prefix="/modelo", tags=["modelo"])
app.include_router(analitica.router, prefix="/analitica", tags=["analitica"])


@app.get("/")
def root():
    return {"service": "Winback MVP API", "version": "1.0", "docs": "/docs"}
