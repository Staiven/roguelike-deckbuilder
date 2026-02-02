# Roguelike Deck-Builder Game

A Python roguelike deck-building game inspired by Slay the Spire and Vault of the Void.

## Features

- **Deck Building**: Build and customize your deck as you progress
- **Turn-based Combat**: Strategic combat with energy management
- **Procedural Maps**: Branching paths with different encounter types
- **Status Effects**: Buffs and debuffs that affect combat
- **Multiple Characters**: Different starting decks and relics
- **Relics**: Passive items that provide powerful bonuses

## Project Structure

```
rogue_project/
├── src/
│   ├── core/           # Enums, effects, events
│   ├── entities/       # Card, Player, Enemy, Relic
│   ├── combat/         # Combat manager, energy, status effects
│   ├── deck/           # Deck management
│   ├── map/            # Map generation
│   ├── data/           # Card, enemy, relic definitions
│   └── characters/     # Character classes
├── tests/              # Unit tests
└── requirements.txt
```

## Installation

```bash
pip install -r requirements.txt
```

## Running the Game

```bash
python -m src.main
```

## Running Tests

```bash
pytest tests/ -v
```

## Core Mechanics

### Cards
- **Attack**: Deal damage to enemies
- **Skill**: Gain block, draw cards, apply effects
- **Power**: Permanent effects that last the combat

### Combat
- Each turn you have 3 energy to spend
- Draw 5 cards at the start of each turn
- Play cards to damage enemies or defend yourself
- End your turn to let enemies act

### Status Effects
- **Strength**: +damage per attack
- **Dexterity**: +block per skill
- **Vulnerable**: Take 50% more damage
- **Weak**: Deal 25% less damage
- **Poison**: Take damage at end of turn

### Map
- Navigate through a procedurally generated map
- Choose between combat, elite, rest, shop, and event nodes
- Defeat the boss at the end of each act

## Characters

### Ironclad (Warrior)
- 80 HP
- Starting relic: Burning Blood (heal 6 HP after combat)
- Focus on strength and big attacks

### Silent (Mage)
- 70 HP
- Starting relic: Ring of the Snake (draw 2 extra cards turn 1)
- Focus on poison and shivs
