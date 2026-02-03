import { useGameStore } from '../store/gameStore';
import './CharacterSelect.css';

interface CharacterOption {
  id: 'warrior' | 'mage';
  name: string;
  hp: number;
  energy: number;
  description: string;
  icon: string;
}

const characters: CharacterOption[] = [
  {
    id: 'warrior',
    name: 'Warrior',
    hp: 80,
    energy: 3,
    description: 'Balanced fighter with strong attacks',
    icon: '⚔️',
  },
  {
    id: 'mage',
    name: 'Mage',
    hp: 60,
    energy: 3,
    description: 'Powerful spells but fragile',
    icon: '🔮',
  },
];

export function CharacterSelect() {
  const { startNewGame, loadGame, deleteSave, logout, loading, user } = useGameStore();

  const handleSelect = (characterId: 'warrior' | 'mage') => {
    if (!loading) {
      startNewGame(characterId);
    }
  };

  const handleContinue = () => {
    if (!loading) {
      loadGame();
    }
  };

  const handleDeleteSave = () => {
    if (!loading && confirm('Delete your saved game?')) {
      deleteSave();
    }
  };

  return (
    <div className="character-select">
      <div className="character-select__header">
        <span className="character-select__user">Playing as: {user.username}</span>
        <button className="character-select__logout" onClick={logout}>
          Logout
        </button>
      </div>

      <h1 className="character-select__title">
        {user.hasSave ? 'Continue or Start New?' : 'Choose Your Character'}
      </h1>

      {user.hasSave && (
        <div className="character-select__continue">
          <button
            className="continue-button"
            onClick={handleContinue}
            disabled={loading}
          >
            Continue Saved Game
          </button>
          <button
            className="delete-save-button"
            onClick={handleDeleteSave}
            disabled={loading}
          >
            Delete Save
          </button>
        </div>
      )}

      {user.hasSave && (
        <div className="character-select__divider">
          <span>or start a new game</span>
        </div>
      )}

      <div className="character-select__grid">
        {characters.map((char) => (
          <button
            key={char.id}
            className="character-card"
            onClick={() => handleSelect(char.id)}
            disabled={loading}
          >
            <div className="character-card__icon">{char.icon}</div>
            <h2 className="character-card__name">{char.name}</h2>
            <div className="character-card__stats">
              <div className="character-card__stat">
                <span className="stat-label">HP</span>
                <span className="stat-value stat-value--hp">{char.hp}</span>
              </div>
              <div className="character-card__stat">
                <span className="stat-label">Energy</span>
                <span className="stat-value stat-value--energy">{char.energy}</span>
              </div>
            </div>
            <p className="character-card__description">{char.description}</p>
          </button>
        ))}
      </div>
      {loading && <div className="character-select__loading">Loading...</div>}
    </div>
  );
}
