import { Chessboard } from 'react-chessboard';
import { useState, useEffect, useRef } from 'react';
import ModelSelectionModal from './ModelSelectionModal';

const API = 'http://localhost:8000';
const FREE_MODELS = [
    'qwen/qwen3-32b',
    'openai/gpt-oss-120b',
    'llama-3.3-70b-versatile',
    'llama-3.1-8b-instant',
];
interface GameState {
    fen: string;
    turn: boolean;
    is_check: boolean;
    is_checkmate: boolean;
    is_game_over: boolean;
    illegalmove?: boolean;
}

interface LastMove {
    piece: {
        isSparePiece: boolean;
        position: string;
        pieceType: string;
    };
    sourceSquare: string;
    targetSquare: string;
}

function AIvsAIChess() {
    const [isModalOpen, setIsModalOpen] = useState(true);
    const [whitePlayer, setWhitePlayer] = useState<string | null>(null);
    const [blackPlayer, setBlackPlayer] = useState<string | null>(null);
    const [fen, setFen] = useState<string>(
        'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
    );
    const [status, setStatus] = useState<GameState | null>(null);
    const [error, setError] = useState<string>('');
    const [isAutoPlaying, setIsAutoPlaying] = useState(false);
    const [lastMove, setLastMove] = useState<LastMove | null>(null);
    const [moveHistory, setMoveHistory] = useState<string[]>([]);
    const [moveDelay, setMoveDelay] = useState(1500);
    const isCallingAPI = useRef(false);

    // Fetch initial game state
    useEffect(() => {
        fetch(`${API}/game_state`)
            .then((res) => res.json())
            .then((data: GameState) => {
                setFen(data.fen);
                setStatus(data);
            });
    }, []);

    // AI vs AI auto-play loop
    useEffect(() => {
        if (
            !isAutoPlaying ||
            !status ||
            status.is_game_over ||
            isCallingAPI.current
        ) {
            return;
        }

        const timer = setTimeout(() => {
            makeAIMove();
        }, moveDelay);

        return () => clearTimeout(timer);
    }, [isAutoPlaying, status, lastMove]);

    const handleStartGame = (model1: string, model2: string) => {
        const players = [model1, model2];
        const white = players.splice(
            Math.floor(Math.random() * players.length),
            1
        )[0];
        const black = players[0];

        setWhitePlayer(white);
        setBlackPlayer(black);
        setIsModalOpen(false);
        startAutoPlay();
    };

    const makeAIMove = async () => {
        if (isCallingAPI.current) return;

        isCallingAPI.current = true;
        setError('');

        try {
            const res = await fetch(`${API}/ai_move`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    turn: status?.turn ?? true,
                    model: status?.turn ? whitePlayer : blackPlayer,
                }),
            });

            if (!res.ok) {
                throw new Error('API request failed');
            }

            const data: GameState = await res.json();

            if (data.illegalmove) {
                setError('AI made an illegal move. Stopping game.');
                setIsAutoPlaying(false);
                isCallingAPI.current = false;
                return;
            }

            console.log('Gamestate', data);

            // Update game state
            setFen(data.fen);
            setStatus(data);

            // Track move history
            const moveNotation = lastMove
                ? `${lastMove.sourceSquare}${lastMove.targetSquare}`
                : 'Starting move';
            setMoveHistory((prev) => [...prev, moveNotation]);

            // Store last move for next iteration
            // Note: We don't have the actual move from backend, so we track it differently
            // The backend handles the move internally

            if (data.is_game_over) {
                setIsAutoPlaying(false);
                if (data.is_checkmate) {
                    setError(
                        `Checkmate! ${data.turn ? 'Black' : 'White'} wins!`
                    );
                } else {
                    setError('Game Over!');
                }
            }
        } catch (err) {
            console.error('Error making AI move:', err);
            setError('Error making AI move. Stopping game.');
            setIsAutoPlaying(false);
        } finally {
            isCallingAPI.current = false;
        }
    };

    const startAutoPlay = () => {
        if (!whitePlayer || !blackPlayer) {
            setIsModalOpen(true);
            return;
        }
        setIsAutoPlaying(true);
        setError('');
    };

    const stopAutoPlay = () => {
        setIsAutoPlaying(false);
    };

    const resetGame = async () => {
        setIsAutoPlaying(false);
        setLastMove(null);
        setMoveHistory([]);
        setError('');

        // Fetch fresh game state to reset
        try {
            const res = await fetch(`${API}/reset`);
            const data: GameState = await res.json();
            setFen(data.fen);
            setStatus(data);
        } catch (err) {
            console.error('Error resetting game:', err);
        }
    };

    const chessBoardOptions = {
        position: fen,
        arePiecesDraggable: false, // Disable manual moves during AI vs AI
    };

    return (
        <>
            <ModelSelectionModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onStartGame={handleStartGame}
            />
            <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-4">
                <div className="max-w-6xl w-full">
                    <h1 className="text-4xl font-bold text-center mb-8 text-white">
                        🤖 AI vs AI Chess Battle
                    </h1>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Chessboard */}
                        {/* Player Info */}
                        <div className="bg-gray-800 rounded-xl p-6 shadow-xl col-span-1 lg:col-span-3 order-first lg:order-none">
                            <div className="flex justify-between items-center text-white">
                                <div className="text-center">
                                    <h3 className="text-lg font-bold">
                                        ⚪ White
                                    </h3>
                                    <p className="text-gray-400">
                                        {whitePlayer || 'N/A'}
                                    </p>
                                </div>
                                <div className="text-center">
                                    <h2 className="text-2xl font-bold">vs</h2>
                                </div>
                                <div className="text-center">
                                    <h3 className="text-lg font-bold">
                                        ⚫ Black
                                    </h3>
                                    <p className="text-gray-400">
                                        {blackPlayer || 'N/A'}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Chessboard */}
                        <div className="lg:col-span-2">
                            <div className="bg-gray-800 rounded-xl p-6 shadow-2xl">
                                <Chessboard options={chessBoardOptions} />
                            </div>
                        </div>

                        {/* Controls and Status */}
                        <div className="space-y-6">
                            {/* Controls */}
                            <div className="bg-gray-800 rounded-xl p-6 shadow-xl">
                                <h2 className="text-xl font-bold text-white mb-4">
                                    Controls
                                </h2>
                                <div className="space-y-3">
                                    <button
                                        onClick={startAutoPlay}
                                        disabled={
                                            isAutoPlaying ||
                                            status?.is_game_over
                                        }
                                        className="w-full px-4 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-semibold text-white transition shadow-lg"
                                    >
                                        {isAutoPlaying
                                            ? '▶️ Playing...'
                                            : '▶️ Start AI Battle'}
                                    </button>

                                    <button
                                        onClick={stopAutoPlay}
                                        disabled={!isAutoPlaying}
                                        className="w-full px-4 py-3 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-semibold text-white transition shadow-lg"
                                    >
                                        ⏸️ Pause
                                    </button>

                                    <button
                                        onClick={resetGame}
                                        className="w-full px-4 py-3 bg-red-600 hover:bg-red-700 rounded-lg font-semibold text-white transition shadow-lg"
                                    >
                                        🔄 Reset Game
                                    </button>

                                    <div className="pt-2">
                                        <label className="block text-white text-sm mb-2">
                                            Move Delay: {moveDelay}ms
                                        </label>
                                        <input
                                            type="range"
                                            min="500"
                                            max="5000"
                                            step="100"
                                            value={moveDelay}
                                            onChange={(e) =>
                                                setMoveDelay(
                                                    parseInt(e.target.value)
                                                )
                                            }
                                            className="w-full"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Game Status */}
                            <div className="bg-gray-800 rounded-xl p-6 shadow-xl">
                                <h2 className="text-xl font-bold text-white mb-4">
                                    Status
                                </h2>
                                <div className="space-y-3 text-white">
                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-400">
                                            Turn:
                                        </span>
                                        <span className="font-bold text-lg">
                                            {status?.turn
                                                ? '⚪ White'
                                                : '⚫ Black'}
                                        </span>
                                    </div>

                                    {status?.is_check && (
                                        <div className="p-3 bg-yellow-900 bg-opacity-50 border border-yellow-600 rounded-lg">
                                            <p className="text-yellow-300 font-semibold">
                                                ⚠️ Check!
                                            </p>
                                        </div>
                                    )}

                                    {status?.is_checkmate && (
                                        <div className="p-3 bg-red-900 bg-opacity-50 border border-red-600 rounded-lg">
                                            <p className="text-red-300 font-semibold">
                                                ♚ Checkmate!
                                            </p>
                                        </div>
                                    )}

                                    {status?.is_game_over && (
                                        <div className="p-3 bg-green-900 bg-opacity-50 border border-green-600 rounded-lg">
                                            <p className="text-green-300 font-semibold text-center">
                                                🎉 Game Over!
                                            </p>
                                            <p className="text-green-200 text-center text-sm mt-1">
                                                Winner:{' '}
                                                {status.turn
                                                    ? 'Black'
                                                    : 'White'}
                                            </p>
                                        </div>
                                    )}

                                    {error && (
                                        <div className="p-3 bg-red-900 bg-opacity-50 border border-red-600 rounded-lg">
                                            <p className="text-red-300 text-sm">
                                                {error}
                                            </p>
                                        </div>
                                    )}

                                    <div className="pt-2 border-t border-gray-700">
                                        <p className="text-gray-400 text-sm">
                                            Total Moves: {moveHistory.length}
                                        </p>
                                    </div>
                                </div>
                            </div>

                            {/* Move History */}
                            <div className="bg-gray-800 rounded-xl p-6 shadow-xl">
                                <h2 className="text-xl font-bold text-white mb-4">
                                    Move History
                                </h2>
                                <div className="max-h-64 overflow-y-auto space-y-2">
                                    {moveHistory.length === 0 ? (
                                        <p className="text-gray-500 text-center py-4">
                                            No moves yet
                                        </p>
                                    ) : (
                                        moveHistory.map((move, index) => (
                                            <div
                                                key={index}
                                                className="flex items-center gap-3 p-2 bg-gray-700 rounded-lg text-white text-sm"
                                            >
                                                <span className="font-bold text-gray-400 min-w-[2rem]">
                                                    {index + 1}.
                                                </span>
                                                <span
                                                    className={
                                                        index % 2 === 0
                                                            ? 'text-white'
                                                            : 'text-gray-300'
                                                    }
                                                >
                                                    {index % 2 === 0
                                                        ? '⚪'
                                                        : '⚫'}
                                                </span>
                                                <span className="text-blue-400">
                                                    {move}
                                                </span>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
}

export default AIvsAIChess;
