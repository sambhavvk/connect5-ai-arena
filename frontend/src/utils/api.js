/**
 * API client for Connect5 AI Arena backend.
 *
 * In dev mode, Vite proxies /api -> http://localhost:8000 (see vite.config.js).
 * In production, the frontend is served from the same origin as the backend,
 * or you override BASE with an env variable.
 */

const BASE = import.meta.env.VITE_API_BASE || '/api';

async function request(path, options = {}) {
  const url = `${BASE}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

/* ---- Game ---- */

/** POST /api/game/start?agent_type=... */
export function startGame(agentType = 'minimax') {
  return request(`/game/start?agent_type=${encodeURIComponent(agentType)}`, {
    method: 'POST',
  });
}

/** POST /api/game/move?game_id=...  body: { column } */
export function makeMove(gameId, column) {
  return request(`/game/move?game_id=${encodeURIComponent(gameId)}`, {
    method: 'POST',
    body: JSON.stringify({ column }),
  });
}

/* ---- Agents ---- */

/** GET /api/agents */
export function getAgents() {
  return request('/agents');
}

/* ---- Leaderboard ---- */

/** GET /api/leaderboard */
export function getLeaderboard() {
  return request('/leaderboard');
}

/* ---- Replays ---- */

/** GET /api/replay/{episodeId} */
export function getReplay(episodeId) {
  return request(`/replay/${encodeURIComponent(episodeId)}`);
}