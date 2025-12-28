import { useState } from 'react';

const FREE_MODELS = [
    'qwen/qwen3-32b',
    'openai/gpt-oss-120b',
    'llama-3.3-70b-versatile',
    'llama-3.1-8b-instant',
    'groq/compound',
    'OPENAI/gpt-5.2',
    'OPENAI/gpt-5.2-pro',
    'OPENAI/gpt-5.1',
    'OPENAI/gpt-5',
    'OPENAI/gpt-5-mini',
    'OPENAI/gpt-5-nano',
    'OPENAI/gpt-5-pro',
    'OPENAI/gpt-4.1',
    'OPENAI/gpt-4.1-mini',
    'OPENAI/gpt-4.1-nano',
    'OPENAI/gpt-4o',
    'OPENAI/gpt-4o-mini',
    'claude-sonnet-4-5',
    'claude-haiku-4-5',
    'claude-opus-4-5',
    'claude-opus-4-1',
    'claude-sonnet-4-0',
    'claude-3-7-sonnet-latest',
    'claude-opus-4-0',
    'claude-3-haiku-20240307',
    'gemini-3-pro-preview',
    'gemini-3-flash-preview',
    'gemini-2.5-flash',
    'gemini-2.5-flash-lite',
    'gemini-2.5-pro',
    'gemini-2.0-flash',
    'gemini-2.0-flash-lite',
    
];

interface Props {
    isOpen: boolean;
    onClose: () => void;
    onStartGame: (model1: string, model2: string) => void;
}

const ModelSelectionModal = ({ isOpen, onClose, onStartGame }: Props) => {
    const [model1, setModel1] = useState(FREE_MODELS[0]);
    const [model2, setModel2] = useState(FREE_MODELS[1]);

    const handleStartGame = () => {
        onStartGame(model1, model2);
        onClose();
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-gray-800 rounded-lg p-8 shadow-2xl w-full max-w-md">
                <h2 className="text-2xl font-bold text-white mb-6">
                    Select AI Models
                </h2>

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                            Model 1
                        </label>
                        <select
                            value={model1}
                            onChange={(e) => setModel1(e.target.value)}
                            className="w-full p-3 bg-gray-700 text-white rounded-lg border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                        >
                            {FREE_MODELS.map((model) => (
                                <option key={model} value={model}>
                                    {model}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                            Model 2
                        </label>
                        <select
                            value={model2}
                            onChange={(e) => setModel2(e.target.value)}
                            className="w-full p-3 bg-gray-700 text-white rounded-lg border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                        >
                            {FREE_MODELS.map((model) => (
                                <option key={model} value={model}>
                                    {model}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                <div className="mt-8 flex justify-end space-x-4">
                    <button
                        onClick={onClose}
                        className="px-6 py-2 rounded-lg bg-gray-600 hover:bg-gray-700 text-white font-semibold transition"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleStartGame}
                        className="px-6 py-2 rounded-lg bg-green-600 hover:bg-green-700 text-white font-semibold transition shadow-lg"
                    >
                        Start Game
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ModelSelectionModal;
