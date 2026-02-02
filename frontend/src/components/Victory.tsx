import { useGameStore } from '../store/gameStore';
import './Victory.css';

export function Victory() {
  const { gameState } = useGameStore();

  const handlePlayAgain = () => {
    window.location.reload();
  };

  if (!gameState) return null;

  const { floor, act, player } = gameState;
  const enemiesKilled = Math.max(0, (floor - 1) * 2 + 1); // Including boss

  return (
    <div className="victory">
      <div className="victory__particles">
        {Array.from({ length: 20 }).map((_, i) => (
          <div key={i} className="victory__particle" style={{
            left: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 2}s`,
            animationDuration: `${2 + Math.random() * 2}s`,
          }} />
        ))}
      </div>

      <div className="victory__content">
        <div className="victory__crown">👑</div>
        <h1 className="victory__title">Victory!</h1>
        <p className="victory__subtitle">You have conquered the spire!</p>

        <div className="victory__stats">
          <h2 className="victory__stats-title">Run Complete</h2>

          <div className="victory__stat-grid">
            <div className="victory__stat">
              <span className="victory__stat-value">{act}</span>
              <span className="victory__stat-label">Acts Completed</span>
            </div>

            <div className="victory__stat">
              <span className="victory__stat-value">{floor}</span>
              <span className="victory__stat-label">Floors Cleared</span>
            </div>

            <div className="victory__stat">
              <span className="victory__stat-value">{enemiesKilled}</span>
              <span className="victory__stat-label">Enemies Defeated</span>
            </div>

            <div className="victory__stat">
              <span className="victory__stat-value">{player.gold}</span>
              <span className="victory__stat-label">Gold Collected</span>
            </div>

            <div className="victory__stat">
              <span className="victory__stat-value">{player.currentHp}/{player.maxHp}</span>
              <span className="victory__stat-label">Final HP</span>
            </div>
          </div>
        </div>

        <button
          className="victory__play-again"
          onClick={handlePlayAgain}
        >
          Play Again
        </button>
      </div>
    </div>
  );
}
