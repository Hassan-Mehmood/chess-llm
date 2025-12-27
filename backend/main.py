from typing import Optional
import chess
from chess import IllegalMoveError, InvalidMoveError

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_groq import ChatGroq

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

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


@app.get("/reset")
def reset():
    board.reset_board()

    return {"success": True}


@app.get("/game_state")
def main():
    resp = {
        "fen": board.board_fen(),
        "turn": board.turn,
        "is_check": board.is_check(),
        "is_checkmate": board.is_checkmate(),
        "is_game_over": board.is_game_over(),
        "illegalmove": False,
    }

    print(resp)

    return resp


@app.post("/move")
def move(data: move_type):
    source_square = data.sourceSquare
    target_square = data.targetSquare

    # Base response (always exists)
    resp = {
        "fen": board.board_fen(),
        "turn": board.turn,
        "is_check": board.is_check(),
        "is_checkmate": board.is_checkmate(),
        "is_game_over": board.is_game_over(),
        "illegalmove": False,
    }

    try:
        board.push_uci(source_square + target_square)

        # Update response after successful move
        resp.update(
            {
                "fen": board.board_fen(),
                "turn": board.turn,
                "is_check": board.is_check(),
                "is_checkmate": board.is_checkmate(),
                "is_game_over": board.is_game_over(),
            }
        )

        return resp

    except (IllegalMoveError, InvalidMoveError):
        resp["illegalmove"] = True
        return resp


class ai_move_type(BaseModel):
    turn: Optional[bool | None]
    model: Optional[str | None]


MAX_ILLEGAL_MOVES = 5


@app.post("/ai_move")
def ai_move(data: ai_move_type):
    resp = {
        "fen": board.board_fen(),
        "turn": board.turn,
        "is_check": board.is_check(),
        "is_checkmate": board.is_checkmate(),
        "is_game_over": board.is_game_over(),
        "illegalmove": False,
    }

    for i in range(MAX_ILLEGAL_MOVES):
        try:
            prompt = get_chess_prompt(data)
            print("Turn: ", "White" if data.turn else "Black")

            print("Using model:", data.model)

            if data.model == "OPENAI":
                llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    api_key=os.getenv("OPENAI_API_KEY"),
                    temperature=1,
                    max_tokens=30,
                    # reasoning_effort="high",
                )

            elif data.model == "CLAUDE":
                llm = ChatAnthropic(
                    model="claude-haiku-4-5-20251001",
                    temperature=1,
                    max_tokens=30,
                    api_key=os.getenv("CLAUDE_API_KEY"),
                )
            else:
                llm = ChatGroq(
                    api_key=os.getenv("GROQ_API_KEY"),
                    model=data.model,
                    temperature=1,
                    max_tokens=30,
                    # reasoning_format="parsed",
                    timeout=None,
                    max_retries=2,
                )

            response = llm.invoke(prompt)
            move = response.content
            print("AI Selected Move", move)
            board.push_uci(move)

            resp.update(
                {
                    "fen": board.board_fen(),
                    "turn": board.turn,
                    "is_check": board.is_check(),
                    "is_checkmate": board.is_checkmate(),
                    "is_game_over": board.is_game_over(),
                    "illegalmove": False,
                }
            )

            return resp

        except (IllegalMoveError, InvalidMoveError) as e:
            print("IllegalMoveError, InvalidMoveError", str(e))

            if i >= MAX_ILLEGAL_MOVES:
                raise Exception("MAX Illegal moves reached")

            print(f"Illegal move detected. Retrying again: {i + 1}/5")

            # print("illegal move", str(e))
            # resp["illegalmove"] = True
            # return resp

        except Exception as e:
            print(str(e))

            if i >= MAX_ILLEGAL_MOVES:
                raise Exception("MAX Illegal moves reached")


def get_chess_prompt(ai_move_data):
    print("AI_MOVE_DATA", ai_move_data)

    legal_moves = []
    for move in board.legal_moves:
        legal_moves.append(move.uci())

    print("legal moves", legal_moves)

    move_stack = board.move_stack
    last_move = move_stack[-1] if len(move_stack) > 0 else None

    # print("MOVE_STACK", move_stack)
    print("LAST MOVE", last_move)

    # - Move Stack (History): {move_stack}
    return f"""
        You are a world-class chess grandmaster. You are playing as {"WHITE" if ai_move_data.turn else "BLACK"}.

        # Current Game State:
        - Board (FEN): {board.board_fen()}
        - Your Turn: {"WHITE" if ai_move_data.turn else "BLACK"}
        - Last Move (UCI): {last_move}
        - Is Check: {board.is_check()}
        - Is Checkmate: {board.is_checkmate()}
        - Is Stalemate: {board.is_stalemate()}
        - Is Game Over: {board.is_game_over()}

        # Your Task:
        Analyze the current board and game state to determine the optimal next move.
        Your response **MUST** be only the next move in UCI format.

        # Legal Moves:
        Choose one of the following legal moves:
        {legal_moves}

        # UCI Format Rules:
        - A move is represented as a four-character string (e.g., 'e2e4', 'g1f3').
        - For pawn promotions, add a fifth character for the promotion piece (e.g., 'a7a8q' for Queen).
        - Do not use SAN (Standard Algebraic Notation) or any other format.

        ## Valid UCI Examples:
        - 'e2e4'   (Pawn moves two squares)
        - 'g1f3'   (Knight to f3)
        - 'e1g1'   (White kingside castle)
        - 'a7a8q'  (Pawn promotion to Queen)

        ## Invalid Move Examples:
        - 'Nf3'    (SAN format)
        - 'e4'     (Too short)
        - 'O-O'    (SAN castling)
        - 'e2-e4'  (Contains a hyphen)

        Generate only the move, with no extra text, explanation, or reasoning. An invalid move will cause an error.
        """


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
