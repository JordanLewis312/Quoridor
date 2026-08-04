#!/usr/bin/env python3
"""
Stage 2: adds the create-game endpoint.
"""
import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from Quoridor_objects import QuoridorGame

app = FastAPI()

games: dict[str, QuoridorGame] = {}  # game_id -> QuoridorGame, held in server memory

@app.get("/health")
def health():
    return {"status": "ok"}


class CreateGameRequest(BaseModel):
    player1_name: str
    player2_name: str
    size: int = 9
    fences: int = 10

@app.post("/games")
def create_game(req: CreateGameRequest):
    game_id = uuid.uuid4().hex[:8]  # short random id, e.g. "a3f9c21b"
    games[game_id] = QuoridorGame(req.player1_name, req.player2_name, size=req.size, fences=req.fences)
    return {"game_id": game_id, "state": games[game_id].serialize()}

@app.get("/games/{game_id}")
def get_state(game_id: str):
    return games[game_id].serialize()


class MoveRequest(BaseModel):
    player_index: int
    direction: str

@app.post("/games/{game_id}/move")
def move(game_id: str, req: MoveRequest):
    return games[game_id].move_piece(req.player_index, req.direction)


class FenceRequest(BaseModel):
    player_index: int
    row: int
    col: int
    orientation: str

@app.post("/games/{game_id}/fence")
def place_fence(game_id: str, req: FenceRequest):
    return games[game_id].place_fence(req.player_index, req.row, req.col, req.orientation)
