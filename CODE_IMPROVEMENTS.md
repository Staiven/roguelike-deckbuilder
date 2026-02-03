# Code Improvement Recommendations

Based on analysis of other open-source roguelike deckbuilders and software engineering best practices.

---

## Priority 1: Data-Driven Content (High Impact)

### Current State
Cards, enemies, and relics are defined as Python constants. This works but requires code changes for new content.

### Recommendation
Add JSON/YAML support for content definitions, allowing designers to add content without touching Python.

```
data/
  cards/
    warrior_cards.json
    mage_cards.json
  enemies/
    act1_enemies.json
  relics/
    common_relics.json
```

**Benefits:**
- Non-coders can edit JSON files
- Easier balancing (just edit numbers)
- Hot-reloading possible during development
- Cleaner separation of data vs logic

**Implementation:**
- Keep Python dataclasses for type safety
- Add JSON loader that validates against schemas
- Python constants become the "fallback" or get generated from JSON

---

## Priority 2: Action/Event Queue System (Medium Impact)

### Current State
Effects execute immediately when cards are played.

### Recommendation
Implement an action queue like [Slay the Web](https://github.com/oskarrough/slaytheweb) does.

```python
class ActionQueue:
    def __init__(self):
        self.queue: list[Action] = []

    def add(self, action: Action) -> None:
        self.queue.append(action)

    def process(self) -> list[ActionResult]:
        results = []
        while self.queue:
            action = self.queue.pop(0)
            result = action.execute()
            results.append(result)
            # Actions can queue more actions
        return results
```

**Benefits:**
- Cleaner animation hooks (frontend can animate each action)
- Easier to implement "when X happens, do Y" triggers
- Better debugging (can log action queue)
- Supports undo/replay for testing

---

## Priority 3: Event Bus Improvements (Medium Impact)

### Current State
You have an event bus (`src/core/events.py`) but it's underutilized.

### Recommendation
Use events more consistently for game state changes:

```python
# Events to add:
class Events(Enum):
    CARD_PLAYED = auto()
    CARD_DRAWN = auto()
    CARD_EXHAUSTED = auto()
    DAMAGE_DEALT = auto()
    DAMAGE_TAKEN = auto()
    BLOCK_GAINED = auto()
    STATUS_APPLIED = auto()
    TURN_STARTED = auto()
    TURN_ENDED = auto()
    ENEMY_DIED = auto()
    COMBAT_STARTED = auto()
    COMBAT_ENDED = auto()
```

**Benefits:**
- Relics can subscribe to events (cleaner than current trigger system)
- Powers/effects can react to game state
- Frontend can subscribe for UI updates
- Easier to add achievements/stats tracking

---

## Priority 4: More Test Coverage (Medium Impact)

### Current State
55 tests covering core mechanics. No integration tests, no API tests.

### Recommendation
Add:

1. **Integration Tests** - Full combat scenarios
```python
def test_full_combat_scenario():
    """Test a complete combat from start to victory."""
    session = create_warrior_run(seed=42)
    session.start_run()
    # Play through a combat...
```

2. **API Tests** - Test the REST endpoints
```python
def test_create_game_endpoint():
    response = client.post("/api/game/new", json={"character_class": "warrior"})
    assert response.status_code == 200
```

3. **Card Balance Tests** - Verify card effects work as expected
```python
@pytest.mark.parametrize("card_id,expected_damage", [
    ("strike", 6),
    ("bash", 8),
])
def test_card_damage_values(card_id, expected_damage):
    ...
```

---

## Priority 5: Type Stubs for Complex Returns (Low Impact)

### Current State
Some functions return complex nested structures without clear typing.

### Recommendation
Add TypedDict or dataclasses for API responses:

```python
from typing import TypedDict

class CombatStateDict(TypedDict):
    player_hp: int
    player_block: int
    enemies: list[EnemyDict]
    hand: list[CardDict]
    energy: int
```

---

## Priority 6: Configuration System (Low Impact)

### Current State
Game constants are scattered throughout the code.

### Recommendation
Centralize configuration:

```python
# src/config.py
@dataclass
class GameConfig:
    # Combat
    starting_hand_size: int = 5
    max_hand_size: int = 10
    base_energy: int = 3

    # Map
    map_width: int = 7
    map_height: int = 15

    # Economy
    starting_gold: int = 99
    card_removal_cost: int = 75
    card_removal_increase: int = 25

CONFIG = GameConfig()
```

**Benefits:**
- Easy difficulty modifiers
- Clear game constants
- Could load from file for modding

---

## Priority 7: Logging System (Low Impact)

### Current State
No structured logging.

### Recommendation
Add logging for debugging and analytics:

```python
import logging

logger = logging.getLogger("roguelike")

# In combat
logger.info("Card played", extra={
    "card": card.name,
    "target": target.name if target else None,
    "damage_dealt": result.damage,
})
```

---

## Quick Wins (Can Do Now)

### 1. Add `__all__` to modules
Makes imports cleaner and documents public API.

### 2. Add docstrings to public functions
Many functions lack docstrings.

### 3. Use `Enum` for string constants
Replace string literals like `"attack"`, `"skill"` with enums.

### 4. Add `py.typed` marker
Marks package as typed for better IDE support.

### 5. Add pre-commit hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-mypy
    hooks:
      - id: mypy
```

---

## Architecture Comparison

| Feature | Your Codebase | Slay the Web | Best Practice |
|---------|---------------|--------------|---------------|
| Engine/UI Separation | Good | Excellent | Separate packages |
| Data-Driven Content | Partial (Python) | JSON | JSON + validation |
| Action Queue | No | Yes | Yes for animations |
| Event System | Basic | Unknown | Comprehensive |
| Test Coverage | Core only | Has tests | Core + Integration + API |
| Type Safety | Good | N/A (JS) | Full typing |

---

## Recommended Order of Implementation

1. **Add API tests** (1-2 hours) - Quick win, catches regressions
2. **Expand event system** (2-3 hours) - Enables better relic/power triggers
3. **JSON content loading** (4-6 hours) - Big quality of life for designers
4. **Action queue** (4-6 hours) - Enables better frontend animations
5. **Configuration system** (1-2 hours) - Quick win for organization

---

## Sources

- [Slay the Web](https://github.com/oskarrough/slaytheweb) - JavaScript implementation
- [DeckBuilderRoguelikeEngine](https://github.com/hoshutakemoto/DeckBuilderRoguelikeEngine) - Architecture-focused engine
- [Decapitate the Spire](https://github.com/jahabrewer/decapitate-the-spire) - Headless Python clone
- [NueDeck](https://github.com/Arefnue/NueDeck) - Unity template
- [RogueBasin ECS](https://www.roguebasin.com/index.php?title=Entity_Component_System) - Design patterns
