"""
Segmentación de prospectos en arquetipos comerciales (RF-03).

Aplica K-Means (4 clusters) sobre variables clave y produce un JSON con el
perfil de cada arquetipo para consumo del dashboard y los asesores.

Uso:
    python ml/clustering.py
"""
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
import sqlite3
import json
import os

DB_PATH = 'data/winback.db'
MODELS_DIR = 'ml/models'


def main():
    os.makedirs(MODELS_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql('SELECT * FROM prospectos', conn)
    conn.close()

    le_motivo = {'precio': 0, 'servicio': 1, 'cobertura': 2, 'traslado': 3,
                 'economico': 4, 'fallecimiento_familiar': 5}
    le_plan = {'basico': 0, 'medio': 1, 'premium': 2}
    df['motivo_enc'] = df['motivo_desercion'].map(le_motivo)
    df['plan_enc'] = df['plan_previo'].map(le_plan)

    X = df[['edad', 'antiguedad_meses', 'prob_reactivacion', 'motivo_enc', 'plan_enc']]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_scaled)

    arquetipos_nombres = {
        0: 'Precio-sensible reciente',
        1: 'Fiel defraudado',
        2: 'Migrador involuntario',
        3: 'Alto valor recuperable'
    }

    arquetipos = []
    for cluster_id, nombre in arquetipos_nombres.items():
        sub = df[df['cluster'] == cluster_id]
        if len(sub) == 0:
            continue
        arquetipos.append({
            'id': cluster_id,
            'nombre': nombre,
            'total_prospectos': len(sub),
            'prob_media': round(sub['prob_reactivacion'].mean(), 3),
            'edad_media': round(sub['edad'].mean(), 1),
            'antiguedad_media': round(sub['antiguedad_meses'].mean(), 1),
            'motivo_frecuente': sub['motivo_desercion'].mode()[0],
            'plan_frecuente': sub['plan_previo'].mode()[0]
        })

    with open(f'{MODELS_DIR}/arquetipos.json', 'w', encoding='utf-8') as f:
        json.dump(arquetipos, f, indent=2, ensure_ascii=False)

    print(f"{len(arquetipos)} arquetipos generados")


if __name__ == '__main__':
    main()
