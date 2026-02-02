import { useGameStore } from '../store/gameStore';
import './GameOver.css';

export function GameOver() {
  const { gameState } = useGameStore();

  const handleTryAgain = () => {
    // Reset to main menu by reloading the page
    // In a more sophisticated implementation, we'd have a resetGame action
    window.location.reload();
  };

  if (!gameState) return null;

  const { floor } = gameState;
  // For demo purposes, we'll calculate enemies killed based on floor
  const enemiesKilled = Math.max(0, (floor - 1) * 2);

  return (
    <div className="game-over">
      <div className="game-over__overlay"></div>

      <div className="game-over__content">
        <h1 className="game-over__title">Defeat</h1>
        <p className="game-over__subtitle">Your journey has come to an end...</p>

        <div className="game-over__stats">
          <h2 className="game-over__stats-title">Run Statistics</h2>

          <div className="game-over__stat-grid">
            <div className="game-over__stat">
              <span className="game-over__stat-value">{floor}</span>
              <span className="game-over__stat-label">Floor Reached</span>
            </div>

            <div className="game-over__stat">
              <span className="game-over__stat-value">{enemiesKilled}</span>
              <span className="game-over__stat-label">Enemies Defeated</span>
            </div>

            <div className="game-over__stat">
              <span className="game-over__stat-value">{gameState.player.gold}</span>
              <span className="game-over__stat-label">Gold Collected</span>
            </div>
          </div>
        </div>

        <button
          className="game-over__retry"
          onClick={handleTryAgain}
        >
          Try Again
        </button>
      </div>
    </div>
  );
}
