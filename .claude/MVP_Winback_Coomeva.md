# Plan MVP — Proyecto Reactivaciones Winback · Coomeva Medicina Prepagada

> **Arquitecto:** Plan orientado a demostración funcional, costo cero, desplegable en entorno gratuito o local.
> **Basado en:** Requerimiento MP-FT-1358 · Proveedor ICESI

---

## 1. Stack Tecnológico (100% gratuito y justificado)

| Componente | Tecnología | Justificación gratuita |
|---|---|---|
| Lenguaje ML / API | Python 3.11 | Open source, ecosistema ML completo |
| Framework API | FastAPI | Async, autodoc Swagger, deploy en Render free |
| Modelo predictivo | scikit-learn + XGBoost | BSD/Apache license, sin costo |
| Explicabilidad | SHAP | MIT license, RF-05 cubierto |
| Datos sintéticos | Python Faker + pandas | MIT license |
| Base de datos | SQLite (local) / Supabase free tier | 500 MB gratis en Supabase |
| Frontend dashboard | React 18 + Recharts | MIT license |
| Despliegue frontend | Vercel free tier | 100 GB bandwidth / mes gratis |
| Despliegue backend | Render.com free tier | 750 h/mes gratis |
| Control de versiones | GitHub (repositorio público) | Gratuito |
| Chatbot prototipo | React widget (simulado) | Sin Twilio ni servicios de pago |
| Notebooks análisis | Jupyter / Google Colab | Google Colab 100% gratuito |

**Costo total: $0**

---

## 2. Modelo de Datos

### Entidades principales

- **prospectos**: id, nombre_completo, edad, ciudad, fecha_desercion, motivo_desercion
  (precio | servicio | cobertura | traslado), antiguedad_meses, plan_previo
  (basico | medio | premium), prob_reactivacion (0.0–1.0), segmento
  (diamante | oro | plata | bronce), estado_gestion.
- **utilizaciones**: id, prospecto_id (FK), tipo_servicio, frecuencia/valor.
- **nps_historial**: id, prospecto_id (FK), score (0–10), fecha.
- **manifestaciones**: id, prospecto_id (FK), tipo (queja | reclamo | sugerencia | felicitacion), canal, fecha.
- **siniestralidad**: agregado por prospecto (ingresos, egresos, ratio).
- **gestiones_reactivacion**: id, prospecto_id (FK), fecha_contacto, canal_contacto, resultado, asesor_id.
- **arquetipos**: id, nombre, descripcion, variables_clave, estrategia_recomendada.

---

## 3. Arquitectura General

```
DATOS SINTÉTICOS (Faker)  →  CAPA ANALÍTICA / ML  →  API FastAPI  →  Dashboard + Chatbot React
2000 prospectos · 6 tablas   RF-01/02/03/05            endpoints REST   Vercel free tier
```

---

## 4. Pasos de Implementación

1. Estructura del repositorio (.claude, data, ml, api, frontend, .gitignore, README).
2. Generación de datos sintéticos (6 tablas, 2000+ registros).
3. Entrenamiento ML (RF-01, RF-02): LogReg, RandomForest, XGBoost + SMOTE.
4. Arquetipos K-Means (RF-03): 4 clusters.
5. Explicabilidad SHAP (RF-05).
6. API FastAPI (routers: prospectos, metricas, arquetipos, chatbot).
7. Frontend Dashboard (React + Recharts).
8. Chatbot UI (RF-04): flujo simulado tipo WhatsApp.
9. Configuración de despliegue (Render, Vercel, .env).

El detalle de cada paso, con el código de referencia de cada componente, se encuentra documentado
en el requerimiento MP-FT-1358 y reproducido en este MVP. La fuente de verdad operativa es este
repositorio: cada script es ejecutable localmente sin dependencias de pago.

---

## 5. Estrategia de Datos Sintéticos

| Variable | Distribución |
|---|---|
| edad | Uniforme 22–78 |
| antiguedad_meses | Uniforme 6–144 |
| motivo_desercion | Multinomial ponderado (precio 35%, servicio 22%, cobertura 18%, ...) |
| plan_previo | Multinomial (básico 50%, medio 35%, premium 15%) |
| prob_reactivacion | Función determinista + ruido N(0, 0.1) |
| nps_score | Beta(2, 5) × 10 (sesgo a scores bajos) |
| num_manifestaciones | Poisson(λ=1.0–2.5) |
| num_utilizaciones | Poisson(λ=2 + antigüedad/36) |
| siniestralidad_ratio | Beta(2, 4) × 2 (rango 0.05–1.8) |

Herramientas: `pip install faker pandas numpy scikit-learn xgboost imbalanced-learn shap fastapi uvicorn`

Volumen final esperado con n=2000: ~20.000–25.000 filas en 6 tablas.

---

## 6. Estándar de Commits (Conventional Commits)

Cada vez que se crea o edita un archivo se hace un commit inmediato siguiendo
[Conventional Commits](https://www.conventionalcommits.org/).

Formato: `<tipo>: <descripción corta en inglés>` (imperativo presente, máx. 72 caracteres).

Tipos permitidos: `feat`, `fix`, `docs`, `chore`, `test`, `refactor`, `style`, `perf`, `ci`, `build`, `revert`.

Reglas de equipo:
- Un commit por archivo o grupo de archivos del mismo contexto.
- Nunca commitear `winback.db`, `.pkl`, `.env` ni `__pycache__/` (van en `.gitignore`).
- Los `fix` referencian el paso o requerimiento afectado en el cuerpo cuando aplique.

---

## 7. Despliegue sin costos

- **Opción A — Local**: generar datos, entrenar, `uvicorn main:app` + `npm run dev`.
- **Opción B — Nube**: Backend en Render.com (free tier), Frontend en Vercel, BD opcional en Supabase.

---

## 8. Limitaciones y Mitigaciones

- Datos sintéticos ≠ reales → documentar supuestos; fácil reemplazo al integrar fuentes reales.
- Chatbot sin WhatsApp real → flujo web funcional; migrar a Twilio/360dialog con presupuesto.
- Render free tier duerme tras 15 min → keep-alive ping.
- SQLite no concurrente → suficiente para MVP; escalar a Supabase PostgreSQL.
- Sin autenticación → agregar HTTPBearer/Supabase Auth en siguiente iteración.

---

## 9. Checklist de criterios de aceptación (MP-FT-1358)

| Criterio | Componente MVP |
|---|---|
| Modelos predictivos funcionales y documentados | `ml/train_models.py` + SHAP |
| Presentación comparativa de más de un modelo | `metricas.json` + dashboard |
| Entrega de métricas de desempeño | Accuracy, Precision, Recall, F1, AUC |
| Generación de ranking de prospectos | Tabla ordenada por prob_reactivacion |
| Segmentación y arquetipos comerciales | K-Means 4 clusters + tarjetas |
| Prototipo funcional de chatbot | Flujo 6 etapas RF-04 |
| Documentación metodológica y técnica | SHAP + README + notebooks |
| Validación funcional con áreas de negocio | Demo en Vercel + API Swagger |

*Documento generado como guía de arquitectura para Proyecto Reactivaciones Winback — Coomeva MP · Proveedor ICESI*