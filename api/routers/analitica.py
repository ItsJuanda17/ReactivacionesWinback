# GET /analitica/insights — hallazgos de negocio calculados desde los datos
import sqlite3
from fastapi import APIRouter
from config import DB_PATH

router = APIRouter()
PUNTO_DE_CORTE = 0.55


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _pct(n, d):
    return round(100 * n / d, 1) if d else 0.0


@router.get("/insights")
def insights():
    """Hallazgos accionables derivados del análisis de la base de prospectos."""
    conn = _conn()
    hallazgos = []

    # 1. Antigüedad: intención de retorno en clientes muy antiguos vs el resto
    antiguos = conn.execute(
        "SELECT AVG(prob_reactivacion) AS p FROM prospectos WHERE antiguedad_meses > 120"
    ).fetchone()["p"]
    resto = conn.execute(
        "SELECT AVG(prob_reactivacion) AS p FROM prospectos WHERE antiguedad_meses <= 120"
    ).fetchone()["p"]
    if antiguos and resto:
        diff = round((antiguos - resto) * 100, 1)
        hallazgos.append({
            "titulo": "La antigüedad pesa en el retorno",
            "detalle": f"Los clientes con más de 10 años de antigüedad muestran una intención de "
                       f"retorno {abs(diff)} puntos {'mayor' if diff >= 0 else 'menor'} que el resto "
                       f"({round(antiguos*100)}% vs {round(resto*100)}%).",
        })

    # 2. Ciudad que concentra el mayor volumen de oportunidades
    ciudad = conn.execute(
        "SELECT ciudad, COUNT(*) AS c FROM prospectos WHERE prob_reactivacion >= ? "
        "GROUP BY ciudad ORDER BY c DESC LIMIT 1", (PUNTO_DE_CORTE,)
    ).fetchone()
    if ciudad:
        hallazgos.append({
            "titulo": "Concentración geográfica",
            "detalle": f"{ciudad['ciudad']} concentra el mayor volumen de oportunidades de "
                       f"recuperación, con {ciudad['c']} clientes priorizables.",
        })

    # 3. Plan Premium: tasa de reactivación histórica vs plan básico
    def conv_plan(plan):
        contactados = conn.execute(
            "SELECT COUNT(DISTINCT g.prospecto_id) AS c FROM gestiones_reactivacion g "
            "JOIN prospectos p ON p.id = g.prospecto_id WHERE p.plan_previo = ?", (plan,)
        ).fetchone()["c"]
        react = conn.execute(
            "SELECT COUNT(DISTINCT g.prospecto_id) AS c FROM gestiones_reactivacion g "
            "JOIN prospectos p ON p.id = g.prospecto_id WHERE p.plan_previo = ? AND g.resultado = 'reactivado'",
            (plan,)
        ).fetchone()["c"]
        return _pct(react, contactados)

    tasas_plan = {"Premium": conv_plan("premium"), "medio": conv_plan("medio"), "básico": conv_plan("basico")}
    mejor_plan = max(tasas_plan, key=tasas_plan.get)
    peor_plan = min(tasas_plan, key=tasas_plan.get)
    hallazgos.append({
        "titulo": f"El plan {mejor_plan} responde mejor",
        "detalle": f"La tasa histórica de reactivación del plan {mejor_plan} es del "
                   f"{tasas_plan[mejor_plan]}%, frente al {tasas_plan[peor_plan]}% del plan "
                   f"{peor_plan}: conviene ajustar la oferta por tipo de plan.",
    })

    # 4. Efectividad del contacto comercial
    g_total = conn.execute("SELECT COUNT(*) AS c FROM gestiones_reactivacion").fetchone()["c"]
    g_efect = conn.execute(
        "SELECT COUNT(*) AS c FROM gestiones_reactivacion WHERE resultado IN ('interesado','reactivado')"
    ).fetchone()["c"]
    hallazgos.append({
        "titulo": "Efectividad del contacto",
        "detalle": f"El {_pct(g_efect, g_total)}% de las gestiones realizadas generan interés o "
                   f"reactivación: el contacto asistido mejora la conversión Winback.",
    })

    conn.close()
    return {"hallazgos": hallazgos}
