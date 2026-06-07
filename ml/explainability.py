"""
Explicabilidad del modelo predictivo (RF-05) con SHAP.

Carga el modelo XGBoost entrenado, calcula los valores SHAP sobre el dataset y
precalcula la importancia global de variables. El resultado se sirve desde un
JSON estático (mitigación: SHAP es costoso en tiempo real, ver sección 8 del plan).

Uso:
    python ml/explainability.py
"""
import sqlite3
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import shap
import pickle
import json
import os

DB_PATH = 'data/winback.db'
MODELS_DIR = 'ml/models'
FEATURES = ['edad', 'antiguedad_meses', 'motivo_enc', 'plan_enc']
FEATURE_LABELS = {
    'edad': 'Edad',
    'antiguedad_meses': 'Antigüedad (meses)',
    'motivo_enc': 'Motivo de deserción',
    'plan_enc': 'Plan previo',
}


def main():
    os.makedirs(MODELS_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql('SELECT * FROM prospectos', conn)
    conn.close()

    df['motivo_enc'] = LabelEncoder().fit_transform(df['motivo_desercion'])
    df['plan_enc'] = LabelEncoder().fit_transform(df['plan_previo'])
    X = df[FEATURES]

    with open(f'{MODELS_DIR}/xgboost.pkl', 'rb') as f:
        modelo = pickle.load(f)

    # Cálculo de valores SHAP (TreeExplainer es eficiente sobre modelos de árbol)
    explainer = shap.TreeExplainer(modelo)
    shap_values = explainer.shap_values(X)

    # Importancia global = media del valor absoluto SHAP por variable
    importancia = np.abs(shap_values).mean(axis=0)
    total = importancia.sum() or 1.0

    ranking = sorted(
        [
            {
                'feature': feat,
                'label': FEATURE_LABELS[feat],
                'mean_abs_shap': round(float(importancia[i]), 4),
                'importancia_relativa': round(float(importancia[i] / total), 4),
            }
            for i, feat in enumerate(FEATURES)
        ],
        key=lambda d: d['mean_abs_shap'],
        reverse=True,
    )

    salida = {
        'modelo': 'xgboost',
        'metodo': 'TreeExplainer (SHAP)',
        'n_muestras': int(len(X)),
        'importancia_variables': ranking,
    }

    with open(f'{MODELS_DIR}/shap_values.json', 'w', encoding='utf-8') as f:
        json.dump(salida, f, indent=2, ensure_ascii=False)

    print("Importancia de variables (SHAP):")
    for r in ranking:
        print(f"  {r['label']:<22} {r['importancia_relativa'] * 100:>5.1f}%")


if __name__ == '__main__':
    main()
