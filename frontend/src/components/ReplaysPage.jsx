/**
 * ReplaysPage — placeholder.
 * Will fetch and step through past game replays from the backend.
 */
export default function ReplaysPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 24 }}>
      <h1>Replays</h1>

      <div className="card" style={{ width: '100%', maxWidth: 500, textAlign: 'center' }}>
        <p className="text-muted">
          Game replays coming soon — browse and step through past matches once the backend is connected.
        </p>
      </div>
    </div>
  );
}