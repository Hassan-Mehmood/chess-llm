import chess
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel


class Piece(BaseModel):
    isSparePiece: bool
    position: str
    pieceType: str


class move_type(BaseModel):
    piece: Piece
    sourceSquare: str
    targetSquare: str | None


app = FastAPI()

# add corsMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


board = chess.Board()


@app.get("/game_state")
def main():
    fen = board.board_fen()

    print(fen)

    return {"fen": fen}


# class move_type:
#     piece:


@app.post("/move")
def move(data: move_type):
    piece = data.piece
    sourceSquare = data.sourceSquare
    targetSquare = data.targetSquare

    if targetSquare is None:
        return {"fen": board.board_fen()}

    else:
        board.push_uci(sourceSquare + targetSquare)

    return {"fen": board.board_fen()}


# {
#     "piece": {
#         "isSparePiece": false,
#         "position": "e2",
#         "pieceType": "wP"
#     },
#     "sourceSquare": "e2",
#     "targetSquare": "e3"
# }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
