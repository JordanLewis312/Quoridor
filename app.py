#!/usr/bin/env python3
"""
Stage 2: adds the create-game endpoint.
"""
import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator
from Quoridor_objects import QuoridorGame
import storage

app = FastAPI()
storage.init_db()

# TODO: once the frontend has a real hosted address, replace "*" with that
# specific origin (e.g. "https://quoridor-frontend.onrender.com") instead
# of allowing every origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_state_or_404(game_id: str) -> dict:
    """Look up a game's stored state by ID, or raise a clean 404 instead of
    letting a missing row surface as nothing/None further down."""
    state = storage.load(game_id)
    if state is None:
        raise HTTPException(status_code=404, detail=f"No game found with ID '{game_id}'.")
    return state


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def serve_frontend():
    """Serve the static frontend so the browser and API share one origin
    (one Render web service, no CORS headaches for the deployed version)."""
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))


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
    game = QuoridorGame(req.player1_name, req.player2_name, size=req.size, fences=req.fences)
    storage.save(game_id, game.serialize())
    return {"game_id": game_id, "state": game.serialize()}


@app.get("/games")
def list_games():
    return {
        game_id: {
            "players": [p["name"] for p in state["players"]],
            "status": state["status"],
        }
        for game_id, state in storage.list_all().items()
    }

@app.get("/games/{game_id}")
def get_state(game_id: str):
    return load_state_or_404(game_id)


class MoveRequest(BaseModel):
    player_index: int
    direction: str

@app.post("/games/{game_id}/move")
def move(game_id: str, req: MoveRequest):
    game = QuoridorGame.from_state(load_state_or_404(game_id))
    result = game.move_piece(req.player_index, req.direction)
    if result["ok"]:
        storage.save(game_id, result["state"])
    return result


class FenceRequest(BaseModel):
    player_index: int
    row: int
    col: int
    orientation: str

@app.post("/games/{game_id}/fence")
def place_fence(game_id: str, req: FenceRequest):
    game = QuoridorGame.from_state(load_state_or_404(game_id))
    result = game.place_fence(req.player_index, req.row, req.col, req.orientation)
    if result["ok"]:
        storage.save(game_id, result["state"])
    return result
