# Orquestación con N8N — Campañas Winback automatizadas

> Proyecto Reactivaciones Winback · Coomeva Medicina Prepagada · Proveedor ICESI
> Requerimiento: uso de **N8N** como capa de automatización/orquestación.

---

## 1. ¿Qué rol cumple N8N y qué NO?

N8N es el **director de orquesta**, no el cerebro. Coordina *cuándo* y *a través de qué
canal* ocurren las cosas, pero **no contiene lógica de negocio ni del modelo**.

| Capa | Responsabilidad | Tecnología |
|---|---|---|
| **Cerebro analítico** | Scoring del modelo, priorización, motor del flujo conversacional | API FastAPI (este repo) |
| **Orquestador** | Agendar campañas, enviar mensajes, reintentos, enrutar al asesor, registrar resultados | **N8N** |
| **Canales** | Entregar el mensaje al cliente | WhatsApp Cloud API / Telegram |

**Principio de diseño:** toda decisión ("¿a quién contacto?", "¿qué le respondo?") la
toma la API. N8N solo ejecuta llamadas HTTP y mueve datos entre sistemas. Así, si cambia
el modelo o el flujo, **N8N no se toca**.

### Lógica que se desacopla del código Python hacia N8N
- Agendamiento de campañas (antes requeriría un cron + script propio).
- Envío por cada canal (WhatsApp, Telegram, email, SMS) y sus reintentos / rate-limiting.
- Enrutamiento del lead caliente a un asesor humano (crear tarea en CRM, avisar por Slack).
- Registro de resultados de contacto de vuelta en la base.

---

## 2. Cambios en la API (YA IMPLEMENTADOS)

Para que N8N quede *tonto* (sin lógica de negocio ni estado), la API expone dos cosas:

### 2.1 `POST /gestiones` — cierra el ciclo escribiendo en `gestiones_reactivacion`
Implementado en [`api/routers/gestiones.py`](../api/routers/gestiones.py). Body:
```json
{ "prospecto_id": "...", "canal_contacto": "telegram", "resultado": "interesado",
  "asesor_id": null, "duracion_segundos": null }
```

### 2.2 `POST /chatbot/conversar` — turno **stateful** (la API recuerda el estado)
Implementado en [`api/routers/chatbot.py`](../api/routers/chatbot.py), respaldado por
[`api/services/sesiones.py`](../api/services/sesiones.py) (tabla `sesiones_chat`). Así N8N
solo reenvía `{user_id, texto, canal}` y la API resuelve en qué punto del flujo va cada
usuario. Body:
```json
{ "user_id": "<chat_id de Telegram>", "texto": "Sí, cuéntame más", "canal": "telegram" }
```
Respuesta: `{ estado, mensaje, opciones, es_final }`. Si `user_id` es nuevo o el texto es
`/start`/`hola`, arranca en el saludo inicial.

> La API debe ser **alcanzable por N8N**. Como N8N corre en Docker y la API en el host
> Windows, dentro de los workflows se usa `http://host.docker.internal:8000` (ya verificado).

---

## 3. Instalar N8N on-premise con Docker (YA EJECUTADO — gratis)

El contenedor ya está corriendo de forma persistente (sobrevive reinicios):
```powershell
docker run -d --name n8n-winback -p 5678:5678 `
  -e GENERIC_TIMEZONE="America/Bogota" `
  -e N8N_SECURE_COOKIE=false `
  -v n8n_winback_data:/home/node/.n8n `
  n8nio/n8n
```
- Interfaz: **http://localhost:5678** (la primera vez pide crear un usuario local — owner).
- El volumen `n8n_winback_data` persiste workflows y credenciales.
- Gestión: `docker stop n8n-winback` / `docker start n8n-winback` / `docker logs -f n8n-winback`.

> **Importante sobre Telegram saliente:** un bot de Telegram **solo puede escribir a usuarios
> que ya le hayan hablado**; no puede iniciar chat contra un número de teléfono (eso sí lo
> permite WhatsApp con plantillas). Por eso el **Workflow A** se diseña como *briefing interno*
> al chat del equipo comercial, y el **Workflow B** maneja la conversación entrante real.

---

## 4. Workflow A — Briefing diario al equipo (saliente)

Archivo importable: [`n8n-workflows/workflow_A_briefing_diario.json`](n8n-workflows/workflow_A_briefing_diario.json)

| # | Nodo | Configuración |
|---|---|---|
| 1 | **Schedule Trigger** | Diario 8:00 a.m. |
| 2 | **HTTP Request** | `GET http://host.docker.internal:8000/prospectos?segmento=diamante&limit=20` |
| 3 | **Code** | Arma un texto con el ranking (nombre, ciudad, % prob, teléfono) |
| 4 | **Telegram** | `sendMessage` al chat del equipo comercial (`REEMPLAZAR_CHAT_ID_EQUIPO`) |

La inteligencia ("¿a quién priorizar?") vive en el paso 2: el modelo ya ordenó por
`prob_reactivacion`. N8N solo formatea y publica.

---

## 5. Workflow B — Conversación entrante (reactiva)

Archivo importable: [`n8n-workflows/workflow_B_telegram_entrante.json`](n8n-workflows/workflow_B_telegram_entrante.json)

| # | Nodo | Configuración |
|---|---|---|
| 1 | **Telegram Trigger** | Escucha `message` (n8n registra el webhook con Telegram al activar) |
| 2 | **HTTP Request** | `POST /chatbot/conversar` con `{user_id: chat.id, texto: message.text, canal:'telegram'}` |
| 3 | **Telegram** | Responde `mensaje` + `opciones` al cliente |
| 4 | **IF** | `estado == 'entrega_asesor'` → rama de lead caliente |
| 5a | **HTTP Request** | `POST /gestiones` con `resultado:'interesado'` |
| 5b | **Telegram** | Avisa al asesor (`REEMPLAZAR_CHAT_ID_ASESOR`): "PROSPECTO LISTO" |

> **Estado de sesión: resuelto en la API.** Como `POST /chatbot/conversar` persiste el
> estado por `user_id` en la tabla `sesiones_chat`, N8N **no** necesita Data Store ni Redis.
> La API es la única fuente de verdad del estado conversacional.
>
> **Vínculo Telegram↔prospecto:** en el demo, la rama de lead caliente registra la gestión
> usando el `chat_id` de Telegram como `prospecto_id` (no hay teléfono compartido). En
> producción, al enviar el primer mensaje se guardaría el mapeo `chat_id → prospecto_id`, o
> se pediría al usuario compartir su contacto (botón *request_contact* de Telegram).

---

## 6. Arquitectura resultante

```
                    ┌──────────────── N8N ────────────────┐
   [Cron 8am] ─────►│ Workflow A: campaña saliente         │
                    │   GET /prospectos (modelo prioriza)  │──► WhatsApp/Telegram ──► Cliente
                    │   POST /gestiones (traza intento)    │
                    ├──────────────────────────────────────┤
   Cliente ────────►│ Workflow B: conversación entrante    │
   (responde)       │   POST /chatbot/mensaje (motor_flujo)│──► respuesta al Cliente
                    │   IF entrega_asesor →                │
                    │      POST /gestiones + Slack/CRM      │──► Asesor humano
                    └──────────────────────────────────────┘
                                    │
                                    ▼
                         API FastAPI = cerebro
                  (scoring ML + motor de flujo, este repo)
```

---

## 7. Puesta en marcha — pasos restantes (manuales)

El entorno ya está montado: API con los endpoints nuevos, contenedor `n8n-winback`
corriendo y conectividad contenedor→API verificada. Faltan **3 pasos que requieren tu
intervención** (no se pueden automatizar):

### Paso 1 — Crear el bot de Telegram y obtener el token
1. En Telegram abre **@BotFather** → `/newbot` → nombre + username terminado en `bot`.
2. Copia el **token** (`123456789:AAH...`).

### Paso 2 — Cargar la credencial en N8N
1. Abre **http://localhost:5678** y crea el usuario owner local.
2. *Credentials → New → Telegram API* → pega el token → nómbrala **"Telegram Winback"**.

### Paso 3 — Importar y activar los workflows
1. *Workflows → Import from File* → importa los dos JSON de
   [`docs/n8n-workflows/`](n8n-workflows/).
2. En cada nodo de Telegram, selecciona la credencial **"Telegram Winback"**.
3. Reemplaza los placeholders:
   - `REEMPLAZAR_CHAT_ID_EQUIPO` y `REEMPLAZAR_CHAT_ID_ASESOR`: tu `chat_id`. Obtenlo
     escribiéndole a tu bot y mirando `https://api.telegram.org/bot<TOKEN>/getUpdates`.
4. **Activa** ambos workflows (toggle *Active*). Al activar el Workflow B, n8n registra
   automáticamente el webhook con Telegram.

### Paso 4 — Probar
- **Workflow B:** escribe `/start` a tu bot → debe responder el saludo y avanzar el flujo
  hasta "PROSPECTO LISTO" (y registrar la gestión + avisar al asesor).
- **Workflow A:** en el editor, *Execute Workflow* (sin esperar las 8am) → debe llegar el
  briefing con el top de prospectos diamante al chat del equipo.

> **Nota:** la API debe estar corriendo para que N8N la consuma. En esta sesión se levantó
> en background; para uso permanente déjala con `cd api ; uvicorn main:app --port 8000`.

---

## 8. Checklist

- [x] `POST /gestiones` implementado y registrado en `main.py`.
- [x] `POST /chatbot/conversar` (stateful) + tabla `sesiones_chat`.
- [x] N8N on-premise con Docker (`n8n-winback`), gratuito, persistente.
- [x] Conectividad contenedor→API verificada (`host.docker.internal:8000`).
- [x] Workflows A y B exportados como JSON importable.
- [ ] Crear bot en BotFather y cargar credencial en N8N *(tú)*.
- [ ] Importar, configurar chat_ids y activar los workflows *(tú)*.
- [ ] Validar que las gestiones quedan registradas (`GET /prospectos/resumen`).
