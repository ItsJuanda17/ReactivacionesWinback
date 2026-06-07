# Documentación metodológica y técnica — Modelo Winback

> Requerimiento **MP-FT-1358** · RF-01, RF-02, RF-05
> Proyecto Reactivaciones Winback · Coomeva Medicina Prepagada · Proveedor ICESI

Este documento consolida la documentación funcional, técnica y metodológica de los
modelos predictivos, para garantizar transparencia, trazabilidad y soporte a la
toma de decisiones del negocio.

---

## 1. Metodología utilizada

El proyecto sigue la lógica **CRISP-DM** adaptada a la estrategia Winback:

1. **Entendimiento del negocio** — identificar usuarios retirados con mayor
   probabilidad de retorno para priorizar la gestión comercial.
2. **Entendimiento e integración de datos** — consolidación de 6 fuentes en un
   único modelo de datos analítico por prospecto (`ml/build_features.py`).
3. **Preparación** — limpieza, imputación, codificación de categóricas y creación
   de variables derivadas.
4. **Modelado** — entrenamiento y comparación de 3 algoritmos (`ml/train_models.py`).
5. **Evaluación** — métricas sobre conjunto de prueba y selección del modelo final.
6. **Explicabilidad** — importancia de variables con SHAP (`ml/explainability.py`).
7. **Segmentación** — arquetipos accionables con K-Means (`ml/clustering.py`).

---

## 2. Modelo de datos consolidado (RF-01)

Se integran, transforman y consolidan las **6 fuentes** del requerimiento en la
tabla `dataset_analitico` (una fila por prospecto):

| Fuente | Variables aportadas |
|---|---|
| Base poblacional (`prospectos`) | edad, antigüedad, valor del plan, motivo de deserción, plan, género |
| Utilizaciones | n.º utilizaciones, valor total, satisfacción media |
| NPS | NPS promedio, NPS mínimo, n.º mediciones |
| Manifestaciones | n.º manifestaciones, quejas/reclamos, tasa de resolución |
| Siniestralidad | ratio de siniestralidad, ingresos totales |
| Gestión de reactivaciones | n.º gestiones, gestiones con interés |

La caracterización considera el **último estado conocido previo a la deserción**.

### Variables derivadas identificadas en el proceso analítico

- `utilizaciones_por_anio` = n.º utilizaciones / años de antigüedad.
- `tasa_manifestaciones` = n.º manifestaciones / años de antigüedad.
- `valor_cliente_cop` = valor del plan × meses de antigüedad.
- `ratio_quejas` = quejas y reclamos / total de manifestaciones.

**Total: 23 variables de entrada.** La lista canónica está en `FEATURE_COLUMNS`
(`ml/build_features.py`).

---

## 3. Modelos utilizados (RF-02)

| Modelo | Familia | Por qué se incluye |
|---|---|---|
| Regresión Logística | Lineal | Baseline interpretable |
| Random Forest | Ensamble (bagging) | Captura no linealidades, robusto |
| XGBoost | Ensamble (boosting) | Alto desempeño en datos tabulares |

### Hiperparámetros

| Modelo | Hiperparámetros |
|---|---|
| Regresión Logística | `max_iter=1000`, `C=1.0`, `solver=lbfgs` |
| Random Forest | `n_estimators=200`, `max_depth=8`, `min_samples_leaf=5` |
| XGBoost | `n_estimators=300`, `max_depth=4`, `learning_rate=0.1`, `subsample=0.9` |

Quedan registrados en `ml/models/metricas.json` (`hiperparametros`).

---

## 4. Estrategia de balanceo de datos

El target (alta intención de retorno) presenta desbalanceo de clases. Se aplica
**SMOTE** (Synthetic Minority Over-sampling Technique) **únicamente sobre el
conjunto de entrenamiento**, para no contaminar la evaluación. Cumple la regla de
negocio "tratamiento de desbalanceo de clases cuando aplique".

---

## 5. Punto de corte

- **Definición del target:** `prob_reactivacion >= 0.55` ⇒ clase positiva.
- El punto de corte (**0.55**) separa prospectos de alta intención de retorno.
- Es un parámetro de negocio ajustable (`PUNTO_DE_CORTE` en `ml/train_models.py`)
  y, según la regla de negocio, **es independiente de las reglas de priorización
  comercial** (segmentos diamante/oro/plata/bronce).

---

## 6. Métricas de desempeño y selección del modelo final

Se evalúan sobre el conjunto de prueba (20%): **Accuracy, Precision, Recall,
F1-Score y ROC-AUC**.

- **Criterio de selección del modelo final:** mayor **F1-Score**, por equilibrar
  precisión y exhaustividad en un contexto de clases desbalanceadas.
- Los resultados vigentes se publican en `ml/models/metricas.json` y en el
  endpoint `GET /metricas`.

---

## 7. Importancia de variables e interpretación de resultados (RF-05)

Se utiliza **SHAP (TreeExplainer)** sobre el modelo final. La importancia global
(media del valor absoluto SHAP por variable) se precalcula y se sirve desde
`GET /modelo/importancia-variables`.

**Interpretación:** las variables de **valor del cliente, ingresos históricos,
antigüedad y motivo de deserción** son las de mayor peso en la probabilidad de
retorno — coherente con el negocio: clientes valiosos y antiguos, con motivos de
salida no estructurales, son los más recuperables.

---

## 8. Segmentación / arquetipos (RF-03)

K-Means con **4 clusters** sobre variables de comportamiento, valor, riesgo y
probabilidad de retorno. Cada arquetipo entrega perfil, variables relevantes,
**estrategia diferencial de contacto** y **recomendaciones de mercadeo**
(`GET /arquetipos`).

---

## 9. Supuestos y limitaciones

- **Datos sintéticos:** generados con Faker para el MVP; las distribuciones son
  realistas pero no corresponden a datos reales de Coomeva. El reemplazo por
  fuentes reales no exige cambios de arquitectura.
- La probabilidad base se construye con una función determinista + ruido; el
  modelo **aprende** sobre ella, por lo que no es una verdad de campo.
- La feature de gestiones excluye el resultado `reactivado` para **evitar fuga de
  información**.
- SHAP es costoso en tiempo real → se **precalcula en batch** y se sirve por JSON.
- El chatbot es un **prototipo funcional** (no productivo): no integra WhatsApp
  Business API.

---

## 10. Recomendaciones para uso del modelo

- Priorizar la gestión sobre los segmentos **diamante** y **oro** (mayor valor
  recuperable esperado).
- Aplicar la **estrategia diferencial** de cada arquetipo en el script del asesor
  y del chatbot.
- Reentrenar periódicamente con datos reales y recalibrar el punto de corte según
  la capacidad operativa del equipo de reactivaciones.
- Monitorear *data drift* y desempeño (F1/AUC) tras cada campaña.
