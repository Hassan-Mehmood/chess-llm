from pydantic import BaseModel, Field
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


class ChessMove(BaseModel):
    """A chess move in UCI format."""

    move: str = Field(
        ...,
        description="The chess move in UCI format (e.g., 'e2e4', 'g1f3', 'e1g1', 'a7a8q')",
        examples=["e2e4", "g1f3", "e1g1", "a7a8q"],
    )
