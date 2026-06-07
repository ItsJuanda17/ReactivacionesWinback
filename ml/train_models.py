"""
Entrenamiento de modelos predictivos de reactivación (RF-01, RF-02).

Compara LogisticRegression, RandomForest y XGBoost, maneja el desbalanceo de
clases con SMOTE y serializa los modelos + métricas comparativas.

Uso:
    python ml/train_models.py
"""
import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score
)
from imblearn.over_sampling import SMOTE
import pickle
import json
import os

DB_PATH = 'data/winback.db'
MODELS_DIR = 'ml/models'


def main():
    os.makedirs(MODELS_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql('SELECT * FROM prospectos', conn)
    conn.close()

    # Feature engineering (un encoder por columna para evitar fugas de codificación)
    le_motivo = LabelEncoder()
    le_plan = LabelEncoder()
    df['motivo_enc'] = le_motivo.fit_transform(df['motivo_desercion'])
    df['plan_enc'] = le_plan.fit_transform(df['plan_previo'])
    df['target'] = (df['prob_reactivacion'] >= 0.55).astype(int)  # binario

    FEATURES = ['edad', 'antiguedad_meses', 'motivo_enc', 'plan_enc']
    X = df[FEATURES]
    y = df['target']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Desbalanceo de clases (RF-02 consideración)
    sm = SMOTE(random_state=42)
    X_bal, y_bal = sm.fit_resample(X_train, y_train)

    modelos = {
        'logistic_regression': LogisticRegression(max_iter=1000),
        'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'xgboost': XGBClassifier(eval_metric='logloss', random_state=42)
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
            'roc_auc': round(roc_auc_score(y_test, modelo.predict_proba(X_test)[:, 1]), 4)
        }
        with open(f'{MODELS_DIR}/{nombre}.pkl', 'wb') as f:
            pickle.dump(modelo, f)

    with open(f'{MODELS_DIR}/metricas.json', 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2)

    print("Modelos entrenados. Resultados:")
    for k, v in resultados.items():
        print(f"  {k}: F1={v['f1']} | AUC={v['roc_auc']}")


if __name__ == '__main__':
    main()
