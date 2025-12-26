import './App.css';
import { useState } from 'react';
import GameBoard from './components/gameBoard';

function App() {
    const [gameStart, setGameStart] = useState(false);

    return (
        <main>
            {gameStart === false ? (
                <div>
                    <h1>Chess</h1>
                    <button onClick={() => setGameStart(true)}>Start</button>
                </div>
            ) : (
                <GameBoard />
            )}
        </main>
    );
}

export default App;
