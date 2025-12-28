from pydantic import BaseModel
from typing import Optional



class Piece(BaseModel):
    isSparePiece: bool
    position: str
    pieceType: str

class move_type(BaseModel):
    piece: Piece
    sourceSquare: str
    targetSquare: str | None

class ai_move_type(BaseModel):
    turn: Optional[bool | None]
    model: Optional[str | None]
