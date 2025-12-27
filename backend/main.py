import chess
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os 
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_groq import ChatGroq

load_dotenv()


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


@app.post("/ai_move")
def ai_move(ai_move_data: move_type):
    board.push_uci(ai_move_data.sourceSquare + ai_move_data.targetSquare)
    print("inside ai move", ai_move_data)
    prompt = get_chess_prompt(ai_move_data)
    llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="qwen/qwen3-32b",
    temperature=1,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2,
)
    response = llm.invoke(prompt)
    print("response", response.content)
    move = response.content
    board.push_uci(move)
    return {"fen": board.board_fen()}


def get_chess_prompt(ai_move_data):
    return f"""
    You are a an expert chest player. You are provided with the data of the last move and based on that move you have to generate the next move.
    The board is given in FEN format {board.board_fen()}.
    You are the player of the white side if the last move is made by the black side, otherwise you are the player of the black side. last moved piecetype {ai_move_data.piece.pieceType}, w mean white pawn, b mean black pawn.
    The last move is given in UCI format {ai_move_data.sourceSquare + ai_move_data.targetSquare}.
    You have to generate the next move in UCI format.
    legal moves are {board.legal_moves}.
    Generate only the move, no extra text or explanation or reasoning.
    """

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
