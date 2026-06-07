# GET /prospectos — ranking de prospectos con filtro por segmento + KPIs de resumen
import sqlite3
from fastapi import APIRouter, Query
from config import DB_PATH

router = APIRouter()

SEGMENTOS_VALIDOS = {'diamante', 'oro', 'plata', 'bronce'}
PUNTO_DE_CORTE = 0.55


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("")
def listar_prospectos(
    segmento: str | None = Query(None, description="diamante | oro | plata | bronce"),
    buscar: str | None = Query(None, description="Filtra por nombre o ciudad"),
    limit: int = Query(50, ge=1, le=2000),
):
    """Devuelve prospectos ordenados por probabilidad de reactivación (desc)."""
    conn = _conn()
    sql = "SELECT * FROM prospectos"
    where, params = [], []
    if segmento and segmento in SEGMENTOS_VALIDOS:
        where.append("segmento = ?")
        params.append(segmento)
    if buscar:
        where.append("(nombre_completo LIKE ? OR ciudad LIKE ?)")
        params += [f"%{buscar}%", f"%{buscar}%"]
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY prob_reactivacion DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/resumen")
def resumen_kpis():
    """KPIs de impacto comercial para el tablero principal."""
    conn = _conn()
    total = conn.execute("SELECT COUNT(*) AS c FROM prospectos").fetchone()["c"]
    alta = conn.execute(
        "SELECT COUNT(*) AS c FROM prospectos WHERE prob_reactivacion >= ?",
        (PUNTO_DE_CORTE,),
    ).fetchone()["c"]
    prob_media = conn.execute("SELECT AVG(prob_reactivacion) AS p FROM prospectos").fetchone()["p"]
    valor_recuperable = conn.execute(
        "SELECT COALESCE(SUM(valor_plan_cop), 0) AS v FROM prospectos WHERE prob_reactivacion >= ?",
        (PUNTO_DE_CORTE,),
    ).fetchone()["v"]
    por_segmento = {
        r["segmento"]: r["c"]
        for r in conn.execute(
            "SELECT segmento, COUNT(*) AS c FROM prospectos GROUP BY segmento"
        ).fetchall()
    }

    # Oportunidades de recuperación por ciudad (prospectos priorizables)
    por_ciudad = [
        {"ciudad": r["ciudad"], "oportunidades": r["c"]}
        for r in conn.execute(
            "SELECT ciudad, COUNT(*) AS c FROM prospectos WHERE prob_reactivacion >= ? "
            "GROUP BY ciudad ORDER BY c DESC LIMIT 8",
            (PUNTO_DE_CORTE,),
        ).fetchall()
    ]

    # Efectividad de la gestión comercial histórica
    g_total = conn.execute("SELECT COUNT(*) AS c FROM gestiones_reactivacion").fetchone()["c"]
    g_efectivas = conn.execute(
        "SELECT COUNT(*) AS c FROM gestiones_reactivacion WHERE resultado IN ('interesado','reactivado')"
    ).fetchone()["c"]
    contactados = conn.execute(
        "SELECT COUNT(DISTINCT prospecto_id) AS c FROM gestiones_reactivacion"
    ).fetchone()["c"]
    reactivados = conn.execute(
        "SELECT COUNT(DISTINCT prospecto_id) AS c FROM gestiones_reactivacion WHERE resultado = 'reactivado'"
    ).fetchone()["c"]
    conn.close()

    return {
        "total_prospectos": total,
        "alta_probabilidad": alta,
        "pct_alta_probabilidad": round(alta / total, 4) if total else 0,
        "prob_media": round(prob_media or 0, 4),
        "valor_recuperable_cop": int(valor_recuperable),
        "reactivados": reactivados,
        "contactados": contactados,
        "tasa_contacto_efectiva": round(g_efectivas / g_total, 4) if g_total else 0,
        "conversion_historica": round(reactivados / contactados, 4) if contactados else 0,
        "por_segmento": por_segmento,
        "por_ciudad": por_ciudad,
    }
