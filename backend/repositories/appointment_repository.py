from typing import Optional

from database import get_connection


def create(customer_name: str, phone: str, date: str, time: str,
           purpose: Optional[str]) -> dict:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO appointments (customer_name, phone, date, time, purpose) "
            "VALUES (?, ?, ?, ?, ?)",
            (customer_name, phone, date, time, purpose),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM appointments WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return dict(row)
    finally:
        conn.close()


def get_by_id(appointment_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM appointments WHERE id = ?", (appointment_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def list_all(status: Optional[str] = None, date: Optional[str] = None) -> list[dict]:
    query = "SELECT * FROM appointments WHERE 1=1"
    params: list = []
    if status:
        query += " AND status = ?"
        params.append(status)
    if date:
        query += " AND date = ?"
        params.append(date)
    query += " ORDER BY date, time, id"

    conn = get_connection()
    try:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def find_booked_at(date: str, time: str) -> Optional[dict]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM appointments "
            "WHERE date = ? AND time = ? AND status = 'booked'",
            (date, time),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def mark_cancelled(appointment_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE appointments SET status = 'cancelled' WHERE id = ?",
            (appointment_id,),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM appointments WHERE id = ?", (appointment_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()