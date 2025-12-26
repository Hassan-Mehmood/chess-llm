import { Chessboard } from 'react-chessboard';
import type { PieceDropHandlerArgs } from 'react-chessboard';

import { useState, useEffect } from 'react';

const API = 'http://localhost:8000';

function GameBoard() {
    const [fen, setFen] = useState();
    const [status, setStatus] = useState(null);

    useEffect(() => {
        fetch(`${API}/game_state`)
            .then((res) => res.json())
            .then((data) => {
                console.log(data);
                setFen(data.fen);
                setStatus(data);
            });
    }, []);

    async function onDrop(drop: PieceDropHandlerArgs) {
        console.log('drop', drop);

        const res = await fetch(`${API}/move`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                piece: drop.piece,
                sourceSquare: drop.sourceSquare,
                targetSquare: drop.targetSquare,
            }),
        });

        const data = await res.json();

        if (!data.success) return false;

        console.log(data);

        setFen(data.fen);
        setStatus(data);
        return true;
    }

    const chessBoardOptions = {
        position: fen, // we'll be getting this from the backend.
        onPieceDrop: onDrop,
    };

    return (
        <div>
            <Chessboard options={chessBoardOptions} />
            {status?.is_check && <p>⚠️ Check</p>}
            {status?.is_checkmate && <p>♚ Checkmate</p>}
        </div>
    );
}

export default GameBoard;
