"""
Generación de arquetipos y segmentación accionable (RF-03).

Aplica K-Means (4 clusters) sobre variables de comportamiento, valor estratégico,
riesgo y probabilidad de retorno, y produce para cada arquetipo: perfil agregado,
variables relevantes que lo distinguen, estrategia diferencial de contacto y
recomendaciones de mercadeo.

Uso:
    python ml/clustering.py
"""
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
import sqlite3
import json
import os

from build_features import build_dataset

DB_PATH = 'data/winback.db'
MODELS_DIR = 'ml/models'

# Variables de segmentación: comportamiento, valor, riesgo y probabilidad de retorno
CLUSTER_FEATURES = [
    'edad', 'antiguedad_meses', 'prob_reactivacion', 'nps_promedio',
    'siniestralidad_ratio', 'num_utilizaciones', 'valor_cliente_cop',
    'num_quejas_reclamos', 'motivo_enc', 'plan_enc',
]

FEATURE_LABELS = {
    'edad': 'edad', 'antiguedad_meses': 'antigüedad', 'prob_reactivacion': 'prob. de retorno',
    'nps_promedio': 'NPS', 'siniestralidad_ratio': 'siniestralidad', 'num_utilizaciones': 'uso del servicio',
    'valor_cliente_cop': 'valor del cliente', 'num_quejas_reclamos': 'quejas/reclamos',
    'motivo_enc': 'motivo de deserción', 'plan_enc': 'plan',
}

# Estrategia diferencial por arquetipo (recomendaciones para mercadeo y contacto)
ESTRATEGIAS = {
    'Precio-sensible reciente': {
        'estrategia_recomendada': 'Oferta de reingreso con descuento temporal y plan ajustado a su capacidad de pago.',
        'canal_sugerido': 'WhatsApp + llamada de cierre',
        'recomendacion_mercadeo': 'Comunicar valor/precio y beneficios diferenciales frente a la competencia.',
        'prioridad': 'media',
    },
    'Fiel defraudado': {
        'estrategia_recomendada': 'Reconocimiento de la antigüedad, disculpa por la experiencia y gestor dedicado.',
        'canal_sugerido': 'Llamada de un asesor senior',
        'recomendacion_mercadeo': 'Enfatizar mejoras en servicio y atención prioritaria; resolver fricción previa.',
        'prioridad': 'alta',
    },
    'Migrador involuntario': {
        'estrategia_recomendada': 'Plan premium con cobertura ampliada y portabilidad de beneficios.',
        'canal_sugerido': 'Email premium + WhatsApp',
        'recomendacion_mercadeo': 'Resaltar cobertura y red de prestadores superior al competidor actual.',
        'prioridad': 'alta',
    },
    'Alto valor recuperable': {
        'estrategia_recomendada': 'Campaña de retención de alto valor con incentivos personalizados.',
        'canal_sugerido': 'Contacto comercial directo',
        'recomendacion_mercadeo': 'Trato preferencial; medir ROI por su valor de cliente histórico.',
        'prioridad': 'alta',
    },
}
ARQUETIPOS_NOMBRES = {
    0: 'Precio-sensible reciente',
    1: 'Fiel defraudado',
    2: 'Migrador involuntario',
    3: 'Alto valor recuperable',
}


def variables_relevantes(sub: pd.DataFrame, df: pd.DataFrame, top_n: int = 3) -> list:
    """Variables que más diferencian al cluster respecto al promedio global."""
    desviaciones = []
    for col in CLUSTER_FEATURES:
        global_std = df[col].std() or 1.0
        z = (sub[col].mean() - df[col].mean()) / global_std
        desviaciones.append((FEATURE_LABELS.get(col, col), z))
    desviaciones.sort(key=lambda t: abs(t[1]), reverse=True)
    return [
        {'variable': nombre, 'tendencia': 'alta' if z > 0 else 'baja'}
        for nombre, z in desviaciones[:top_n]
    ]


def main():
    os.makedirs(MODELS_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    df = build_dataset(conn)
    conn.close()

    X = df[CLUSTER_FEATURES]
    X_scaled = StandardScaler().fit_transform(X)

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_scaled)

    arquetipos = []
    for cluster_id, nombre in ARQUETIPOS_NOMBRES.items():
        sub = df[df['cluster'] == cluster_id]
        if len(sub) == 0:
            continue
        estrategia = ESTRATEGIAS[nombre]
        arquetipos.append({
            'id': int(cluster_id),
            'nombre': nombre,
            'total_prospectos': int(len(sub)),
            'prob_media': round(float(sub['prob_reactivacion'].mean()), 3),
            'edad_media': round(float(sub['edad'].mean()), 1),
            'antiguedad_media': round(float(sub['antiguedad_meses'].mean()), 1),
            'nps_medio': round(float(sub['nps_promedio'].mean()), 1),
            'siniestralidad_media': round(float(sub['siniestralidad_ratio'].mean()), 2),
            'valor_cliente_medio': int(sub['valor_cliente_cop'].mean()),
            'motivo_frecuente': sub['motivo_desercion'].mode()[0],
            'plan_frecuente': sub['plan_previo'].mode()[0],
            'variables_relevantes': variables_relevantes(sub, df),
            **estrategia,
        })

    with open(f'{MODELS_DIR}/arquetipos.json', 'w', encoding='utf-8') as f:
        json.dump(arquetipos, f, indent=2, ensure_ascii=False)

    print(f"{len(arquetipos)} arquetipos generados con estrategia y recomendaciones")


if __name__ == '__main__':
    main()
