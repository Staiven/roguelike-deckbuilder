import { useGameStore } from '../store/gameStore';
import './Reward.css';

export function Reward() {
  const { skipReward, loading } = useGameStore();

  const handleSkip = () => {
    if (!loading) {
      skipReward();
    }
  };

  return (
    <div className="reward">
      <div className="reward__glow"></div>

      <div className="reward__content">
        <h1 className="reward__title">Victory!</h1>
        <p className="reward__subtitle">You have defeated your enemies</p>

        <div className="reward__rewards">
          <div className="reward__section">
            <h2 className="reward__section-title">Rewards</h2>
            <div className="reward__items">
              <div className="reward__item reward__item--gold">
                <span className="reward__item-icon">💰</span>
                <span className="reward__item-text">15-25 Gold</span>
              </div>
            </div>
          </div>
        </div>

        <button
          className="reward__skip"
          onClick={handleSkip}
          disabled={loading}
        >
          {loading ? 'Processing...' : 'Continue'}
        </button>
      </div>
    </div>
  );
}
