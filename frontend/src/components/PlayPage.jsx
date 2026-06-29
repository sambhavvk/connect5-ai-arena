import { useState, useCallback } from 'react';
import Board from './Board';
import {
  createEmptyBoard,
  dropPiece,
  checkWinner,
  isGameOver,
  getValidMoves,
} from '../utils/game';

/**
 * PlayPage — full game loop.
 *
 * Currently plays human (Red, player 1) vs a simple random AI (Yellow, player 2).
 * Swap out the AI logic later when the backend is ready.
 */

/* ---- simple random AI (replace with API call later) ---- */
function randomAI(board) {
  const moves = getValidMoves(board);
  if (moves.length === 0) return null;
  return moves[Math.floor(Math.random() * moves.length)];
}

export default function PlayPage() {
  const [board, setBoard] = useState(createEmptyBoard);
  const [currentPlayer, setCurrentPlayer] = useState(1); // 1 = human, 2 = AI
  const [result, setResult] = useState(null); // null | { winner, cells }
  const [lastMove, setLastMove] = useState(null);
  const [aiThinking, setAiThinking] = useState(false);

  const gameOver = result !== null;

  /** Human makes a move. */
  const handleDrop = useCallback(
    (col) => {
      if (gameOver || aiThinking || currentPlayer !== 1) return;

      const newBoard = dropPiece(board, col, 1);
      if (!newBoard) return;

      const droppedRow = newBoard.findIndex((row) => row[col] === 1);
      setBoard(newBoard);
      setLastMove({ row: droppedRow, col });
      setCurrentPlayer(2);

      const winner = checkWinner(newBoard);
      if (winner) {
        setResult(winner);
        return;
      }

      // Trigger AI move after a short delay
      setAiThinking(true);
      setTimeout(() => {
        const aiCol = randomAI(newBoard);
        if (aiCol === null) {
          setAiThinking(false);
          return;
        }
        const afterAi = dropPiece(newBoard, aiCol, 2);
        if (!afterAi) {
          setAiThinking(false);
          return;
        }
        const aiRow = afterAi.findIndex((row) => row[aiCol] === 2);
        setBoard(afterAi);
        setLastMove({ row: aiRow, col: aiCol });
        setCurrentPlayer(1);
        setAiThinking(false);

        const aiWinner = checkWinner(afterAi);
        if (aiWinner) setResult(aiWinner);
      }, 400);
    },
    [board, currentPlayer, gameOver, aiThinking]
  );

  /** Reset the game. */
  const resetGame = () => {
    setBoard(createEmptyBoard());
    setCurrentPlayer(1);
    setResult(null);
    setLastMove(null);
    setAiThinking(false);
  };

  /* ---- derive status text ---- */
  let statusText;
  if (result) {
    if (result.winner === 0) statusText = "It's a draw!";
    else if (result.winner === 1) statusText = 'You win! 🎉';
    else statusText = 'AI wins! 🤖';
  } else if (aiThinking) {
    statusText = 'AI is thinking...';
  } else {
    statusText = 'Your turn — click a column to drop a piece';
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20 }}>
      <h1>Play</h1>

      {/* ---- Status bar ---- */}
      <div className="card" style={{ padding: '12px 24px', textAlign: 'center', minWidth: 280 }}>
        <span style={{ fontWeight: 600, fontSize: '1rem' }}>{statusText}</span>
        {aiThinking && (
          <span style={{ marginLeft: 8, display: 'inline-block' }} className="spinner" />
        )}
      </div>

      {/* ---- Board ---- */}
      <Board
        board={board}
        onDrop={handleDrop}
        disabled={gameOver || aiThinking || currentPlayer !== 1}
        winningCells={result?.cells || null}
        lastMove={lastMove}
      />

      {/* ---- Controls ---- */}
      <div style={{ display: 'flex', gap: 12 }}>
        <button className="btn-secondary" onClick={resetGame}>
          New Game
        </button>
      </div>

      {/* ---- Legend ---- */}
      <div style={{ display: 'flex', gap: 24, fontSize: '0.85rem', color: 'var(--text-muted)' }}>
        <span>
          <span
            style={{
              display: 'inline-block',
              width: 14,
              height: 14,
              borderRadius: '50%',
              background: 'var(--cell-p1)',
              verticalAlign: 'middle',
              marginRight: 6,
            }}
          />
          You (Red)
        </span>
        <span>
          <span
            style={{
              display: 'inline-block',
              width: 14,
              height: 14,
              borderRadius: '50%',
              background: 'var(--cell-p2)',
              verticalAlign: 'middle',
              marginRight: 6,
            }}
          />
          AI (Yellow)
        </span>
      </div>
    </div>
  );
}