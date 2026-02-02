import { useGameStore } from './store/gameStore';
import { CharacterSelect } from './components/CharacterSelect';
import { MapView } from './components/MapView';
import { CombatScene } from './components/CombatScene';
import { RestSite } from './components/RestSite';
import { Reward } from './components/Reward';
import { GameOver } from './components/GameOver';
import { Victory } from './components/Victory';
import './styles/app.css';

function App() {
  const { gameState, loading, error, setError } = useGameStore();

  const renderScreen = () => {
    // If no game state, show character select (main menu)
    if (!gameState) {
      return <CharacterSelect />;
    }

    // Render based on game state
    switch (gameState.state) {
      case 'main_menu':
        return <CharacterSelect />;
      case 'map':
        return (
          <MapView
            map={gameState.map}
            currentRow={gameState.map.currentRow}
            currentCol={gameState.map.currentCol}
          />
        );
      case 'combat':
        return <CombatScene />;
      case 'rest':
        return <RestSite />;
      case 'reward':
        return <Reward />;
      case 'game_over':
        return <GameOver />;
      case 'victory':
        return <Victory />;
      case 'event':
      case 'shop':
        // Placeholder for future screens
        return (
          <div className="placeholder-screen">
            <h2>Coming Soon: {gameState.state}</h2>
            <button onClick={() => useGameStore.getState().skipReward()}>
              Continue
            </button>
          </div>
        );
      default:
        return <CharacterSelect />;
    }
  };

  return (
    <div className="app">
      {/* Main content */}
      {renderScreen()}

      {/* Loading overlay */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
        </div>
      )}

      {/* Error display */}
      {error && (
        <div className="error-toast">
          <span className="error-toast__message">{error}</span>
          <button
            className="error-toast__close"
            onClick={() => setError(null)}
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Game info bar */}
      {gameState && gameState.state !== 'main_menu' && (
        <div className="game-info-bar">
          <div className="game-info-bar__item">
            <span className="game-info-bar__label">HP</span>
            <span className="game-info-bar__value game-info-bar__value--hp">
              {gameState.player.currentHp}/{gameState.player.maxHp}
            </span>
          </div>
          <div className="game-info-bar__item">
            <span className="game-info-bar__label">Gold</span>
            <span className="game-info-bar__value game-info-bar__value--gold">
              {gameState.player.gold}
            </span>
          </div>
          <div className="game-info-bar__item">
            <span className="game-info-bar__label">Floor</span>
            <span className="game-info-bar__value">
              {gameState.floor}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
