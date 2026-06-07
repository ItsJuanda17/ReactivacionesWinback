"""
Explicabilidad del modelo predictivo (RF-05) con SHAP.

Carga el modelo final seleccionado en el entrenamiento, calcula los valores SHAP
sobre el dataset analítico consolidado y precalcula la importancia global de
variables. El resultado se sirve desde un JSON estático (mitigación: SHAP es
costoso en tiempo real, ver documentación metodológica).

Uso:
    python ml/explainability.py
"""
import sqlite3
import numpy as np
import shap
import pickle
import json
import os

from build_features import build_dataset, FEATURE_COLUMNS, FEATURE_LABELS

DB_PATH = 'data/winback.db'
MODELS_DIR = 'ml/models'


def main():
    os.makedirs(MODELS_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    df = build_dataset(conn)
    conn.close()
    X = df[FEATURE_COLUMNS]

    with open(f'{MODELS_DIR}/metricas.json', encoding='utf-8') as f:
        modelo_final = json.load(f).get('modelo_final', 'xgboost')

    with open(f'{MODELS_DIR}/{modelo_final}.pkl', 'rb') as f:
        modelo = pickle.load(f)

    # TreeExplainer es eficiente sobre modelos de árbol (RF / XGBoost)
    explainer = shap.TreeExplainer(modelo)
    shap_values = explainer.shap_values(X)

    # En clasificación binaria algunos modelos devuelven una lista [clase0, clase1]
    if isinstance(shap_values, list):
        shap_values = shap_values[1]
    # o un tensor 3D (n, features, clases)
    shap_values = np.asarray(shap_values)
    if shap_values.ndim == 3:
        shap_values = shap_values[:, :, 1]

    importancia = np.abs(shap_values).mean(axis=0)
    total = importancia.sum() or 1.0

    ranking = sorted(
        [
            {
                'feature': feat,
                'label': FEATURE_LABELS.get(feat, feat),
                'mean_abs_shap': round(float(importancia[i]), 4),
                'importancia_relativa': round(float(importancia[i] / total), 4),
            }
            for i, feat in enumerate(FEATURE_COLUMNS)
        ],
        key=lambda d: d['mean_abs_shap'],
        reverse=True,
    )

    salida = {
        'modelo': modelo_final,
        'metodo': 'TreeExplainer (SHAP)',
        'n_muestras': int(len(X)),
        'importancia_variables': ranking,
    }

    with open(f'{MODELS_DIR}/shap_values.json', 'w', encoding='utf-8') as f:
        json.dump(salida, f, indent=2, ensure_ascii=False)

    print(f"Importancia de variables (SHAP · {modelo_final}) — top 10:")
    for r in ranking[:10]:
        print(f"  {r['label']:<24} {r['importancia_relativa'] * 100:>5.1f}%")


if __name__ == '__main__':
    main()
