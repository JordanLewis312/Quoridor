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
        # CREATE TABLE IF NOT EXISTS is a no-op on a table that already
        # exists, so a new column needs its own explicit migration step.
        conn.execute("ALTER TABLE games ADD COLUMN IF NOT EXISTS previous_state JSONB")


def save(game_id: str, state: dict) -> None:
    """Save a new state, shifting whatever was there before into
    previous_state -- giving exactly one level of undo. A brand-new game
    (no existing row) leaves previous_state NULL, since there's nothing
    to undo back to yet."""
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute(
            """
            INSERT INTO games (id, state, previous_state, updated_at)
            VALUES (%s, %s, NULL, now())
            ON CONFLICT (id) DO UPDATE
                SET previous_state = games.state, state = EXCLUDED.state, updated_at = now()
            """,
            (game_id, Jsonb(state)),
        )


def undo(game_id: str) -> dict | None:
    """Restore previous_state back into state. Returns the restored state,
    or None if there's nothing to undo (either no such game, or this game's
    last action has already been undone once).

    TODO: not currently called by the fence-confirm flow -- that now uses
    a validate-without-saving preview instead, since undoing an already
    -committed action is visible to the opponent before you get a chance
    to revert it (a real multiplayer bug we hit and fixed). This is kept
    dormant for a future "undo my completed last turn" feature, which
    will additionally need a way to notify the opponent it happened, not
    just rely on their next poll."""
    with psycopg.connect(DATABASE_URL) as conn:
        row = conn.execute(
            """
            UPDATE games
            SET state = previous_state, previous_state = NULL
            WHERE id = %s AND previous_state IS NOT NULL
            RETURNING state
            """,
            (game_id,),
        ).fetchone()
    return row[0] if row else None


def load(game_id: str) -> dict | None:
    with psycopg.connect(DATABASE_URL) as conn:
        row = conn.execute("SELECT state FROM games WHERE id = %s", (game_id,)).fetchone()
    return row[0] if row else None


def list_all() -> dict[str, dict]:
    with psycopg.connect(DATABASE_URL) as conn:
        rows = conn.execute("SELECT id, state FROM games").fetchall()
    return {game_id: state for game_id, state in rows}
