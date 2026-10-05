#!/usr/bin/env python3
"""
Stage 2: adds the create-game endpoint.
"""
import os
import random
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator, model_validator
from Quoridor_objects import QuoridorGame
import storage

app = FastAPI()
storage.init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://quoridor-7oai.onrender.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_state_or_404(game_id: str) -> dict:
    # Look up a game's stored state by ID, or 404 error message
    state = storage.load(game_id)
    if state is None:
        raise HTTPException(status_code=404, detail=f"No game found with ID '{game_id}'.")
    return state


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def serve_frontend():
    # Browser and api serve the same static frontend
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))


@app.get("/logo.svg")
def serve_logo():
    return FileResponse(os.path.join(os.path.dirname(__file__), "logo.svg"))


@app.get("/example-board.svg")
def serve_example_board():
    return FileResponse(os.path.join(os.path.dirname(__file__), "example-board.svg"))


@app.get("/fence-example.svg")
def serve_fence_example():
    return FileResponse(os.path.join(os.path.dirname(__file__), "fence-example.svg"))


PLAYER_COLORS = {"blue", "red", "green", "yellow", "purple", "orange"}  # hex values in index.html

class CreateGameRequest(BaseModel):
    player1_name: str
    player2_name: str = Field(min_length=1)
    size: int = 9
    fences: int = 10
    player1_color: str = "blue"
    player2_color: str = "red"

    @model_validator(mode="after")
    def validate_colors(self):
        if self.player1_color not in PLAYER_COLORS or self.player2_color not in PLAYER_COLORS:
            raise ValueError("Unknown player color - please pick one from the list.")
        if self.player1_color == self.player2_color:
            raise ValueError("Both players picked the same color - please pick two different ones.")
        return self

    @field_validator("player1_name")
    @classmethod
    def validate_player1_name(cls, v):
        if not v.strip():
            raise ValueError("Enter at least your own name (in the first box) before creating a game.")
        return v

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
    game = QuoridorGame(req.player1_name, req.player2_name, size=req.size, fences=req.fences,
                        player1_color=req.player1_color, player2_color=req.player2_color)
    # Seats and board sides fixed (creator always top, joiner always on bottom), 
    # but who moves first is randomized.
    game.current_player = random.choice([0, 1])
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


class JoinRequest(BaseModel):
    name: str = ""

@app.post("/games/{game_id}/join")
def join_game(game_id: str, req: JoinRequest):
    game = QuoridorGame.from_state(load_state_or_404(game_id))
    result = game.join(req.name)
    if result["ok"] and result["claimed_now"]:
        storage.save(game_id, result["state"])
    return result


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

@app.post("/games/{game_id}/fence/preview")
def preview_fence(game_id: str, req: FenceRequest):
    # Validate fence placement for preview (but not saving
    # new gamestate until player confirms)
    game = QuoridorGame.from_state(load_state_or_404(game_id))
    return game.place_fence(req.player_index, req.row, req.col, req.orientation)


@app.post("/games/{game_id}/fence")
def place_fence(game_id: str, req: FenceRequest):
    game = QuoridorGame.from_state(load_state_or_404(game_id))
    result = game.place_fence(req.player_index, req.row, req.col, req.orientation)
    if result["ok"]:
        storage.save(game_id, result["state"])
    return result


class UndoRequest(BaseModel):
    player_index: int

@app.post("/games/{game_id}/undo")
def undo(game_id: str, req: UndoRequest):
    # Ensure only the player who actually made the last move/fence can undo it --
    state = load_state_or_404(game_id)
    history = state.get("history", [])
    if not history:
        return {"ok": False, "error": "Nothing to undo."}
    if history[-1]["player_index"] != req.player_index:
        return {"ok": False, "error": "Can't undo — your opponent made the last move."}
    new_state = storage.undo(game_id)
    if new_state is None:
        return {"ok": False, "error": "Nothing to undo."}
    return {"ok": True, "state": new_state}
