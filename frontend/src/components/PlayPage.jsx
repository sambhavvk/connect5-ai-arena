import { useState, useEffect, useCallback } from 'react';
import Board from './Board';
import { startGame, makeMove, getAgents } from '../utils/api';
import { createEmptyBoard, checkWinner } from '../utils/game';

/**
 * PlayPage — full game loop talking to the FastAPI backend.
 *
 * Workflow:
 *   1. Pick an AI agent from the dropdown (fetched from GET /api/agents).
 *   2. Click "Start Game" → POST /api/game/start creates a game.
 *   3. Click a column → POST /api/game/move sends human move, backend runs AI,
 *      returns updated board + optional winner.
 */

export default function PlayPage() {
  /* ---- game state ---- */
  const [board, setBoard] = useState(createEmptyBoard);
  const [gameId, setGameId] = useState(null);
  const [result, setResult] = useState(null); // null | { winner, cells }
  const [lastMove, setLastMove] = useState(null);
  const [thinking, setThinking] = useState(false);
  const [error, setError] = useState(null);

  /* ---- agent list ---- */
  const [agents, setAgents] = useState({});
  const [selectedAgent, setSelectedAgent] = useState('minimax');

  useEffect(() => {
    getAgents()
      .then((list) => {
        // list is { minimax: true, mcts_pure: true, ... } or just an array of names
        if (Array.isArray(list)) {
          const obj = {};
          list.forEach((name) => (obj[name] = true));
          setAgents(obj);
        } else {
          setAgents(list);
        }
      })
      .catch(() => {
        // Backend might not be running — that's okay
        setAgents({ minimax: true, mcts_pure: true, mcts_nn: true });
      });
  }, []);

  const agentNames = Object.keys(agents).filter((k) => agents[k] !== false && agents[k] !== null);

  /* ---- start a new game ---- */
  const handleStart = useCallback(async () => {
    setError(null);
    setThinking(true);
    try {
      const data = await startGame(selectedAgent);
      setGameId(data.game_id);
      setBoard(data.board);
      setResult(null);
      setLastMove(null);
      // current_player is 0 = human, so the human can click
    } catch (err) {
      setError(err.message);
    } finally {
      setThinking(false);
    }
  }, [selectedAgent]);

  /* ---- human clicks a column ---- */
  const handleDrop = useCallback(
    async (col) => {
      if (!gameId || result || thinking) return;

      setError(null);
      setThinking(true);
      try {
        const data = await makeMove(gameId, col);

        // Find where the human piece landed (column `col`, first occupied cell from bottom)
        const newBoard = data.board;
        let droppedRow = -1;
        for (let r = newBoard.length - 1; r >= 0; r--) {
          if (newBoard[r][col] !== 0) {
            droppedRow = r;
            break;
          }
        }
        setBoard(newBoard);
        setLastMove({ row: droppedRow, col });
        setThinking(false);

        // ---- result handling ----
        if (data.winner === 0) {
          // Human won
          const win = checkWinner(newBoard);
          setResult(win);
          setGameId(null);
          return;
        }

        if (data.winner === 1) {
          // AI won — board already includes AI's winning move
          const win = checkWinner(newBoard);
          setResult(win);
          setGameId(null);
          return;
        }

        if (data.winner === null) {
          // Draw
          setResult({ winner: 0 });
          setGameId(null);
          return;
        }

        // Game continues — highlight AI's move
        if (data.ai_move_column != null) {
          const aiCol = data.ai_move_column;
          let aiRow = -1;
          for (let r = newBoard.length - 1; r >= 0; r--) {
            if (newBoard[r][aiCol] !== 0 && newBoard[r][aiCol] === 2) {
              aiRow = r;
              break;
            }
          }
          setLastMove({ row: aiRow, col: aiCol });
        }
      } catch (err) {
        setError(err.message);
        setThinking(false);
      }
    },
    [gameId, result, thinking]
  );

  /* ---- derived status text ---- */
  let statusText;
  if (error) {
    statusText = `Error: ${error}`;
  } else if (result) {
    if (result.winner === 0) statusText = "It's a draw!";
    else if (result.winner === 1) statusText = 'You win! 🎉';
    else if (result.winner === 2) statusText = 'AI wins! 🤖';
  } else if (thinking) {
    statusText = 'Thinking...';
  } else if (!gameId) {
    statusText = 'Choose an opponent and start a new game';
  } else {
    statusText = 'Your turn — click a column to drop a piece';
  }

  const canPlay = gameId && !result && !thinking;
  const gameOver = result !== null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20 }}>
      <h1>Play</h1>

      {/* ---- Agent selector ---- */}
      <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap', justifyContent: 'center' }}>
        <label style={{ fontWeight: 500, fontSize: '0.9rem' }}>
          Opponent:
          <select
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value)}
            style={{
              marginLeft: 8,
              padding: '6px 10px',
              borderRadius: 'var(--radius)',
              border: '1px solid var(--border)',
              background: 'var(--surface)',
              color: 'var(--text-h)',
              fontSize: '0.875rem',
              fontFamily: 'var(--sans)',
            }}
          >
            {agentNames.length === 0 && <option value="minimax">minimax</option>}
            {agentNames.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </label>

        <button className="btn-primary" onClick={handleStart} disabled={thinking}>
          {gameId ? 'Restart' : 'Start Game'}
        </button>
      </div>

      {/* ---- Status bar ---- */}
      <div
        className="card"
        style={{
          padding: '12px 24px',
          textAlign: 'center',
          minWidth: 280,
          borderColor: error ? 'var(--danger)' : undefined,
        }}
      >
        <span style={{ fontWeight: 600, fontSize: '1rem', color: error ? 'var(--danger)' : undefined }}>
          {statusText}
        </span>
        {thinking && <span className="spinner" style={{ marginLeft: 8 }} />}
      </div>

      {/* ---- Board ---- */}
      <Board
        board={board}
        onDrop={handleDrop}
        disabled={!canPlay}
        winningCells={result?.cells || null}
        lastMove={lastMove}
      />

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