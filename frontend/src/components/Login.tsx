import { useState } from 'react';
import { useGameStore } from '../store/gameStore';
import './Login.css';

export function Login() {
  const [username, setUsername] = useState('');
  const { login, loading, error } = useGameStore();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (username.trim()) {
      login(username.trim());
    }
  };

  return (
    <div className="login">
      <h1 className="login__title">Roguelike Deckbuilder</h1>
      <form className="login__form" onSubmit={handleSubmit}>
        <label className="login__label" htmlFor="username">
          Enter your name to play
        </label>
        <input
          id="username"
          className="login__input"
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Your name"
          maxLength={50}
          disabled={loading}
          autoFocus
        />
        <button
          className="login__button"
          type="submit"
          disabled={!username.trim() || loading}
        >
          {loading ? 'Loading...' : 'Play'}
        </button>
      </form>
      {error && <div className="login__error">{error}</div>}
    </div>
  );
}
