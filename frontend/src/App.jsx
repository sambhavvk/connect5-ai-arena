import { useState } from 'react';
import PlayPage from './components/PlayPage';
import LeaderboardPage from './components/LeaderboardPage';
import ReplaysPage from './components/ReplaysPage';
import './App.css';

const PAGES = {
  play: { label: 'Play', component: PlayPage },
  leaderboard: { label: 'Leaderboard', component: LeaderboardPage },
  replays: { label: 'Replays', component: ReplaysPage },
};

function App() {
  const [page, setPage] = useState('play');

  const PageComponent = PAGES[page].component;

  return (
    <div className="app-shell">
      {/* ----- Nav bar ----- */}
      <nav className="navbar">
        <div className="container navbar-inner">
          <span className="navbar-brand">Connect5 AI Arena</span>
          <div className="navbar-links">
            {Object.entries(PAGES).map(([key, { label }]) => (
              <button
                key={key}
                className={`nav-link ${page === key ? 'active' : ''}`}
                onClick={() => setPage(key)}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* ----- Page content ----- */}
      <main className="main-content container">
        <PageComponent />
      </main>
    </div>
  );
}

export default App;