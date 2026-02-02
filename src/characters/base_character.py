"""Character class definitions."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING

from src.entities.player import Player
from src.entities.card import CardInstance

if TYPE_CHECKING:
    from src.entities.relic import RelicInstance


class CharacterClass(Enum):
    """Available character classes."""
    WARRIOR = auto()
    MAGE = auto()
    ROGUE = auto()


@dataclass
class CharacterDefinition:
    """
    Definition of a playable character class.

    Contains starting stats, deck, and relic.
    """
    character_class: CharacterClass
    name: str
    description: str
    max_hp: int
    starting_gold: int = 99
    max_energy: int = 3

    def create_player(self) -> Player:
        """Create a new Player instance for this character."""
        return Player(
            name=self.name,
            max_hp=self.max_hp,
            current_hp=self.max_hp,
            gold=self.starting_gold,
            max_energy=self.max_energy,
            energy=self.max_energy,
        )


# Warrior character definition
WARRIOR = CharacterDefinition(
    character_class=CharacterClass.WARRIOR,
    name="Ironclad",
    description="A battle-hardened warrior who harnesses pain to fuel powerful attacks.",
    max_hp=80,
    starting_gold=99,
    max_energy=3,
)


# Mage character definition
MAGE = CharacterDefinition(
    character_class=CharacterClass.MAGE,
    name="Silent",
    description="A deadly huntress from the foglands, masters poison and shivs.",
    max_hp=70,
    starting_gold=99,
    max_energy=3,
)


# Rogue character definition
ROGUE = CharacterDefinition(
    character_class=CharacterClass.ROGUE,
    name="Defect",
    description="A combat automaton that channels energy through orbs.",
    max_hp=75,
    starting_gold=99,
    max_energy=3,
)


CHARACTER_REGISTRY: dict[CharacterClass, CharacterDefinition] = {
    CharacterClass.WARRIOR: WARRIOR,
    CharacterClass.MAGE: MAGE,
    CharacterClass.ROGUE: ROGUE,
}


def get_character_definition(char_class: CharacterClass) -> CharacterDefinition:
    """Get the definition for a character class."""
    return CHARACTER_REGISTRY[char_class]


def create_player_for_class(char_class: CharacterClass) -> Player:
    """Create a new player for a character class."""
    definition = get_character_definition(char_class)
    return definition.create_player()


class Character:
    """
    A character instance for a run.

    Wraps the Player with character-specific card pools and abilities.
    """

    def __init__(self, definition: CharacterDefinition):
        self.definition = definition
        self.player = definition.create_player()
        self._starting_deck_initialized = False
        self._starting_relic_initialized = False

    @classmethod
    def create(cls, char_class: CharacterClass) -> Character:
        """Create a new Character instance for a class."""
        definition = get_character_definition(char_class)
        return cls(definition)

    @property
    def name(self) -> str:
        return self.definition.name

    @property
    def character_class(self) -> CharacterClass:
        return self.definition.character_class

    def initialize_starting_deck(self, cards: list[CardInstance]) -> None:
        """Set up the starting deck for this character."""
        self.player.master_deck = cards
        self._starting_deck_initialized = True

    def initialize_starting_relic(self, relic: RelicInstance) -> None:
        """Set up the starting relic for this character."""
        self.player.relics = [relic]
        self._starting_relic_initialized = True

    def is_fully_initialized(self) -> bool:
        """Check if the character has been fully set up."""
        return self._starting_deck_initialized and self._starting_relic_initialized

    def __str__(self) -> str:
        return f"{self.name} ({self.character_class.name})"
