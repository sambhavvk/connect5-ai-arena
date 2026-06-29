/**
 * LeaderboardPage — placeholder.
 * Will display Elo rankings from the backend.
 */
export default function LeaderboardPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 24 }}>
      <h1>Leaderboard</h1>

      <div className="card" style={{ width: '100%', maxWidth: 500, textAlign: 'center' }}>
        <p className="text-muted">
          Leaderboard coming soon — rankings will appear here once the backend is connected.
        </p>
      </div>
    </div>
  );
}