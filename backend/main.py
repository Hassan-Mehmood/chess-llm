from typing import Optional
import chess
from chess import IllegalMoveError, InvalidMoveError

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.chessGame import chessgame
from src.models import ai_move_type
from src.LLMAgents import chessllmagents


app = FastAPI(title = "AI CHESS GAMWE")

# add corsMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get("/reset")
async def reset():
    try:
        return await chessgame.reset()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/game_state")
async def game_state():
    try:
        return await chessgame.game_state()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai_move")
async def ai_move(data: ai_move_type):
    try:
        return await chessllmagents.ai_move(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
