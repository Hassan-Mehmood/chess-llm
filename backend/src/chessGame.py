
import chess
from chess import IllegalMoveError, InvalidMoveError
from src.models import move_type

class ChessGame:
    def __init__(self):
        self.board = chess.Board()


    async def reset(self):
        self.board.reset_board()
        return {"success": True}


    async def game_state(self):
        resp = {
            "fen": self.board.board_fen(),
            "turn": self.board.turn,
            "is_check": self.board.is_check(),
            "is_checkmate": self.board.is_checkmate(),
            "is_game_over": self.board.is_game_over(),
            "illegalmove": False,
        }
        print(resp)
        return resp


    async def move(self, data: move_type):
        source_square = data.sourceSquare
        target_square = data.targetSquare

        # Base response (always exists)
        resp = {
            "fen": self.board.board_fen(),
            "turn": self.board.turn,
            "is_check": self.board.is_check(),
            "is_checkmate": self.board.is_checkmate(),
            "is_game_over": self.board.is_game_over(),
            "illegalmove": False,
        }

        try:
            self.board.push_uci(source_square + target_square)

            # Update response after successful move
            resp.update(
                {
                    "fen": self.board.board_fen(),
                    "turn": self.board.turn,
                    "is_check": self.board.is_check(),
                    "is_checkmate": self.board.is_checkmate(),
                    "is_game_over": self.board.is_game_over(),
                }
            )

            return resp

        except (IllegalMoveError, InvalidMoveError):
            resp["illegalmove"] = True
            return resp

chessgame = ChessGame()