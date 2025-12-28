import json
import chess
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from src.models import ai_move_type, ChessMove
from src.chessGame import ChessGame
from chess import IllegalMoveError, InvalidMoveError
from src.config import settings
from langchain.chat_models import init_chat_model


class ChessLLMAgents:
    def __init__(self):
        self.MAX_ILLEGAL_MOVES = 5
        self.chessGame = ChessGame()

    async def ai_move(self, data: ai_move_type):
        resp = {
            "fen": self.chessGame.board.board_fen(),
            "turn": self.chessGame.board.turn,
            "is_check": self.chessGame.board.is_check(),
            "is_checkmate": self.chessGame.board.is_checkmate(),
            "is_game_over": self.chessGame.board.is_game_over(),
            "illegalmove": False,
        }

        for i in range(self.MAX_ILLEGAL_MOVES):
            try:
                prompt = await self.get_chess_prompt(data)
                print("Turn: ", "White" if data.turn else "Black")

                # print("Using model:", data.model)

                if "OPENAI/" in data.model:
                    # trim CLAUDE from model name
                    model_name = data.model.replace("OPENAI/", "")
                    print("Using model:", model_name)
                    # llm = ChatOpenAI(
                    #     model=model_name,
                    #     api_key=settings.OPENAI_API_KEY,
                    #     temperature=1,
                    #     max_tokens=30,
                    #     # reasoning_effort="high",
                    # )

                    llm = init_chat_model(model_name)

                    llm = llm.with_structured_output(ChessMove)

                elif "claude" in data.model:
                    print("Using model:", data.model)
                    # llm = ChatAnthropic(
                    #     model=data.model,
                    #     temperature=1,
                    #     max_tokens=30,
                    #     api_key=settings.CLAUDE_API_KEY,
                    # )

                    llm = init_chat_model(
                        data.model,
                    )

                    llm = llm.with_structured_output(ChessMove)

                elif "gemini" in data.model:
                    print("Using model:", data.model)
                    llm = ChatGoogleGenerativeAI(
                        model=data.model,
                        temperature=1.0,
                        max_tokens=30,
                        api_key=settings.GEMINI_API_KEY,
                    )
                    llm = llm.with_structured_output(ChessMove)

                else:
                    print("Using model:", data.model)
                    llm = ChatGroq(
                        api_key=settings.GROQ_API_KEY,
                        model=data.model,
                        temperature=1,
                        max_tokens=30,
                        # reasoning_format="parsed",
                        timeout=None,
                        max_retries=2,
                    )

                print("-" * 50)
                print(prompt)
                print("-" * 50)

                response = llm.invoke(prompt)
                move = response.move
                print("AI Selected Move", move)
                self.chessGame.board.push_uci(move)

                resp.update(
                    {
                        "fen": self.chessGame.board.board_fen(),
                        "turn": self.chessGame.board.turn,
                        "is_check": self.chessGame.board.is_check(),
                        "is_checkmate": self.chessGame.board.is_checkmate(),
                        "is_game_over": self.chessGame.board.is_game_over(),
                        "illegalmove": False,
                    }
                )

                return resp

            except (IllegalMoveError, InvalidMoveError) as e:
                print("IllegalMoveError, InvalidMoveError", str(e))

                if i >= self.MAX_ILLEGAL_MOVES:
                    raise Exception("MAX Illegal moves reached")

                print(f"Illegal move detected. Retrying again: {i + 1}/5")

                # print("illegal move", str(e))
                # resp["illegalmove"] = True
                # return resp

            except Exception as e:
                print(str(e))

                if i >= self.MAX_ILLEGAL_MOVES:
                    raise Exception("MAX Illegal moves reached")

    # async def get_chess_prompt(self, ai_move_data):
    #     print("AI_MOVE_DATA", ai_move_data)

    #     legal_moves = []
    #     for move in self.chessGame.board.legal_moves:
    #         legal_moves.append(move.uci())

    #     print("legal moves", legal_moves)

    #     move_stack = self.chessGame.board.move_stack
    #     last_move = move_stack[-1] if len(move_stack) > 0 else None

    #     # print("MOVE_STACK", move_stack)
    #     print("LAST MOVE", last_move)

    #     asci_board = str(self.chessGame.board)

    #     # - Move Stack (History): {move_stack}
    #     # - Board (FEN): {self.chessGame.board.board_fen()}
    #     return f"""
    #         You are a world-class chess grandmaster. You are playing as {"WHITE" if ai_move_data.turn else "BLACK"}.

    #         # Current Game State:
    #         - Turn: {"WHITE" if ai_move_data.turn else "BLACK"}
    #         - Board:
    #         {asci_board}
    #         - Last Move (UCI): {last_move}
    #         - Is Check: {self.chessGame.board.is_check()}
    #         - Is Checkmate: {self.chessGame.board.is_checkmate()}
    #         - Is Stalemate: {self.chessGame.board.is_stalemate()}
    #         - Is Game Over: {self.chessGame.board.is_game_over()}

    #         # Your Task:
    #         Analyze the current board and game state to determine the optimal next move.
    #         Your response **MUST** be only the next move in UCI format.

    #         # Legal Moves:
    #         Choose one of the following legal moves:
    #         You cannot select any move other than the following moves. You will be disqualified if you try to output any other move.
    #         {legal_moves}

    #         # UCI Format Rules:
    #         - A move is represented as a four-character string (e.g., 'e2e4', 'g1f3').
    #         - For pawn promotions, add a fifth character for the promotion piece (e.g., 'a7a8q' for Queen).
    #         - Do not use SAN (Standard Algebraic Notation) or any other format.

    #         ## Valid UCI Examples:
    #         - 'e2e4'   (Pawn moves two squares)
    #         - 'g1f3'   (Knight to f3)
    #         - 'e1g1'   (White kingside castle)
    #         - 'a7a8q'  (Pawn promotion to Queen)

    #         ## Invalid Move Examples:
    #         - 'Nf3'    (SAN format)
    #         - 'e4'     (Too short)
    #         - 'O-O'    (SAN castling)
    #         - 'e2-e4'  (Contains a hyphen)

    #         Generate only the move, with no extra text, explanation, or reasoning. An invalid move will cause an error.
    #         """

    async def get_chess_prompt(self, ai_move_data):
        # legal moves as simple list of UCI strings
        legal_moves = [m.uci() for m in self.chessGame.board.legal_moves]

        move_stack = self.chessGame.board.move_stack
        last_move = move_stack[-1].uci() if len(move_stack) > 0 else None

        # ASCII board with ranks and files (python-chess str(board) uses case: UPPER=White, lower=Black)
        ascii_board = str(self.chessGame.board)
        # add rank/file labels to make spatial orientation explicit
        rows = ascii_board.splitlines()
        labeled_rows = []
        rank = 8
        for r in rows:
            labeled_rows.append(f"{rank} | {r}")
            rank -= 1
        labeled_rows.append("    a b c d e f g h")
        labeled_board = "\n".join(labeled_rows)

        # Structured square -> piece mapping (human readable)
        piece_map = {}
        for sq, piece in self.chessGame.board.piece_map().items():
            # e.g. 'a2': 'white_pawn' or 'b8': 'black_knight'
            color = "white" if piece.color == chess.WHITE else "black"
            kind = {
                chess.PAWN: "pawn",
                chess.ROOK: "rook",
                chess.KNIGHT: "knight",
                chess.BISHOP: "bishop",
                chess.QUEEN: "queen",
                chess.KING: "king",
            }[piece.piece_type]
            piece_map[chess.square_name(sq)] = f"{color}_{kind}"

        # compact JSON string for model
        piece_map_json = json.dumps(piece_map, sort_keys=True)

        # FEN (canonical)
        fen = self.chessGame.board.board_fen()

        return f"""
You are a world-class chess grandmaster. You are playing as {"WHITE" if ai_move_data.turn else "BLACK"}.

BOARD ENCODING RULES (IMPORTANT):
- Uppercase letters = WHITE pieces; Lowercase letters = BLACK pieces.
- P/p = pawn, R/r = rook, N/n = knight, B/b = bishop, Q/q = queen, K/k = king
- '.' = empty square
- Use ONLY the provided legal moves list. Do NOT invent moves.
- Output MUST be exactly one move in UCI (e.g., 'e2e4') and nothing else.

- Board (FEN): {fen}
- Structured pieces (square -> piece):
{piece_map_json}

# Current Game State:
- Turn: {"WHITE" if ai_move_data.turn else "BLACK"}
- Board (visual):
{labeled_board}


- Last Move (UCI): {last_move}
- Is Check: {self.chessGame.board.is_check()}
- Is Checkmate: {self.chessGame.board.is_checkmate()}
- Is Stalemate: {self.chessGame.board.is_stalemate()}
- Is Game Over: {self.chessGame.board.is_game_over()}

# Your Task:
Analyze the current board and pick the single best next move for {"WHITE" if ai_move_data.turn else "BLACK"}.
Return ONLY the chosen move in UCI format, exactly one token. No explanation, no commentary.

# Legal Moves (must choose one):
{legal_moves}

# UCI Format Rules:
- Four characters for a normal move (e.g., 'e2e4'), add a fifth for promotion (e.g., 'a7a8q').
- Do NOT use SAN like 'Nf3' or any other format.

GENERATE ONLY THE MOVE.
"""


chessllmagents = ChessLLMAgents()
