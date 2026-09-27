"""Persistence layer for games -- a thin wrapper around Postgres so app.py
never touches SQL directly. Games are stored as a single JSONB blob per row,
with Postgres used as solely a durable key-value store (which is otherwise 
unavailable with Render's free hosting tier)"""
import os

import psycopg
from psycopg.types.json import Jsonb

DATABASE_URL = os.environ["DATABASE_URL"]


def init_db():
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS games (
                id TEXT PRIMARY KEY,
                state JSONB NOT NULL,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )


def save(game_id: str, state: dict) -> None:
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute(
            """
            INSERT INTO games (id, state, updated_at)
            VALUES (%s, %s, now())
            ON CONFLICT (id) DO UPDATE SET state = EXCLUDED.state, updated_at = now()
            """,
            (game_id, Jsonb(state)),
        )


def load(game_id: str) -> dict | None:
    with psycopg.connect(DATABASE_URL) as conn:
        row = conn.execute("SELECT state FROM games WHERE id = %s", (game_id,)).fetchone()
    return row[0] if row else None


def list_all() -> dict[str, dict]:
    with psycopg.connect(DATABASE_URL) as conn:
        rows = conn.execute("SELECT id, state FROM games").fetchall()
    return {game_id: state for game_id, state in rows}
