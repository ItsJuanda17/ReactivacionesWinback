# RF-04 — Flujo chatbot simulado (sin Twilio)
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

FLUJO = {
    'inicio': {
        'mensaje': '¡Hola! 👋 Soy el asistente de Coomeva MP. ¿Te gustaría conocer cómo retomar tu plan de salud con beneficios exclusivos?',
        'opciones': ['Sí, cuéntame más', 'No gracias'],
        'siguiente': {'Sí, cuéntame más': 'tratamiento_datos', 'No gracias': 'despedida'}
    },
    'tratamiento_datos': {
        'mensaje': 'Para continuar, necesito tu autorización para el tratamiento de tus datos personales según nuestra política. ¿Autorizas?',
        'opciones': ['Autorizo', 'No autorizo'],
        'siguiente': {'Autorizo': 'calentamiento', 'No autorizo': 'despedida'}
    },
    'calentamiento': {
        'mensaje': '¡Perfecto! Sabemos que tuviste un plan con nosotros. Actualmente tenemos ofertas especiales para clientes como tú. ¿Qué te llevó a cancelar?',
        'opciones': ['El precio', 'La cobertura', 'Me fui a otra empresa', 'Otro motivo'],
        'siguiente': {'El precio': 'interes', 'La cobertura': 'interes', 'Me fui a otra empresa': 'interes', 'Otro motivo': 'interes'}
    },
    'interes': {
        'mensaje': 'Entiendo, ¡gracias por contarnos! Tenemos planes desde $180.000/mes con cobertura completa. ¿Te interesa hablar con uno de nuestros asesores?',
        'opciones': ['Sí, quiero que me llamen', 'Por ahora no'],
        'siguiente': {'Sí, quiero que me llamen': 'entrega_asesor', 'Por ahora no': 'despedida'}
    },
    'entrega_asesor': {
        'mensaje': '✅ ¡Excelente! Un asesor de Coomeva te contactará en las próximas 2 horas. Tu caso fue asignado como PROSPECTO LISTO.',
        'opciones': [],
        'siguiente': {}
    },
    'despedida': {
        'mensaje': '¡Gracias por tu tiempo! Si cambias de opinión, escríbenos cuando quieras. 👋',
        'opciones': [],
        'siguiente': {}
    }
}


class MensajeRequest(BaseModel):
    estado_actual: str
    opcion_elegida: str | None = None


@router.post("/mensaje")
def procesar_mensaje(req: MensajeRequest):
    estado = req.estado_actual
    nodo = FLUJO.get(estado, FLUJO['inicio'])

    if req.opcion_elegida and req.opcion_elegida in nodo.get('siguiente', {}):
        siguiente_estado = nodo['siguiente'][req.opcion_elegida]
        nodo_siguiente = FLUJO[siguiente_estado]
        return {
            'estado': siguiente_estado,
            'mensaje': nodo_siguiente['mensaje'],
            'opciones': nodo_siguiente['opciones'],
            'es_final': len(nodo_siguiente['opciones']) == 0
        }

    return {
        'estado': 'inicio',
        'mensaje': FLUJO['inicio']['mensaje'],
        'opciones': FLUJO['inicio']['opciones'],
        'es_final': False
    }
