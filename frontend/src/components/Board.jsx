import { useMemo } from 'react';
import { COLS, ROWS, isValidMove } from '../utils/game';
import './Board.css';

/* ---------- layout constants (easy to tweak) ---------- */
const CELL = 48;          // cell diameter
const PAD = 20;           // padding around grid
const RADIUS = CELL / 2 - 4;  // piece radius
const W = PAD * 2 + COLS * CELL;
const H = PAD * 2 + ROWS * CELL;

/**
 * SVG-based Connect5 board.
 *
 * Props:
 *   board      – 2D array board[row][col] (0 empty, 1 / 2 players)
 *   onDrop     – (col: number) => void   called when player clicks a column
 *   disabled   – if true, clicks are ignored
 *   winningCells – Set of "row,col" strings to highlight
 *   lastMove   – { row, col } | null    piece to animate
 */
export default function Board({
  board,
  onDrop,
  disabled = false,
  winningCells = null,
  lastMove = null,
}) {
  /* build a Set for O(1) lookup */
  const winSet = useMemo(() => {
    if (!winningCells) return new Set();
    if (winningCells instanceof Set) return winningCells;
    return new Set(winningCells.map(([r, c]) => `${r},${c}`));
  }, [winningCells]);

  const lastKey = lastMove ? `${lastMove.row},${lastMove.col}` : null;

  return (
    <div className="board-wrapper">
      <svg
        className="board-svg"
        viewBox={`0 0 ${W} ${H}`}
        width={W}
        height={H}
        aria-label="Connect5 game board"
      >
        {/* ---- board background ---- */}
        <rect x={0} y={0} width={W} height={H} rx={12} fill="var(--board-bg)" />

        {/* ---- grid cells (empty holes) ---- */}
        {Array.from({ length: ROWS }, (_, row) =>
          Array.from({ length: COLS }, (_, col) => {
            const cx = PAD + col * CELL + CELL / 2;
            const cy = PAD + row * CELL + CELL / 2;
            return (
              <circle
                key={`hole-${row}-${col}`}
                cx={cx}
                cy={cy}
                r={RADIUS}
                fill="var(--board-grid)"
              />
            );
          })
        )}

        {/* ---- pieces ---- */}
        {Array.from({ length: ROWS }, (_, row) =>
          Array.from({ length: COLS }, (_, col) => {
            const player = board[row][col];
            if (player === 0) return null;

            const cx = PAD + col * CELL + CELL / 2;
            const cy = PAD + row * CELL + CELL / 2;
            const key = `${row},${col}`;
            const isWinning = winSet.has(key);
            const isLast = key === lastKey;

            const fill = player === 1 ? 'var(--cell-p1)' : 'var(--cell-p2)';
            const stroke = player === 1 ? 'var(--cell-p1-ring)' : 'var(--cell-p2-ring)';

            return (
              <g key={`piece-${key}`} className={`piece ${isLast ? 'dropping' : ''}`}>
                {/* outer ring */}
                <circle
                  cx={cx}
                  cy={cy}
                  r={RADIUS}
                  fill={fill}
                  stroke={stroke}
                  strokeWidth={2}
                  className={isWinning ? 'win-cell' : ''}
                />
                {/* inner highlight */}
                <circle
                  cx={cx - 2}
                  cy={cy - 2}
                  r={RADIUS * 0.45}
                  fill="rgba(255,255,255,0.25)"
                />
              </g>
            );
          })
        )}

        {/* ---- column click targets (invisible hover zones) ---- */}
        {Array.from({ length: COLS }, (_, col) => {
          const canDrop = !disabled && isValidMove(board, col);
          return (
            <rect
              key={`hover-${col}`}
              x={PAD + col * CELL}
              y={0}
              width={CELL}
              height={H}
              className={`col-hover-zone ${!canDrop ? 'disabled' : ''}`}
              onClick={() => canDrop && onDrop(col)}
            />
          );
        })}
      </svg>
    </div>
  );
}