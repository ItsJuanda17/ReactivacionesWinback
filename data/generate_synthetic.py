"""
Generador de datos sintéticos para el MVP Winback Coomeva.
Crea 6 tablas relacionadas con un mínimo de 2000 prospectos.

Uso:
    python data/generate_synthetic.py
    python data/generate_synthetic.py --n 5000 --seed 42
"""
from faker import Faker
import pandas as pd
import sqlite3
import random
import numpy as np
import argparse
import os
from datetime import date

fake = Faker('es_CO')


def _to_date(value: str) -> date:
    """Convierte una fecha ISO (str) a date para Faker date_between."""
    return date.fromisoformat(value)


# ---------- 1. PROSPECTOS ----------
def generate_prospectos(n: int) -> pd.DataFrame:
    """Genera la tabla maestra de prospectos retirados de MP."""
    motivos = ['precio', 'servicio', 'cobertura', 'traslado', 'economico', 'fallecimiento_familiar']
    motivos_w = [35, 22, 18, 12, 10, 3]
    planes = ['basico', 'medio', 'premium']
    planes_w = [50, 35, 15]
    ciudades = ['Cali', 'Bogotá', 'Medellín', 'Barranquilla', 'Pereira',
                'Bucaramanga', 'Cartagena', 'Manizales', 'Pasto', 'Ibagué']
    estados_gestion = ['pendiente', 'contactado', 'interesado', 'cerrado', 'no_contactable']

    rows = []
    for _ in range(n):
        antiguedad = random.randint(6, 144)             # 6 meses a 12 años
        motivo = random.choices(motivos, weights=motivos_w)[0]
        plan = random.choices(planes, weights=planes_w)[0]
        edad = random.randint(22, 78)
        genero = random.choice(['F', 'M'])

        # Lógica de probabilidad realista (no es la verdad: se aprende en el modelo)
        base_prob = 0.30
        if antiguedad > 36:           base_prob += 0.20
        if antiguedad > 84:           base_prob += 0.10
        if plan == 'premium':         base_prob += 0.15
        elif plan == 'medio':         base_prob += 0.05
        if motivo == 'precio':        base_prob -= 0.12
        if motivo == 'servicio':      base_prob -= 0.08
        if motivo == 'traslado':      base_prob -= 0.05
        if edad < 40:                 base_prob += 0.05
        if edad > 60:                 base_prob += 0.08
        prob = float(np.clip(base_prob + np.random.normal(0, 0.10), 0.05, 0.95))

        rows.append({
            'id': fake.uuid4(),
            'nombre_completo': fake.name(),
            'documento': fake.numerify('##########'),
            'edad': edad,
            'genero': genero,
            'ciudad': random.choice(ciudades),
            'telefono': fake.numerify('30########'),
            'email': fake.email(),
            'fecha_desercion': fake.date_between('-2y', 'today').isoformat(),
            'motivo_desercion': motivo,
            'antiguedad_meses': antiguedad,
            'plan_previo': plan,
            'valor_plan_cop': {'basico': 180000, 'medio': 320000, 'premium': 520000}[plan],
            'prob_reactivacion': round(prob, 3),
            'segmento': asignar_segmento(prob),
            'estado_gestion': random.choices(estados_gestion, weights=[45, 25, 12, 10, 8])[0]
        })
    return pd.DataFrame(rows)


def asignar_segmento(prob: float) -> str:
    if prob >= 0.75: return 'diamante'
    if prob >= 0.55: return 'oro'
    if prob >= 0.35: return 'plata'
    return 'bronce'


# ---------- 2. UTILIZACIONES ----------
def generate_utilizaciones(prospectos: pd.DataFrame) -> pd.DataFrame:
    """Cada prospecto tiene entre 0 y 12 utilizaciones históricas."""
    tipos = ['consulta_general', 'urgencias', 'hospitalizacion',
             'laboratorio', 'imagenes_diagnosticas', 'especialista', 'cirugia_ambulatoria']
    tipos_w = [40, 15, 5, 18, 10, 10, 2]
    rows = []
    for _, p in prospectos.iterrows():
        # Más utilizaciones en planes altos y mayor antigüedad
        n_util = np.random.poisson(2 + p['antiguedad_meses'] / 36)
        n_util = min(int(n_util), 12)
        for _ in range(n_util):
            tipo = random.choices(tipos, weights=tipos_w)[0]
            valor_base = {'consulta_general': 80000, 'urgencias': 250000,
                          'hospitalizacion': 2500000, 'laboratorio': 120000,
                          'imagenes_diagnosticas': 350000, 'especialista': 180000,
                          'cirugia_ambulatoria': 1800000}[tipo]
            rows.append({
                'id': fake.uuid4(),
                'prospecto_id': p['id'],
                'tipo_servicio': tipo,
                'fecha': fake.date_between('-3y', _to_date(p['fecha_desercion'])).isoformat(),
                'valor_cop': int(valor_base * np.random.uniform(0.8, 1.4)),
                'satisfaccion': random.choices([1, 2, 3, 4, 5], weights=[5, 10, 25, 35, 25])[0]
            })
    return pd.DataFrame(rows)


# ---------- 3. NPS ----------
def generate_nps(prospectos: pd.DataFrame) -> pd.DataFrame:
    """NPS histórico: 1 a 4 mediciones por prospecto antes de la deserción."""
    rows = []
    for _, p in prospectos.iterrows():
        n_mediciones = random.randint(1, 4)
        for _ in range(n_mediciones):
            # Sesgo hacia scores bajos (clientes que se fueron)
            score = int(np.clip(np.random.beta(2, 5) * 10, 0, 10))
            rows.append({
                'id': fake.uuid4(),
                'prospecto_id': p['id'],
                'score': score,
                'categoria': 'promotor' if score >= 9 else ('pasivo' if score >= 7 else 'detractor'),
                'fecha': fake.date_between('-2y', _to_date(p['fecha_desercion'])).isoformat(),
                'canal': random.choice(['email', 'sms', 'app', 'llamada'])
            })
    return pd.DataFrame(rows)


# ---------- 4. MANIFESTACIONES ----------
def generate_manifestaciones(prospectos: pd.DataFrame) -> pd.DataFrame:
    """Quejas, reclamos, sugerencias y felicitaciones."""
    tipos = ['queja', 'reclamo', 'sugerencia', 'felicitacion']
    tipos_w = [35, 30, 20, 15]
    canales = ['call_center', 'app', 'web', 'presencial', 'redes_sociales']
    rows = []
    for _, p in prospectos.iterrows():
        # Más manifestaciones para quienes se fueron por servicio
        lambda_param = 2.5 if p['motivo_desercion'] == 'servicio' else 1.0
        n_manif = min(int(np.random.poisson(lambda_param)), 6)
        for _ in range(n_manif):
            rows.append({
                'id': fake.uuid4(),
                'prospecto_id': p['id'],
                'tipo': random.choices(tipos, weights=tipos_w)[0],
                'canal': random.choice(canales),
                'fecha': fake.date_between('-2y', _to_date(p['fecha_desercion'])).isoformat(),
                'resuelto': random.choices([1, 0], weights=[70, 30])[0]
            })
    return pd.DataFrame(rows)


# ---------- 5. SINIESTRALIDAD ----------
def generate_siniestralidad(prospectos: pd.DataFrame) -> pd.DataFrame:
    """Cálculo agregado de siniestralidad por prospecto (1 fila por prospecto)."""
    rows = []
    for _, p in prospectos.iterrows():
        meses = p['antiguedad_meses']
        ingresos = p['valor_plan_cop'] * meses
        siniestralidad_ratio = float(np.clip(np.random.beta(2, 4) * 2, 0.05, 1.8))
        egresos = int(ingresos * siniestralidad_ratio)
        rows.append({
            'id': fake.uuid4(),
            'prospecto_id': p['id'],
            'ingresos_totales_cop': int(ingresos),
            'egresos_totales_cop': egresos,
            'siniestralidad_ratio': round(siniestralidad_ratio, 3),
            'categoria_riesgo': 'alto' if siniestralidad_ratio > 1.0 else (
                                'medio' if siniestralidad_ratio > 0.6 else 'bajo')
        })
    return pd.DataFrame(rows)


# ---------- 6. GESTIONES DE REACTIVACIÓN ----------
def generate_gestiones(prospectos: pd.DataFrame) -> pd.DataFrame:
    """Histórico de intentos de reactivación (campaña 2025-2026)."""
    canales = ['whatsapp', 'llamada', 'email', 'sms']
    canales_w = [40, 30, 20, 10]
    resultados = ['no_contesta', 'interesado', 'rechazado', 'reactivado', 'colgo']
    resultados_w = [40, 25, 20, 5, 10]
    rows = []
    for _, p in prospectos.iterrows():
        # Solo quienes ya fueron contactados tienen gestiones
        if p['estado_gestion'] in ('pendiente', 'no_contactable'):
            continue
        n_gest = random.randint(1, 4)
        for _ in range(n_gest):
            rows.append({
                'id': fake.uuid4(),
                'prospecto_id': p['id'],
                'fecha_contacto': fake.date_between('-1y', 'today').isoformat(),
                'canal_contacto': random.choices(canales, weights=canales_w)[0],
                'resultado': random.choices(resultados, weights=resultados_w)[0],
                'asesor_id': f'ASE-{random.randint(1, 25):03d}',
                'duracion_segundos': random.randint(30, 720)
            })
    return pd.DataFrame(rows)


# ---------- ORQUESTACIÓN ----------
def main(n: int, seed: int, db_path: str):
    random.seed(seed)
    np.random.seed(seed)
    Faker.seed(seed)

    os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)

    print(f"Generando {n} prospectos y tablas relacionadas (seed={seed})...")
    prospectos = generate_prospectos(n)
    utilizaciones = generate_utilizaciones(prospectos)
    nps = generate_nps(prospectos)
    manifestaciones = generate_manifestaciones(prospectos)
    siniestralidad = generate_siniestralidad(prospectos)
    gestiones = generate_gestiones(prospectos)

    conn = sqlite3.connect(db_path)
    prospectos.to_sql('prospectos', conn, if_exists='replace', index=False)
    utilizaciones.to_sql('utilizaciones', conn, if_exists='replace', index=False)
    nps.to_sql('nps_historial', conn, if_exists='replace', index=False)
    manifestaciones.to_sql('manifestaciones', conn, if_exists='replace', index=False)
    siniestralidad.to_sql('siniestralidad', conn, if_exists='replace', index=False)
    gestiones.to_sql('gestiones_reactivacion', conn, if_exists='replace', index=False)
    conn.close()

    print(f"Datos generados en {db_path}")
    print(f"   - prospectos:              {len(prospectos):>6} filas")
    print(f"   - utilizaciones:           {len(utilizaciones):>6} filas")
    print(f"   - nps_historial:           {len(nps):>6} filas")
    print(f"   - manifestaciones:         {len(manifestaciones):>6} filas")
    print(f"   - siniestralidad:          {len(siniestralidad):>6} filas")
    print(f"   - gestiones_reactivacion:  {len(gestiones):>6} filas")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--n', type=int, default=2000, help='Número de prospectos (mínimo 2000)')
    parser.add_argument('--seed', type=int, default=42, help='Semilla para reproducibilidad')
    parser.add_argument('--db', type=str, default='data/winback.db', help='Ruta del SQLite')
    args = parser.parse_args()
    assert args.n >= 2000, "Se requieren mínimo 2000 prospectos para entrenamiento"
    main(args.n, args.seed, args.db)
