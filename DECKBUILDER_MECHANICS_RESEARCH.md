# Comprehensive Roguelike Deckbuilder Mechanics Research

A deep dive into mechanics, cards, items, and systems from the most popular roguelike deckbuilders. Use this as reference for game design inspiration.

---

## Table of Contents
1. [Core Game Structures](#core-game-structures)
2. [Card Mechanics & Keywords](#card-mechanics--keywords)
3. [Character/Class Systems](#characterclass-systems)
4. [Resource Systems](#resource-systems)
5. [Combat Innovations](#combat-innovations)
6. [Meta-Progression Systems](#meta-progression-systems)
7. [Status Effects & Debuffs](#status-effects--debuffs)
8. [Unique Game Mechanics](#unique-game-mechanics)
9. [Enemy & Boss Design](#enemy--boss-design)
10. [Items, Relics & Equipment](#items-relics--equipment)
11. [Map & Progression Systems](#map--progression-systems)

---

## Core Game Structures

### Traditional Deck-Draw (Slay the Spire Style)
- Draw 5 cards per turn from draw pile
- Play cards using energy (typically 3/turn)
- Discard remaining cards at end of turn
- Shuffle discard into draw when empty
- **Used by:** Slay the Spire, Monster Train, Inscryption, Tainted Grail

### Conveyor Belt System (MECHBORN)
- 7 cards visible in a "conveyor belt"
- Playing a card immediately draws a replacement
- More predictable draws, different strategic considerations
- No traditional hand management

### Fixed Deck Size (Vault of the Void)
- Deck is ALWAYS exactly 20 cards
- Can swap cards between battles freely
- Focus on choosing the right tool for each fight
- No deck bloat problems

### Two-Deck System (Nowhere Prophet, Griftlands)
- Separate decks for different purposes
- **Nowhere Prophet:** Convoy (followers) + Leader (spells)
- **Griftlands:** Combat deck + Negotiation deck
- Cards drawn from both simultaneously

### Real-Time Deck Combat (One Step From Eden)
- Cards cycle in real-time during combat
- Must dodge attacks while casting spells
- Action game meets deckbuilder
- Position-based targeting on grid

### Party-Based Shared Deck (Chrono Ark)
- Multiple characters, ONE shared deck
- Each character contributes unique cards
- Shared mana pool across party
- Draw 2 cards/turn, hand persists

---

## Card Mechanics & Keywords

### From Slay the Spire

| Keyword | Effect |
|---------|--------|
| **Exhaust** | Card is removed from deck for this combat after playing |
| **Ethereal** | Auto-exhausts if in hand at end of turn |
| **Innate** | Always appears in opening hand |
| **Retain** | Card doesn't discard at end of turn |
| **Unplayable** | Cannot be played (must discard/exhaust) |
| **X-Cost** | Costs all remaining energy, scales effect |

### Stance System (Slay the Spire - Watcher)
- **Neutral:** No bonuses
- **Calm:** Gain 2 energy when exiting
- **Wrath:** Deal AND take double damage
- **Divinity:** Triple damage, +3 energy, exits automatically

### Scry Mechanic
- Look at top X cards of draw pile
- May discard any of them
- Doesn't trigger "discard" effects
- Enables planning and deck manipulation

### Orb System (Slay the Spire - Defect)
- Orbs sit in slots, provide passive + evoke effects
- **Lightning:** Passive damage, evoke for burst
- **Frost:** Passive block, evoke for big block
- **Dark:** Grows each turn, evokes for massive damage
- **Plasma:** Gain energy passively and on evoke
- Focus stat amplifies orb effects

### Sigil System (Inscryption)
- Cards have "sigils" = abilities
- Can TRANSFER sigils between cards
- Create custom cards with multiple sigils
- 79 total sigils across all acts

**Key Sigils:**
- **Many Lives:** Survives sacrifice
- **Unkillable:** Returns to hand on death
- **Touch of Death:** Instant kill on damage
- **Airborne:** Attacks directly (bypasses blockers)
- **Bifurcated/Trifurcated Strike:** Multi-target attacks
- **Fledgling:** Transforms after X turns

### Gem Socket System (Roguebook)
- Cards have 0-2 gem slots
- Gems add effects: extra damage, block, copy card, reduce cost
- Gems are PERMANENT once socketed
- 4 gem rarities with increasing power

### Void Stone System (Vault of the Void)
- Similar to gems but can be rearranged (on certain characters)
- Different colors = different effect types
- Customize individual cards to strategy

---

## Character/Class Systems

### Slay the Spire Characters
1. **Ironclad:** Strength scaling, self-damage/healing synergies, exhaust
2. **Silent:** Poison, shivs (0-cost attacks), discard synergies
3. **Defect:** Orb manipulation, focus scaling, powers
4. **Watcher:** Stances, scry, divinity combos

### Monster Train Champions
- Champions are the core of deck composition
- Can only upgrade via Dark Forge event
- Three upgrade paths each with different focuses
- If killed, goes to Consume Pile (can reform)

**Example - Hornbreaker Prince:**
- Brawler path: Multistrike focus
- Reaper path: Attack + Slay ability
- Wrathful path: Balanced with Slay + Revenge

### Dicey Dungeons Classes
1. **Warrior:** Reroll dice up to 3x/turn, straightforward damage
2. **Thief:** Steals random enemy equipment, uses low dice (1-3)
3. **Robot:** "Calculate" system with CPU counter, jackpot mechanic
4. **Inventor:** Free gadget each round, destroys own equipment for parts
5. **Witch:** Throw dice for 1 damage each, weak but unique
6. **Jester:** Deck of cards instead of equipment, Snap! limit break

### Chrono Ark (20 Characters)
- Each has 12 unique cards
- Multiple build paths per character
- Can role-switch some characters
- Even healers have distinct playstyles (damage whip healer vs barrier healer)

### Griftlands Dual-Archetype System
Per deck type (Combat & Negotiation):
- **Diplomacy (Green):** Influence points, scaling damage
- **Hostility (Red):** Bonus damage through Dominance, play many cards
- **Manipulate (Purple):** Composure/defense, hand manipulation

---

## Resource Systems

### Energy/Mana (Standard)
- Gain fixed amount per turn (usually 3)
- Spend to play cards
- Resets each turn

### Ammo System (Pirates Outlaws)
- Ranged attacks cost ammo
- Melee attacks are FREE
- Must use "reload" cards to restore ammo
- No turn limit - play until out of ammo

### Purge for Energy (Vault of the Void)
- Discard any card to gain 1 energy
- Cards go to discard (not lost)
- Encourages aggressive hand cycling
- Some cards have "purge" triggers

### Momentum (Fights in Tight Spaces)
- Energy equivalent for martial arts moves
- Builds and spends during combat
- Positioning affects available moves

### Action Count System (Chrono Ark)
- Enemies show number before they act
- Each skill played reduces count by 1
- **Swiftness** skills don't reduce count
- Creates tension and planning

### Escalating Energy (Nowhere Prophet)
- Start at 3 energy, opponent at 4
- Each turn: energy cap increases by 1
- Similar to Hearthstone mana crystals

### CPU Counter (Dicey Dungeons - Robot)
- Must hit target number EXACTLY
- Going over = turn ends immediately
- Hit exactly = jackpot bonus move
- High risk/reward resource management

---

## Combat Innovations

### Vertical Tower Defense (Monster Train)
- Three floors to defend
- Place units on different levels
- Enemies climb up the train
- Must protect the Pyre at top

### Positioning Grid (Nowhere Prophet, Chrono Ark)
- Grid-based unit placement
- Use terrain/obstacles as cover
- Positioning affects targeting and protection
- Front units protect back units

### Ring of Cards (Ring of Pain)
- Dungeon IS a ring of cards
- Choose which adjacent card to interact with
- Navigate by moving around the ring
- Can stealth past enemies

### Tile-Based Combat (Shogun Showdown)
- Single-axis combat
- Position and timing matter
- Enemies telegraph moves
- Unique tactical feel

### Lane Combat (Arcanium)
- 4 lanes for combat
- AI-controlled minions
- Coordinate 3 heroes' abilities
- Stuns prevent card play but allow repositioning

### Argument System (Griftlands Negotiation)
- Deploy "arguments" with their own HP
- Arguments can be attacked/defended
- Destroying argument = overflow to core
- Adds strategic layer beyond direct damage

### Turn Order / Speed (Various)
- **Ring of Pain:** Outspeeding enemies = attack first
- **Chrono Ark:** Speed stat determines who acts first
- **Inscryption:** Simultaneous attack resolution

---

## Meta-Progression Systems

### Unlock-Only (Pure Roguelike)
- **Slay the Spire:** Unlock new cards/relics, no power increase
- **Monster Train:** Similar - new content, not stronger starts
- Purist approach - skill matters most

### Character Leveling
- **Chrono Ark:** Characters level up, unlock new card variants
- **Arcanium:** Out-of-session talent trees per hero
- **Across the Obelisk:** Perks unlocked through achievements

### Currency-Based Upgrades
- **Roguebook:** Embellishments upgrade HP, damage, guaranteed relics
- **Rogue Legacy:** Spend meta-currency on family manor
- **Dead Cells:** Permanent ability unlocks

### Story-Driven Progression
- **Hades:** Story unfolds over many runs
- **Inscryption:** Meta-narrative across acts
- Dying is part of the experience

### Ascension/Difficulty Systems
- **Slay the Spire:** 20 Ascension levels with stacking modifiers
- Provides endless challenge
- Some games: unlock higher difficulties through wins

---

## Status Effects & Debuffs

### Damage Over Time (DoT)

| Effect | Behavior |
|--------|----------|
| **Poison** | Deals damage, often stacks, may reduce over time |
| **Bleed** | Damage over time, may trigger on movement |
| **Burn** | Fire damage, may spread to nearby targets |

### Stat Modifiers

| Effect | Behavior |
|--------|----------|
| **Weak** | Target deals reduced damage (usually 25-30%) |
| **Vulnerable** | Target takes increased damage (usually 50%) |
| **Frail** | Block gained is reduced |
| **Strength Down** | Reduces attack power |

### Control Effects

| Effect | Behavior |
|--------|----------|
| **Freeze** | Skip turn or restricted movement |
| **Stun** | Cannot act |
| **Root** | Cannot move but can still act |
| **Silence** | Cannot use abilities/spells |

### Unique Status Effects

**Inscryption:**
- **Stinky:** Adjacent enemies lose 1 power

**Slay the Spire:**
- **Intangible:** Reduce ALL damage to 1
- **Artifact:** Blocks next debuff application
- **Metallicize:** Gain block at end of turn
- **Thorns:** Deal damage when attacked
- **Barricade:** Block doesn't expire

**Griftlands:**
- **Composure:** Temporary HP for negotiation turn
- **Dominance:** Bonus damage for hostility cards
- **Influence:** Scaling for diplomacy cards

**Chrono Ark:**
- **Healing Gauge:** End-of-battle HP restoration
- **Overheal:** Bypasses healing efficiency penalties

---

## Unique Game Mechanics

### Joker System (Balatro)
- Jokers are passive effects held in slots (usually 5)
- 150 jokers with 4 rarities
- Core of scoring synergies
- Joker ORDER matters (left-to-right scoring)

**Rarity Rates:**
- Common: 70%
- Uncommon: 25%
- Rare: 5%
- Legendary: 0.3%

### Poker Hand Scoring (Balatro)
- Hands have Chips x Mult values
- "Contains" mechanic: Four of a Kind contains Three of a Kind, Pair
- Trigger effects based on hand contents
- Planet cards upgrade hand types permanently

### Dialogue as Deckbuilding (Signs of the Sojourner)
- Cards have symbols on each side
- Match symbols to succeed in conversation
- Different symbols = different communication styles
- Deck represents your personality/identity
- Fatigue cards accumulate from travel

### Sacrifice System (Inscryption)
- Must sacrifice creatures to play stronger ones
- Creates economy of weak vs strong cards
- Death cards created from your fallen cards
- Black Goat = premium sacrifice fodder

### Death Card Creation (Inscryption)
- When you die, create a custom "Death Card"
- Choose stats and sigils from your run
- Appears in future runs
- Only in Act 1

### Follower Permadeath (Nowhere Prophet)
- Followers can be wounded
- Wounded twice = permanent death
- Dead cards become useless
- Creates attachment and careful play

### Ally Stacking (Roguebook)
- Allies can stack (e.g., 12 frogs)
- Attack = number of stacks, then reduce by 1
- Build around ally multiplication
- Synergies with "if ally in play" effects

### Two-Hero System (Roguebook)
- Control 2 heroes simultaneously
- Front hero protects back hero
- Switch positions for combos
- Each hero has 50+ cards, unique skill tree

### Jackpot Mechanic (Dicey Dungeons - Robot)
- Must hit EXACT target number
- Over = disaster, exact = bonus
- Creates tension in dice allocation

### Talent Tiers (Roguebook)
- Unlocked based on deck size
- Larger deck = more talents
- Reverses typical "thin your deck" strategy

---

## Enemy & Boss Design

### Intent System
- **Slay the Spire style:** Show what enemy will do next turn
- Allows player to plan defense/offense
- Creates information-based strategy

### Reinforcement Waves (Vault of the Void)
- Enemies summon reinforcements until progress bar fills
- Must kill quickly or get overwhelmed
- Adds urgency to combat

### Boss Patterns
**Monster Train - Seraph:**
- 3 variations to prepare for
- Structure entire run around boss weakness

**Slay the Spire bosses:**
- Each has unique mechanics requiring adaptation
- Scaling difficulty forces deck evolution

### Elite Encounters
- Optional harder fights for better rewards
- Risk/reward balance
- Often have unique mechanics

### Enemy Keywords/Abilities
- Artifact: Blocks debuffs
- Thorns: Damage on attack
- Curl Up: Gain block when hit
- Split: Create copies on death
- Minion summoning

---

## Items, Relics & Equipment

### Relic Categories (Slay the Spire)
- **Starter Relics:** Character-specific starting item
- **Common:** Frequent drops, modest effects
- **Uncommon:** Less frequent, stronger
- **Rare:** Powerful, game-changing
- **Boss Relics:** Choose after defeating boss, often trade-offs
- **Event Relics:** From special encounters
- **Shop Relics:** Purchasable

### Notable Relic Effects
- **Energy:** Ice Cream (energy carries over)
- **Card Draw:** Ring of the Snake (+2 cards turn 1)
- **Scaling:** Kunai (gain dex on 3 attacks)
- **Defense:** Orichalcum (gain block if none at end)
- **Transformation:** Pandora's Box (transform all strikes/defends)

### Relic Synergy Timing
- Early: Survivability, card draw
- Mid: Strategy amplification
- Late: Damage maximization, boss-killing

### Item System (Inscryption)
- Consumable items in inventory
- **Pliers:** Damage yourself for direct hit on enemy
- **Fan:** Give all creatures Flying for 1 turn
- **Hourglass:** Enemy skips next turn
- **Scissors:** Destroy one enemy card

### Grafts (Griftlands)
- Permanent passive bonuses
- Combat grafts vs Negotiation grafts
- Different rarities with scaling power

### Artifacts (One Step From Eden)
- Passive abilities
- Choose after most battles
- Combine with spells for builds

---

## Map & Progression Systems

### Branching Paths (Slay the Spire)
- Multiple routes through each act
- Different node types visible
- Plan path based on needs
- Elite paths = harder but more rewards

### Node Types
- **Combat:** Regular enemy encounters
- **Elite:** Harder enemies, guaranteed relic
- **Rest Site:** Heal or upgrade a card
- **Shop:** Buy cards, relics, remove cards
- **Event:** Random encounter with choices
- **Treasure:** Guaranteed chest
- **Boss:** End of act

### Map Exploration (Roguebook)
- Hex-based map to explore
- Use ink/brushes to reveal tiles
- Hidden treasures and encounters
- Larger exploration = more rewards

### Chapter System (Pirates Outlaws)
- 7 unlockable maps/chapters
- Each has unique difficulty and secrets
- Navigate mode = roguelike expedition
- Tavern stops for healing and card removal

### Ring Structure (Ring of Pain)
- Dungeon is a circular card arrangement
- Move around ring to choose encounters
- Skull exits = elite-like challenges
- Color-coded doors = special areas

---

## Cool Ideas Summary

### Mechanics Worth Implementing

1. **Intent System** - Show enemy actions for strategic planning
2. **Multiple Resource Types** - Energy + secondary resource (ammo, orbs, stances)
3. **Card Keywords** - Exhaust, Retain, Innate for deck manipulation
4. **Positioning Matters** - Grid or lane-based combat adds depth
5. **Scaling Synergies** - Poison stacks, strength builds, orb focus
6. **Risk/Reward Choices** - Boss relics with downsides, elite paths
7. **Character Variety** - Distinct playstyles, not just stat differences
8. **Permadeath Consequences** - Wounded followers, permanent loss
9. **Card Customization** - Gems, sigils, upgrades
10. **Multiple Win Conditions** - Combat vs negotiation, stealth vs fight

### Innovative Concepts to Explore

1. **Dialogue as Combat** - Signs of the Sojourner's symbol matching
2. **Poker Scoring** - Balatro's chip x mult with hand types
3. **Conveyor Belt Hands** - MECHBORN's always-refilling cards
4. **Fixed Deck Size** - Vault of the Void's 20-card limit
5. **Tower Defense Hybrid** - Monster Train's three-floor defense
6. **Real-Time Casting** - One Step From Eden's action combat
7. **Dual Deck Systems** - Combat + Social/Negotiation decks
8. **Party Synergies** - Shared deck, individual characters

### Avoiding Common Pitfalls

1. **Deck Bloat** - Provide card removal options
2. **Dead Draws** - Curses/wounds need counterplay
3. **Dominant Strategies** - Balance multiple viable builds
4. **Run Length** - ~1 hour seems ideal for most games
5. **Meta-Progression Balance** - Don't make early runs feel unfair
6. **Information Overload** - Clear UI for complex systems

---

## Sources

- [Slay the Spire Wiki](https://slaythespire.wiki.gg/)
- [Monster Train Wiki](https://monster-train.fandom.com/)
- [Inscryption Wiki](https://inscryption.fandom.com/)
- [Balatro Wiki](https://balatrowiki.org/)
- [Griftlands Wiki](https://griftlands.fandom.com/)
- [Nowhere Prophet Wiki](https://nowhereprophet.fandom.com/)
- [Chrono Ark Guides](https://steamcommunity.com/app/1188930/guides/)
- [Ring of Pain Guides](https://steamcommunity.com/app/998740)
- [Vault of the Void Guides](https://steamcommunity.com/app/1135810)
- [Dicey Dungeons Wiki](https://diceydungeons.fandom.com/)
- [One Step From Eden Wiki](https://onestepfromeden.fandom.com/)
- [Signs of the Sojourner Wiki](https://signs-of-the-sojourner.fandom.com/)
- [Roguebook Guides](https://steamcommunity.com/app/1076200)
- [Pirates Outlaws Guides](https://www.levelwinner.com/pirates-outlaws-beginners-guide/)
- [Rogueliker - Best Roguelike Deckbuilders](https://rogueliker.com/roguelike-deckbuilders/)
- [Turn Based Lovers](https://turnbasedlovers.com/)
- [GameRant - Deck Builder Rankings](https://gamerant.com/)
