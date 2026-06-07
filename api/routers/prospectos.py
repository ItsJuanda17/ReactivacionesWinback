# GET /prospectos — ranking de prospectos con filtro por segmento
import sqlite3
from fastapi import APIRouter, Query
from config import DB_PATH

router = APIRouter()

SEGMENTOS_VALIDOS = {'diamante', 'oro', 'plata', 'bronce'}


@router.get("")
def listar_prospectos(
    segmento: str | None = Query(None, description="diamante | oro | plata | bronce"),
    limit: int = Query(50, ge=1, le=2000),
):
    """Devuelve prospectos ordenados por probabilidad de reactivación (desc)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    sql = "SELECT * FROM prospectos"
    params = []
    if segmento and segmento in SEGMENTOS_VALIDOS:
        sql += " WHERE segmento = ?"
        params.append(segmento)
    sql += " ORDER BY prob_reactivacion DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]
