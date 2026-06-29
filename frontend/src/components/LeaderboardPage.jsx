import { useState, useEffect } from 'react';
import { getLeaderboard } from '../utils/api';

/**
 * LeaderboardPage — fetches Elo rankings from GET /api/leaderboard.
 */
export default function LeaderboardPage() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getLeaderboard()
      .then(setEntries)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 24 }}>
      <h1>Leaderboard</h1>

      {loading && (
        <span className="text-muted">
          <span className="spinner" style={{ marginRight: 8 }} />
          Loading rankings...
        </span>
      )}

      {error && (
        <div className="card" style={{ borderColor: 'var(--danger)', maxWidth: 400, textAlign: 'center' }}>
          <p style={{ color: 'var(--danger)', margin: 0 }}>
            Could not load leaderboard: {error}
          </p>
        </div>
      )}

      {!loading && !error && entries.length === 0 && (
        <p className="text-muted">No rankings yet.</p>
      )}

      {!loading && !error && entries.length > 0 && (
        <div style={{ width: '100%', maxWidth: 480 }}>
          <table
            style={{
              width: '100%',
              borderCollapse: 'collapse',
              background: 'var(--surface)',
              borderRadius: 'var(--radius-lg)',
              overflow: 'hidden',
              boxShadow: 'var(--shadow-sm)',
            }}
          >
            <thead>
              <tr style={{ background: 'var(--accent-bg)' }}>
                <th style={thStyle}>#</th>
                <th style={{ ...thStyle, textAlign: 'left' }}>Player</th>
                <th style={{ ...thStyle, textAlign: 'right' }}>Elo</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry, i) => (
                <tr
                  key={entry.player || i}
                  style={{ borderBottom: '1px solid var(--border)' }}
                >
                  <td style={tdStyle}>{i + 1}</td>
                  <td style={{ ...tdStyle, fontWeight: 500, textAlign: 'left' }}>
                    {entry.player}
                  </td>
                  <td style={{ ...tdStyle, textAlign: 'right', fontFamily: 'var(--mono)' }}>
                    {entry.elo}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p className="text-muted" style={{ fontSize: '0.8rem' }}>
        Elo ratings update after each match.
      </p>
    </div>
  );
}

const thStyle = {
  padding: '10px 16px',
  fontSize: '0.8rem',
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  color: 'var(--text-muted)',
};

const tdStyle = {
  padding: '12px 16px',
  fontSize: '0.9rem',
  color: 'var(--text-h)',
  textAlign: 'center',
};