import { useState } from 'react';
import Board from './Board';
import { getReplay } from '../utils/api';

/**
 * ReplaysPage — fetch a game replay by episode ID and step through moves.
 * Backend endpoint: GET /api/replay/{episode_id}
 */
export default function ReplaysPage() {
  const [episodeId, setEpisodeId] = useState('');
  const [replay, setReplay] = useState(null);   // { steps: [{board, move, player}] }
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLoad = async () => {
    if (!episodeId.trim()) return;
    setError(null);
    setLoading(true);
    setReplay(null);
    setStep(0);
    try {
      const data = await getReplay(episodeId.trim());
      setReplay(data);
      setStep(0);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Support different replay data shapes:
  // - { steps: [{board, action, player}, ...] }
  // - { moves: [[row,col,player], ...], board_history: [...] }
  const steps = replay?.steps || replay?.moves || replay?.history || [];
  const boardList = replay?.board_history || replay?.boards || null;

  // current board at the given step
  let currentBoard = null;
  let currentInfo = null;
  if (steps.length > 0 && step < steps.length) {
    const s = steps[step];
    // If the step has a board, use it; otherwise look in board_history
    currentBoard = s.board;
    if (!currentBoard && boardList && step < boardList.length) {
      currentBoard = boardList[step];
    }
    currentInfo = s;
  }

  const canPrev = step > 0;
  const canNext = steps.length > 0 && step < steps.length - 1;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20 }}>
      <h1>Replays</h1>

      {/* ---- Episode ID input ---- */}
      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
        <input
          type="text"
          placeholder="Episode ID"
          value={episodeId}
          onChange={(e) => setEpisodeId(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleLoad()}
          style={{
            padding: '8px 12px',
            borderRadius: 'var(--radius)',
            border: '1px solid var(--border)',
            background: 'var(--surface)',
            color: 'var(--text-h)',
            fontSize: '0.875rem',
            fontFamily: 'var(--sans)',
            width: 220,
          }}
        />
        <button className="btn-primary" onClick={handleLoad} disabled={loading || !episodeId.trim()}>
          {loading ? 'Loading...' : 'Load'}
        </button>
      </div>

      {/* ---- Error ---- */}
      {error && (
        <div className="card" style={{ borderColor: 'var(--danger)', maxWidth: 400, textAlign: 'center' }}>
          <p style={{ color: 'var(--danger)', margin: 0 }}>{error}</p>
        </div>
      )}

      {/* ---- Replay viewer ---- */}
      {replay && (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
          {/* Step counter */}
          <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <button className="btn-secondary" onClick={() => setStep((s) => s - 1)} disabled={!canPrev}>
              ◀ Prev
            </button>
            <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>
              Move {step + 1} / {steps.length}
            </span>
            <button className="btn-secondary" onClick={() => setStep((s) => s + 1)} disabled={!canNext}>
              Next ▶
            </button>
          </div>

          {/* Move info */}
          {currentInfo && (
            <p className="text-muted" style={{ fontSize: '0.85rem', margin: 0 }}>
              Player {currentInfo.player ?? '?'}
              {currentInfo.action != null && ` → column ${currentInfo.action}`}
              {currentInfo.move != null && ` → ${JSON.stringify(currentInfo.move)}`}
            </p>
          )}

          {/* Board */}
          {currentBoard && (
            <Board board={currentBoard} onDrop={() => {}} disabled />
          )}
        </div>
      )}

      {/* ---- Empty state ---- */}
      {!replay && !loading && !error && (
        <div className="card" style={{ maxWidth: 450, textAlign: 'center' }}>
          <p className="text-muted">
            Enter an episode ID to view a replay. Episode IDs come from past games
            stored in the database.
          </p>
        </div>
      )}
    </div>
  );
}