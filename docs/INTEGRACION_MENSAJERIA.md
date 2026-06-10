# Integración del chatbot Winback con WhatsApp o Telegram (RF-04)

> Proyecto Reactivaciones Winback · Coomeva Medicina Prepagada · Proveedor ICESI
> Estado actual: el chatbot es un **flujo determinista** (máquina de estados) expuesto en
> `POST /chatbot/mensaje` y consumido solo por el widget React. Esta guía explica cómo
> exponer ese **mismo flujo** en un canal de mensajería real.

---

## 1. ¿Cuál integrar primero? Telegram vs WhatsApp

| Criterio | **Telegram** | **WhatsApp (Cloud API de Meta)** |
|---|---|---|
| Crear el bot | Token gratis en ~2 min con `@BotFather` | App en Meta for Developers + número + verificación de negocio |
| Verificación de identidad | No requiere | Requiere **Meta Business** verificado |
| Mensajes salientes (proactivos) | Libres | Solo con **plantillas pre-aprobadas** por Meta |
| Ventana de conversación | Sin restricción | Regla de **24 horas** de atención al cliente |
| Costo | Gratis | Gratis hasta cierto volumen, luego por conversación |
| Tiempo a "hola mundo" | Minutos | Días (aprobaciones) |
| Relevancia para el negocio | Media (canal no usado por Coomeva) | **Alta** (40% de las gestiones históricas son por WhatsApp) |

**Recomendación:** implementar **Telegram primero** como prueba de concepto end-to-end
(es el camino de menor fricción), y reutilizar exactamente el mismo motor de flujo para
**WhatsApp** cuando el negocio habilite la cuenta Meta Business. La arquitectura propuesta
deja ambos canales sobre el mismo núcleo, así que migrar es trivial.

---

## 2. Refactor previo (común a ambos canales)

Hoy la lógica del flujo vive dentro de `api/routers/chatbot.py` (el diccionario `FLUJO`).
Para no duplicarla, primero **extraemos el motor** a un módulo reutilizable.

### Paso 2.1 — Crear `api/services/motor_flujo.py`

```python
# api/services/motor_flujo.py
"""Motor del flujo winback, independiente del canal (web, Telegram, WhatsApp)."""

FLUJO = {
    'inicio': {
        'mensaje': '¡Hola! 👋 Soy el asistente de Coomeva MP. ¿Te gustaría conocer cómo '
                   'retomar tu plan de salud con beneficios exclusivos?',
        'opciones': ['Sí, cuéntame más', 'No gracias'],
        'siguiente': {'Sí, cuéntame más': 'tratamiento_datos', 'No gracias': 'despedida'}
    },
    'tratamiento_datos': {
        'mensaje': 'Para continuar, necesito tu autorización para el tratamiento de tus '
                   'datos personales según nuestra política. ¿Autorizas?',
        'opciones': ['Autorizo', 'No autorizo'],
        'siguiente': {'Autorizo': 'calentamiento', 'No autorizo': 'despedida'}
    },
    'calentamiento': {
        'mensaje': '¡Perfecto! Sabemos que tuviste un plan con nosotros. Actualmente '
                   'tenemos ofertas especiales para clientes como tú. ¿Qué te llevó a cancelar?',
        'opciones': ['El precio', 'La cobertura', 'Me fui a otra empresa', 'Otro motivo'],
        'siguiente': {'El precio': 'interes', 'La cobertura': 'interes',
                      'Me fui a otra empresa': 'interes', 'Otro motivo': 'interes'}
    },
    'interes': {
        'mensaje': 'Entiendo, ¡gracias por contarnos! Tenemos planes desde $180.000/mes '
                   'con cobertura completa. ¿Te interesa hablar con uno de nuestros asesores?',
        'opciones': ['Sí, quiero que me llamen', 'Por ahora no'],
        'siguiente': {'Sí, quiero que me llamen': 'entrega_asesor', 'Por ahora no': 'despedida'}
    },
    'entrega_asesor': {
        'mensaje': '✅ ¡Excelente! Un asesor de Coomeva te contactará en las próximas 2 horas. '
                   'Tu caso fue asignado como PROSPECTO LISTO.',
        'opciones': [], 'siguiente': {}
    },
    'despedida': {
        'mensaje': '¡Gracias por tu tiempo! Si cambias de opinión, escríbenos cuando quieras. 👋',
        'opciones': [], 'siguiente': {}
    },
}


def avanzar(estado_actual: str, opcion_elegida: str | None):
    """Devuelve el siguiente nodo del flujo dado el estado y la opción elegida."""
    nodo = FLUJO.get(estado_actual, FLUJO['inicio'])
    if opcion_elegida and opcion_elegida in nodo.get('siguiente', {}):
        siguiente = nodo['siguiente'][opcion_elegida]
        n = FLUJO[siguiente]
        return {'estado': siguiente, 'mensaje': n['mensaje'],
                'opciones': n['opciones'], 'es_final': len(n['opciones']) == 0}
    inicio = FLUJO['inicio']
    return {'estado': 'inicio', 'mensaje': inicio['mensaje'],
            'opciones': inicio['opciones'], 'es_final': False}
```

### Paso 2.2 — Adelgazar `api/routers/chatbot.py`

```python
# api/routers/chatbot.py
from fastapi import APIRouter
from pydantic import BaseModel
from services.motor_flujo import avanzar

router = APIRouter()

class MensajeRequest(BaseModel):
    estado_actual: str
    opcion_elegida: str | None = None

@router.post("/mensaje")
def procesar_mensaje(req: MensajeRequest):
    return avanzar(req.estado_actual, req.opcion_elegida)
```

> Crea también `api/services/__init__.py` vacío para que el paquete sea importable.

El widget React sigue funcionando igual: no cambia el contrato del endpoint.

---

## 3. Integración con **Telegram** (camino recomendado)

### Paso 3.1 — Crear el bot y obtener el token
1. En Telegram, abre un chat con **`@BotFather`**.
2. Envía `/newbot`, elige un nombre visible (ej. *Coomeva Winback*) y un username que
   termine en `bot` (ej. `coomeva_winback_bot`).
3. BotFather te devuelve un **token** como `123456789:AAH...`. Guárdalo.

### Paso 3.2 — Guardar el token como variable de entorno
Nunca lo escribas en el código. En PowerShell (Windows), para la sesión actual:
```powershell
$env:TELEGRAM_BOT_TOKEN = "123456789:AAH..."
```
Para producción (Render) agrégalo como *Environment Variable* en el dashboard.

### Paso 3.3 — Instalar dependencias
```powershell
.\venv\Scripts\pip.exe install httpx
```
`httpx` basta: hablaremos con la **HTTP Bot API** de Telegram por webhook, sin librerías
pesadas. (Alternativa: `python-telegram-bot`, pero httpx mantiene el stack mínimo.)

### Paso 3.4 — Crear el router del webhook `api/routers/telegram.py`

```python
# api/routers/telegram.py
import os
import httpx
from fastapi import APIRouter, Request
from services.motor_flujo import avanzar

router = APIRouter()
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
API = f"https://api.telegram.org/bot{TOKEN}"

# Estado de conversación por usuario (MVP en memoria; en prod usar Redis o tabla SQLite)
SESIONES: dict[int, str] = {}


async def _enviar(chat_id: int, texto: str, opciones: list[str]):
    """Envía un mensaje con teclado de respuesta (botones)."""
    teclado = {"keyboard": [[{"text": o}] for o in opciones],
               "resize_keyboard": True, "one_time_keyboard": True} if opciones else {"remove_keyboard": True}
    async with httpx.AsyncClient() as client:
        await client.post(f"{API}/sendMessage",
                          json={"chat_id": chat_id, "text": texto, "reply_markup": teclado})


@router.post("/webhook")
async def webhook(request: Request):
    update = await request.json()
    msg = update.get("message")
    if not msg or "text" not in msg:
        return {"ok": True}

    chat_id = msg["chat"]["id"]
    texto = msg["text"].strip()

    # /start (o primer contacto) reinicia el flujo
    if texto == "/start" or chat_id not in SESIONES:
        SESIONES[chat_id] = "inicio"
        nodo = avanzar("inicio", None)
    else:
        nodo = avanzar(SESIONES[chat_id], texto)

    SESIONES[chat_id] = nodo["estado"]
    await _enviar(chat_id, nodo["mensaje"], nodo["opciones"])

    # Aquí podrías persistir el lead cuando es_final y estado == 'entrega_asesor'
    if nodo["es_final"] and nodo["estado"] == "entrega_asesor":
        # TODO: insertar gestión en gestiones_reactivacion (canal 'telegram', resultado 'interesado')
        pass
    return {"ok": True}
```

### Paso 3.5 — Registrar el router en `api/main.py`
```python
from routers import prospectos, metricas, arquetipos, chatbot, modelo, analitica, telegram
...
app.include_router(telegram.router, prefix="/telegram", tags=["telegram"])
```

### Paso 3.6 — Exponer tu API local con un túnel HTTPS
Telegram solo entrega webhooks a URLs HTTPS públicas. En local usa **ngrok**:
```powershell
# Instala ngrok (https://ngrok.com/download) y autentícate, luego:
ngrok http 8000
```
Copia la URL `https://xxxx.ngrok-free.app`. En producción usa directamente la URL de Render.

### Paso 3.7 — Registrar el webhook en Telegram
Una sola vez, reemplazando token y URL:
```powershell
curl "https://api.telegram.org/bot$($env:TELEGRAM_BOT_TOKEN)/setWebhook?url=https://xxxx.ngrok-free.app/telegram/webhook"
```
Verifica con:
```powershell
curl "https://api.telegram.org/bot$($env:TELEGRAM_BOT_TOKEN)/getWebhookInfo"
```

### Paso 3.8 — Probar
1. Levanta la API: `cd api ; uvicorn main:app --reload --port 8000`
2. Mantén `ngrok` corriendo.
3. En Telegram, abre tu bot y envía `/start`.
4. Debes ver el saludo y los botones; al pulsar opciones, el flujo avanza hasta
   "PROSPECTO LISTO". 🎉

---

## 4. Integración con **WhatsApp** (ruta productiva)

Mismo motor (`avanzar`), distinto transporte. Resumen de lo adicional:

1. **Cuenta y app**: crea una app en [Meta for Developers](https://developers.facebook.com/),
   agrega el producto *WhatsApp*, asóciala a una **Meta Business** verificada y registra un
   número de teléfono. Obtienes `PHONE_NUMBER_ID` y un `ACCESS_TOKEN`.
2. **Webhook**: configura la URL `https://.../whatsapp/webhook` y un `VERIFY_TOKEN`
   propio. Meta hace primero un `GET` de verificación (debes devolver el `hub.challenge`)
   y luego envía los mensajes por `POST`.
3. **Plantillas**: para iniciar conversación de forma proactiva (campaña winback saliente)
   necesitas **plantillas aprobadas** por Meta. Dentro de la ventana de 24h tras un mensaje
   del usuario puedes responder libremente con texto/botones.
4. **Enviar mensajes**: `POST https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages`
   con `Authorization: Bearer {ACCESS_TOKEN}`, usando `interactive`/`button` para replicar
   las opciones del flujo.

Esqueleto del router (análogo a Telegram):

```python
# api/routers/whatsapp.py
import os, httpx
from fastapi import APIRouter, Request, Response
from services.motor_flujo import avanzar

router = APIRouter()
TOKEN = os.environ["WHATSAPP_TOKEN"]
PHONE_ID = os.environ["WHATSAPP_PHONE_ID"]
VERIFY = os.environ["WHATSAPP_VERIFY_TOKEN"]
SESIONES: dict[str, str] = {}

@router.get("/webhook")
def verificar(request: Request):
    p = request.query_params
    if p.get("hub.mode") == "subscribe" and p.get("hub.verify_token") == VERIFY:
        return Response(content=p.get("hub.challenge"), media_type="text/plain")
    return Response(status_code=403)

@router.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
    except (KeyError, IndexError):
        return {"ok": True}              # eventos de estado, no mensajes
    wa_id = msg["from"]
    texto = msg.get("text", {}).get("body", "").strip()
    estado = SESIONES.get(wa_id, "inicio")
    nodo = avanzar("inicio", None) if texto.lower() in ("hola", "/start") or wa_id not in SESIONES \
        else avanzar(estado, texto)
    SESIONES[wa_id] = nodo["estado"]
    async with httpx.AsyncClient() as c:
        await c.post(
            f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages",
            headers={"Authorization": f"Bearer {TOKEN}"},
            json={"messaging_product": "whatsapp", "to": wa_id,
                  "type": "text", "text": {"body": nodo["mensaje"]}})
    return {"ok": True}
```

---

## 5. Pendientes antes de productivizar (ambos canales)

- **Persistencia de sesión**: hoy `SESIONES` es un dict en memoria → se pierde al reiniciar
  y no escala horizontalmente. Migrar a Redis o a una tabla `sesiones_chat` en SQLite/Postgres.
- **Registrar el lead**: cuando el flujo llega a `entrega_asesor`, insertar una fila en
  `gestiones_reactivacion` (`canal_contacto='telegram'|'whatsapp'`, `resultado='interesado'`)
  y, si se cruza con `prospectos` por teléfono, marcar el `estado_gestion`.
- **Seguridad del webhook**: validar firma (Telegram: `secret_token` en `setWebhook`;
  WhatsApp: cabecera `X-Hub-Signature-256`).
- **Habeas Data**: el nodo `tratamiento_datos` ya pide autorización; registrar el
  consentimiento con fecha/canal para cumplimiento legal (Ley 1581 de 2012).
- **Idempotencia**: ambos proveedores reintentan webhooks; usar el `message_id` para no
  procesar duplicados.
