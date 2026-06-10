# RF-04 — Flujo chatbot (máquina de estados servida desde services/motor_flujo.py)
from fastapi import APIRouter
from pydantic import BaseModel

from services.motor_flujo import avanzar
from services import sesiones

router = APIRouter()

# Disparadores que reinician la conversación desde el saludo inicial.
DISPARADORES_INICIO = {'/start', 'start', 'hola', 'inicio', 'menu'}


class MensajeRequest(BaseModel):
    estado_actual: str
    opcion_elegida: str | None = None


@router.post("/mensaje")
def procesar_mensaje(req: MensajeRequest):
    """Turno *stateless* del flujo (usado por el widget React, que guarda su estado)."""
    return avanzar(req.estado_actual, req.opcion_elegida)


class ConversarRequest(BaseModel):
    user_id: str                   # id del usuario en el canal (chat_id de Telegram, wa_id, etc.)
    texto: str                     # texto entrante del usuario
    canal: str = 'telegram'        # telegram | whatsapp | ...


@router.post("/conversar")
def conversar(req: ConversarRequest):
    """Turno *stateful*: la API recuerda el estado por usuario.

    Pensado para que N8N sea tonto: solo reenvía `{user_id, texto, canal}` y aquí se
    resuelve el estado, se avanza el flujo y se persiste el nuevo estado.
    """
    sesiones.asegurar_tabla()
    estado_previo = sesiones.obtener_estado(req.user_id)
    texto = req.texto.strip()

    if estado_previo is None or texto.lower() in DISPARADORES_INICIO:
        nodo = avanzar('inicio', None)            # saludo inicial
    else:
        nodo = avanzar(estado_previo, texto)      # avanza según la opción elegida

    sesiones.guardar_estado(req.user_id, req.canal, nodo['estado'])
    return nodo
