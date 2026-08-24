#!/usr/bin/env python3
"""
Stage 2: adds the create-game endpoint.
"""
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator, field_validator
from Quoridor_objects import QuoridorGame

app = FastAPI()

# TODO: once the frontend has a real hosted address, replace "*" with that
# specific origin (e.g. "https://quoridor-frontend.onrender.com") instead
# of allowing every origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

games: dict[str, QuoridorGame] = {}  # game_id -> QuoridorGame, held in server memory


def get_game(game_id: str) -> QuoridorGame:
    """Look up a game by ID, or raise a clean 404 instead of a raw KeyError."""
    game = games.get(game_id)
    if game is None:
        raise HTTPException(status_code=404, detail=f"No game found with ID '{game_id}'.")
    return game


@app.get("/health")
def health():
    return {"status": "ok"}


class CreateGameRequest(BaseModel):
    player1_name: str = Field(min_length=1)
    player2_name: str = Field(min_length=1)
    size: int = 9
    fences: int = 10

    @field_validator("size", mode="before")
    @classmethod
    def validate_size(cls, v):
        try:
            v = int(v)
        except (TypeError, ValueError):
            v = None
        if v is None or not (3 <= v <= 10):
            raise ValueError("Board size (rows/columns) must be a number between 3 and 10 (default 9) - please try again.")
        return v

    @field_validator("fences", mode="before")
    @classmethod
    def validate_fences(cls, v):
        try:
            v = int(v)
        except (TypeError, ValueError):
            v = None
        if v is None or not (1 <= v <= 15):
            raise ValueError("Fences must be a whole number from 1 to 15 (default 10) - please try again.")
        return v

@app.post("/games")
def create_game(req: CreateGameRequest):
    game_id = uuid.uuid4().hex[:8]  # short random id, e.g. "a3f9c21b"
    games[game_id] = QuoridorGame(req.player1_name, req.player2_name, size=req.size, fences=req.fences)
    return {"game_id": game_id, "state": games[game_id].serialize()}

@app.get("/games/{game_id}")
def get_state(game_id: str):
    return get_game(game_id).serialize()


class MoveRequest(BaseModel):
    player_index: int
    direction: str

@app.post("/games/{game_id}/move")
def move(game_id: str, req: MoveRequest):
    return get_game(game_id).move_piece(req.player_index, req.direction)


class FenceRequest(BaseModel):
    player_index: int
    row: int
    col: int
    orientation: str

@app.post("/games/{game_id}/fence")
def place_fence(game_id: str, req: FenceRequest):
    return get_game(game_id).place_fence(req.player_index, req.row, req.col, req.orientation)
