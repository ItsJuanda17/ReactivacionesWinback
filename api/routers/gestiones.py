# POST /gestiones — registra el resultado de un contacto (lo escribe N8N tras cada interacción)
import sqlite3
import uuid
from datetime import date

from fastapi import APIRouter
from pydantic import BaseModel

from config import DB_PATH

router = APIRouter()

CANALES_VALIDOS = {'whatsapp', 'telegram', 'llamada', 'email', 'sms'}
RESULTADOS_VALIDOS = {
    'no_contesta', 'interesado', 'rechazado', 'reactivado', 'colgo', 'contactado',
}


class GestionIn(BaseModel):
    prospecto_id: str
    canal_contacto: str            # whatsapp | telegram | llamada | email | sms
    resultado: str                 # interesado | reactivado | rechazado | no_contesta ...
    asesor_id: str | None = None
    duracion_segundos: int | None = None


@router.post("")
def registrar_gestion(g: GestionIn):
    """Inserta una gestión de reactivación y devuelve el id generado."""
    gestion_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO gestiones_reactivacion "
            "(id, prospecto_id, fecha_contacto, canal_contacto, resultado, asesor_id, duracion_segundos) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (gestion_id, g.prospecto_id, date.today().isoformat(),
             g.canal_contacto, g.resultado, g.asesor_id, g.duracion_segundos),
        )
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "id": gestion_id}
