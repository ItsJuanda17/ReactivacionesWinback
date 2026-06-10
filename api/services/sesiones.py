"""Persistencia de sesiones de chat para conversaciones multi-canal (Telegram/WhatsApp).

Permite que N8N (u otro orquestador) sea *stateless*: solo reenvía `{user_id, texto}`
y la API recuerda en qué punto del flujo va cada usuario. SQLite es la única fuente
de verdad del estado conversacional.
"""
import sqlite3
from datetime import datetime, timezone

from config import DB_PATH


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def asegurar_tabla() -> None:
    """Crea la tabla de sesiones si no existe (idempotente)."""
    conn = _conn()
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS sesiones_chat ("
            "  user_id    TEXT PRIMARY KEY,"
            "  canal      TEXT,"
            "  estado     TEXT NOT NULL,"
            "  updated_at TEXT NOT NULL"
            ")"
        )
        conn.commit()
    finally:
        conn.close()


def obtener_estado(user_id: str) -> str | None:
    """Devuelve el estado actual del usuario, o None si no hay sesión abierta."""
    conn = _conn()
    try:
        row = conn.execute(
            "SELECT estado FROM sesiones_chat WHERE user_id = ?", (user_id,)
        ).fetchone()
        return row["estado"] if row else None
    finally:
        conn.close()


def guardar_estado(user_id: str, canal: str, estado: str) -> None:
    """Inserta o actualiza el estado del usuario (upsert)."""
    conn = _conn()
    try:
        conn.execute(
            "INSERT INTO sesiones_chat (user_id, canal, estado, updated_at) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET "
            "  canal = excluded.canal, estado = excluded.estado, updated_at = excluded.updated_at",
            (user_id, canal, estado, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()
