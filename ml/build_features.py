"""
Construcción del modelo de datos analítico consolidado (RF-01).

Integra, transforma y consolida las 6 fuentes de información en una única tabla
por prospecto (`dataset_analitico`), con variables derivadas listas para el
entrenamiento. Cubre el entregable "Modelo de datos consolidado para explotación
analítica" del requerimiento MP-FT-1358.

Fuentes consolidadas:
    prospectos · utilizaciones · nps_historial · manifestaciones ·
    siniestralidad · gestiones_reactivacion

Uso:
    python ml/build_features.py
"""
import sqlite3
import pandas as pd
import numpy as np
import os

DB_PATH = 'data/winback.db'

# Variables categóricas y su orden de codificación (estable y documentado)
MOTIVO_ENC = {'precio': 0, 'servicio': 1, 'cobertura': 2, 'traslado': 3,
              'economico': 4, 'fallecimiento_familiar': 5}
PLAN_ENC = {'basico': 0, 'medio': 1, 'premium': 2}
GENERO_ENC = {'F': 0, 'M': 1}


def build_dataset(conn: sqlite3.Connection) -> pd.DataFrame:
    """Consolida las 6 fuentes en un dataframe por prospecto."""
    prospectos = pd.read_sql('SELECT * FROM prospectos', conn)
    utilizaciones = pd.read_sql('SELECT * FROM utilizaciones', conn)
    nps = pd.read_sql('SELECT * FROM nps_historial', conn)
    manifestaciones = pd.read_sql('SELECT * FROM manifestaciones', conn)
    siniestralidad = pd.read_sql('SELECT * FROM siniestralidad', conn)
    gestiones = pd.read_sql('SELECT * FROM gestiones_reactivacion', conn)

    df = prospectos.copy()

    # ---- Estado poblacional (base) + codificación ----
    df['motivo_enc'] = df['motivo_desercion'].map(MOTIVO_ENC).fillna(-1).astype(int)
    df['plan_enc'] = df['plan_previo'].map(PLAN_ENC).fillna(-1).astype(int)
    df['genero_enc'] = df['genero'].map(GENERO_ENC).fillna(-1).astype(int)

    # ---- Utilizaciones (intensidad de uso del servicio) ----
    util_agg = utilizaciones.groupby('prospecto_id').agg(
        num_utilizaciones=('id', 'count'),
        valor_utilizaciones_cop=('valor_cop', 'sum'),
        satisfaccion_media=('satisfaccion', 'mean'),
    ).reset_index()
    df = df.merge(util_agg, left_on='id', right_on='prospecto_id', how='left').drop(columns='prospecto_id')

    # ---- NPS (lealtad / satisfacción declarada) ----
    nps_agg = nps.groupby('prospecto_id').agg(
        nps_promedio=('score', 'mean'),
        nps_min=('score', 'min'),
        num_mediciones_nps=('id', 'count'),
    ).reset_index()
    df = df.merge(nps_agg, left_on='id', right_on='prospecto_id', how='left').drop(columns='prospecto_id')

    # ---- Manifestaciones (fricción con el servicio) ----
    manifestaciones['es_queja_reclamo'] = manifestaciones['tipo'].isin(['queja', 'reclamo']).astype(int)
    manif_agg = manifestaciones.groupby('prospecto_id').agg(
        num_manifestaciones=('id', 'count'),
        num_quejas_reclamos=('es_queja_reclamo', 'sum'),
        tasa_resolucion=('resuelto', 'mean'),
    ).reset_index()
    df = df.merge(manif_agg, left_on='id', right_on='prospecto_id', how='left').drop(columns='prospecto_id')

    # ---- Siniestralidad (valor / riesgo) ----
    sin_cols = siniestralidad[['prospecto_id', 'siniestralidad_ratio', 'ingresos_totales_cop']]
    df = df.merge(sin_cols, left_on='id', right_on='prospecto_id', how='left').drop(columns='prospecto_id')

    # ---- Históricos de gestión de reactivaciones ----
    # Nota: se excluye el resultado 'reactivado' como feature para evitar fuga de información.
    gestiones['es_interesado'] = (gestiones['resultado'] == 'interesado').astype(int)
    gest_agg = gestiones.groupby('prospecto_id').agg(
        num_gestiones=('id', 'count'),
        num_interesado=('es_interesado', 'sum'),
    ).reset_index()
    df = df.merge(gest_agg, left_on='id', right_on='prospecto_id', how='left').drop(columns='prospecto_id')

    # ---- Imputación de prospectos sin registros relacionados ----
    cols_cero = ['num_utilizaciones', 'valor_utilizaciones_cop', 'num_manifestaciones',
                 'num_quejas_reclamos', 'num_mediciones_nps', 'num_gestiones', 'num_interesado']
    df[cols_cero] = df[cols_cero].fillna(0)
    df['satisfaccion_media'] = df['satisfaccion_media'].fillna(df['satisfaccion_media'].median())
    df['nps_promedio'] = df['nps_promedio'].fillna(df['nps_promedio'].median())
    df['nps_min'] = df['nps_min'].fillna(df['nps_min'].median())
    df['tasa_resolucion'] = df['tasa_resolucion'].fillna(0)
    df['siniestralidad_ratio'] = df['siniestralidad_ratio'].fillna(df['siniestralidad_ratio'].median())
    df['ingresos_totales_cop'] = df['ingresos_totales_cop'].fillna(0)

    # ---- Variables derivadas identificadas en el proceso analítico ----
    anios = (df['antiguedad_meses'] / 12).clip(lower=0.5)
    df['utilizaciones_por_anio'] = (df['num_utilizaciones'] / anios).round(3)
    df['tasa_manifestaciones'] = (df['num_manifestaciones'] / anios).round(3)
    df['valor_cliente_cop'] = (df['valor_plan_cop'] * df['antiguedad_meses']).astype(int)
    df['ratio_quejas'] = np.where(
        df['num_manifestaciones'] > 0,
        (df['num_quejas_reclamos'] / df['num_manifestaciones']).round(3),
        0.0,
    )

    return df


# Variables de entrada utilizadas por el modelo (RF-01 "Variables de entrada utilizadas")
FEATURE_COLUMNS = [
    # Estado poblacional
    'edad', 'antiguedad_meses', 'valor_plan_cop', 'motivo_enc', 'plan_enc', 'genero_enc',
    # Utilizaciones
    'num_utilizaciones', 'valor_utilizaciones_cop', 'satisfaccion_media',
    # NPS
    'nps_promedio', 'nps_min', 'num_mediciones_nps',
    # Manifestaciones
    'num_manifestaciones', 'num_quejas_reclamos', 'tasa_resolucion',
    # Siniestralidad
    'siniestralidad_ratio', 'ingresos_totales_cop',
    # Gestión de reactivaciones
    'num_gestiones', 'num_interesado',
    # Derivadas
    'utilizaciones_por_anio', 'tasa_manifestaciones', 'valor_cliente_cop', 'ratio_quejas',
]

FEATURE_LABELS = {
    'edad': 'Edad', 'antiguedad_meses': 'Antigüedad (meses)', 'valor_plan_cop': 'Valor del plan',
    'motivo_enc': 'Motivo de deserción', 'plan_enc': 'Plan previo', 'genero_enc': 'Género',
    'num_utilizaciones': 'N.º utilizaciones', 'valor_utilizaciones_cop': 'Valor utilizaciones',
    'satisfaccion_media': 'Satisfacción media', 'nps_promedio': 'NPS promedio', 'nps_min': 'NPS mínimo',
    'num_mediciones_nps': 'N.º mediciones NPS', 'num_manifestaciones': 'N.º manifestaciones',
    'num_quejas_reclamos': 'Quejas y reclamos', 'tasa_resolucion': 'Tasa de resolución',
    'siniestralidad_ratio': 'Siniestralidad (ratio)', 'ingresos_totales_cop': 'Ingresos totales',
    'num_gestiones': 'N.º gestiones', 'num_interesado': 'Gestiones con interés',
    'utilizaciones_por_anio': 'Utilizaciones por año', 'tasa_manifestaciones': 'Tasa de manifestaciones',
    'valor_cliente_cop': 'Valor del cliente', 'ratio_quejas': 'Ratio de quejas',
}


def main():
    conn = sqlite3.connect(DB_PATH)
    df = build_dataset(conn)
    # Persistir el dataset analítico consolidado como entregable
    df.to_sql('dataset_analitico', conn, if_exists='replace', index=False)
    conn.close()
    os.makedirs('ml/models', exist_ok=True)
    print(f"Dataset analítico consolidado: {len(df)} prospectos x {len(FEATURE_COLUMNS)} variables")
    print(f"   Tabla persistida: dataset_analitico")
    print(f"   Variables: {', '.join(FEATURE_COLUMNS)}")


if __name__ == '__main__':
    main()
