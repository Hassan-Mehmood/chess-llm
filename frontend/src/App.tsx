import './App.css';
import { useState } from 'react';
import GameBoard from './components/gameBoard';
import { Button } from '@/components/ui/button';

function App() {
    const [gameStart, setGameStart] = useState(false);

    return (
        <main className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 min-h-screen">
            {gameStart === false ? (
                <div className="flex justify-center items-center h-screen">
                    <Button
                        variant="outline"
                        size="lg"
                        className="font-bold py-4 px-8 text-lg hover:bg-gray-100 transition-colors duration-200 rounded-lg"
                        onClick={() => setGameStart(true)}
                    >
                        Start Game
                    </Button>
                </div>
            ) : (
                <GameBoard />
            )}
        </main>
    );
}

export default App;
