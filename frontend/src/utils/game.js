/**
 * Connect5 game helpers.
 * Board: 9 rows × 10 columns, 5-in-a-row to win.
 * board[row][col] = 0 (empty), 1 (player 1), 2 (player 2)
 */

export const ROWS = 9;
export const COLS = 10;
export const WIN_LENGTH = 5;

/** Create an empty board (all zeros). */
export function createEmptyBoard() {
  return Array.from({ length: ROWS }, () => Array(COLS).fill(0));
}

/**
 * Drop a piece into a column. Returns a new board (immutable).
 * Returns null if the column is full.
 */
export function dropPiece(board, col, player) {
  if (col < 0 || col >= COLS) return null;
  for (let row = ROWS - 1; row >= 0; row--) {
    if (board[row][col] === 0) {
      const newBoard = board.map((r) => [...r]);
      newBoard[row][col] = player;
      return newBoard;
    }
  }
  return null; // column full
}

/** Check if a column can accept a piece. */
export function isValidMove(board, col) {
  if (col < 0 || col >= COLS) return false;
  return board[0][col] === 0;
}

/** Get list of valid column indices. */
export function getValidMoves(board) {
  const moves = [];
  for (let c = 0; c < COLS; c++) {
    if (isValidMove(board, c)) moves.push(c);
  }
  return moves;
}

/**
 * Check for a winner. Returns:
 *   { winner: 1|2, cells: [[r,c], ...] } if won,
 *   null if no winner,
 *   { winner: 0 } if draw (board full, no winner).
 */
export function checkWinner(board) {
  const directions = [
    [0, 1],   // horizontal
    [1, 0],   // vertical
    [1, 1],   // diagonal down-right
    [1, -1],  // diagonal down-left
  ];

  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const player = board[r][c];
      if (player === 0) continue;

      for (const [dr, dc] of directions) {
        const cells = [[r, c]];
        for (let k = 1; k < WIN_LENGTH; k++) {
          const nr = r + dr * k;
          const nc = c + dc * k;
          if (nr < 0 || nr >= ROWS || nc < 0 || nc >= COLS) break;
          if (board[nr][nc] !== player) break;
          cells.push([nr, nc]);
        }
        if (cells.length === WIN_LENGTH) {
          return { winner: player, cells };
        }
      }
    }
  }

  // Check for draw
  if (getValidMoves(board).length === 0) {
    return { winner: 0 };
  }

  return null;
}

/** Check if the game is over (win or draw). */
export function isGameOver(board) {
  return checkWinner(board) !== null;
}