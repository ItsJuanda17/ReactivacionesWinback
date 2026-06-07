"""
Entrenamiento y comparación de modelos predictivos de reactivación (RF-01, RF-02).

Entrena sobre el dataset analítico consolidado (6 fuentes), compara
LogisticRegression, RandomForest y XGBoost, maneja el desbalanceo con SMOTE y
serializa los modelos + un JSON de métricas enriquecido con los metadatos que
exige el requerimiento (hiperparámetros, punto de corte, modelo final).

Uso:
    python ml/train_models.py
"""
import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
)
from imblearn.over_sampling import SMOTE
import pickle
import json
import os

from build_features import build_dataset, FEATURE_COLUMNS

DB_PATH = 'data/winback.db'
MODELS_DIR = 'ml/models'
PUNTO_DE_CORTE = 0.55  # umbral de probabilidad para clasificar "alta intención de retorno"

# Hiperparámetros explícitos (RF-02: "Definición de hiperparámetros")
HIPERPARAMETROS = {
    'logistic_regression': {'max_iter': 1000, 'C': 1.0, 'solver': 'lbfgs'},
    'random_forest': {'n_estimators': 200, 'max_depth': 8, 'min_samples_leaf': 5, 'random_state': 42},
    'xgboost': {'n_estimators': 300, 'max_depth': 4, 'learning_rate': 0.1,
                'subsample': 0.9, 'eval_metric': 'logloss', 'random_state': 42},
}


def main():
    os.makedirs(MODELS_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    df = build_dataset(conn)
    conn.close()

    X = df[FEATURE_COLUMNS]
    y = (df['prob_reactivacion'] >= PUNTO_DE_CORTE).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Estrategia de balanceo de datos (RF-02): SMOTE sobre el set de entrenamiento
    sm = SMOTE(random_state=42)
    X_bal, y_bal = sm.fit_resample(X_train, y_train)

    modelos = {
        'logistic_regression': LogisticRegression(**HIPERPARAMETROS['logistic_regression']),
        'random_forest': RandomForestClassifier(**HIPERPARAMETROS['random_forest']),
        'xgboost': XGBClassifier(**HIPERPARAMETROS['xgboost']),
    }

    resultados = {}
    for nombre, modelo in modelos.items():
        modelo.fit(X_bal, y_bal)
        preds = modelo.predict(X_test)
        resultados[nombre] = {
            'accuracy': round(accuracy_score(y_test, preds), 4),
            'precision': round(precision_score(y_test, preds, zero_division=0), 4),
            'recall': round(recall_score(y_test, preds, zero_division=0), 4),
            'f1': round(f1_score(y_test, preds, zero_division=0), 4),
            'roc_auc': round(roc_auc_score(y_test, modelo.predict_proba(X_test)[:, 1]), 4),
        }
        with open(f'{MODELS_DIR}/{nombre}.pkl', 'wb') as f:
            pickle.dump(modelo, f)

    # Criterio de selección del modelo final (RF-02): mayor F1-Score
    modelo_final = max(resultados, key=lambda m: resultados[m]['f1'])

    salida = {
        'modelos': resultados,
        'modelo_final': modelo_final,
        'criterio_seleccion': 'Mayor F1-Score sobre el conjunto de prueba',
        'punto_de_corte': PUNTO_DE_CORTE,
        'estrategia_balanceo': 'SMOTE (oversampling de la clase minoritaria en entrenamiento)',
        'hiperparametros': HIPERPARAMETROS,
        'n_variables': len(FEATURE_COLUMNS),
        'variables': FEATURE_COLUMNS,
        'n_train': int(len(X_train)),
        'n_test': int(len(X_test)),
    }

    with open(f'{MODELS_DIR}/metricas.json', 'w', encoding='utf-8') as f:
        json.dump(salida, f, indent=2, ensure_ascii=False)

    print("Modelos entrenados sobre dataset consolidado. Resultados:")
    for k, v in resultados.items():
        marca = '  <-- modelo final' if k == modelo_final else ''
        print(f"  {k}: F1={v['f1']} | AUC={v['roc_auc']}{marca}")


if __name__ == '__main__':
    main()
