# Roguelike Deckbuilder Implementation Reference

A detailed technical reference for implementing roguelike deckbuilder mechanics. Includes exact formulas, numbers, data structures, and interaction rules.

---

## Table of Contents
1. [Core Systems & Formulas](#1-core-systems--formulas)
2. [Status Effects Database](#2-status-effects-database)
3. [Card Keywords Reference](#3-card-keywords-reference)
4. [Slay the Spire Data](#4-slay-the-spire-data)
5. [Balatro Data](#5-balatro-data)
6. [Monster Train Data](#6-monster-train-data)
7. [Inscryption Data](#7-inscryption-data)
8. [Hades Boon System](#8-hades-boon-system)
9. [Economy & Progression](#9-economy--progression)
10. [Enemy Design Patterns](#10-enemy-design-patterns)
11. [TypeScript Interfaces](#11-typescript-interfaces)

---

## 1. Core Systems & Formulas

### 1.1 Damage Calculation Order (Slay the Spire)

```
Final Damage = floor((Base Damage + Strength) * Weak Modifier * Vulnerable Modifier)

Where:
- Weak Modifier = 0.75 (deal 25% less damage)
- Vulnerable Modifier = 1.50 (take 50% more damage)
- Strength = flat +/- per hit (applies to EACH hit of multi-hit attacks)
```

**Order of Operations:**
1. Start with card's base damage
2. Add/subtract Strength (flat modifier, per hit)
3. Apply Weak (multiplicative, rounds down)
4. Apply Vulnerable (multiplicative, rounds down)

**Example:**
```
Card: 6 damage x 3 hits
Strength: +2
Enemy has Vulnerable

Per hit: floor((6 + 2) * 1.5) = floor(12) = 12 damage
Total: 12 * 3 = 36 damage
```

### 1.2 Block Calculation

```
Final Block = floor((Base Block + Dexterity) * Frail Modifier)

Where:
- Frail Modifier = 0.75 (gain 25% less block)
- Dexterity = flat +/- to all block gained from cards
```

**Note:** Frail only affects card-based block. Relics, Metallicize, Plated Armor, Frost Orbs are NOT affected.

### 1.3 Poison Damage Formula (Slay the Spire)

```
Total Poison Damage = P * (P + 1) / 2

Where P = initial poison stacks
```

**Timing:** At START of enemy turn:
1. Enemy loses HP equal to poison stacks (ignores block)
2. Poison stacks decrease by 1

**Examples:**
| Poison | Total Damage |
|--------|--------------|
| 5      | 15           |
| 10     | 55           |
| 20     | 210          |
| 50     | 1275         |
| 100    | 5050         |

**Catalyst Interaction:**
- Base: Doubles poison (2x)
- Upgraded: Triples poison (3x)
- With Burst: Cast twice = 4x or 9x
- Blocked by 1 Artifact stack

### 1.4 Balatro Scoring Formula

```
Final Score = Total Chips × Total Mult

Calculation Order:
1. Start with hand's base Chips and Mult
2. Add flat +Chips from cards, jokers, enhancements
3. Add flat +Mult from cards, jokers
4. Apply ×Mult multipliers (multiplicative, in order left-to-right)
```

**Base Hand Values:**

| Hand            | Chips | Mult | Level Up (+Chips/+Mult) |
|-----------------|-------|------|-------------------------|
| High Card       | 5     | 1    | +10/+1                  |
| Pair            | 10    | 2    | +15/+1                  |
| Two Pair        | 20    | 2    | +20/+1                  |
| Three of Kind   | 30    | 3    | +20/+2                  |
| Straight        | 30    | 4    | +30/+3                  |
| Flush           | 35    | 4    | +15/+2                  |
| Full House      | 40    | 4    | +25/+2                  |
| Four of Kind    | 60    | 7    | +30/+3                  |
| Straight Flush  | 100   | 8    | +40/+4                  |
| Five of Kind    | 120   | 12   | +35/+3                  |
| Flush House     | 140   | 14   | +40/+4                  |
| Flush Five      | 160   | 16   | +50/+3                  |

**Card Chip Values:**
| Rank | Chips |
|------|-------|
| 2-10 | Face value |
| J/Q/K | 10   |
| A     | 11   |

---

## 2. Status Effects Database

### 2.1 Debuffs (Applied to Enemies)

```typescript
interface Debuff {
  name: string;
  stackable: boolean;
  duration: number | 'permanent' | 'until_triggered';
  effect: string;
  formula?: string;
}
```

| Name | Stackable | Duration | Effect |
|------|-----------|----------|--------|
| **Vulnerable** | Yes (turns) | X turns | Take 50% more damage from attacks |
| **Weak** | Yes (turns) | X turns | Deal 25% less damage |
| **Poison** | Yes (stacks) | Until 0 | Lose HP = stacks at turn start, then -1 |
| **Frail** | Yes (turns) | X turns | Gain 25% less block from cards |
| **Doom** (Ares/StS) | Yes (stacks) | 1-1.5s | Take burst damage after delay |
| **Hangover** (Dionysus) | Yes (stacks) | 4 sec | Take damage every 0.5s, max 5 stacks |
| **Chill** (Demeter) | Yes (stacks) | Until removed | Slow attacks, at 10 stacks = shatter |
| **Marked** (Artemis) | No | 2.5 sec | Higher crit chance from all sources |
| **Exposed** (Athena) | No | 5 sec | Take more backstab damage |

### 2.2 Buffs (Applied to Player/Allies)

| Name | Stackable | Duration | Effect |
|------|-----------|----------|--------|
| **Strength** | Yes | Combat | +1 damage per attack per stack |
| **Dexterity** | Yes | Combat | +1 block per card per stack |
| **Artifact** | Yes (charges) | Until used | Negates next debuff application |
| **Intangible** | Yes (turns) | X turns | ALL damage reduced to 1 |
| **Barricade** | No | Combat | Block doesn't expire at turn end |
| **Metallicize** | Yes (stacks) | Combat | Gain X block at end of turn |
| **Thorns** | Yes (stacks) | Combat | Deal X damage when attacked |
| **Plated Armor** | Yes (stacks) | Combat | Gain X block/turn, lose 1 stack when hit |
| **Rage** (Monster Train) | Yes (stacks) | Combat | +X attack per stack |
| **Armor** (Monster Train) | Yes (stacks) | Until damaged | Absorbs X damage, then removed |
| **Multistrike** | Yes (stacks) | Combat | Attack X additional times |

### 2.3 Status Effect Interactions

**Artifact Blocking:**
- 1 Artifact negates ALL stacks from a single source
- Example: Card applies 5 Poison → Artifact blocks all 5
- Does NOT block self-inflicted debuffs

**Timing Priority:**
1. Intangible (reduces to 1)
2. Block (absorbs remaining)
3. Plated Armor/Thorns (on damage received)
4. HP loss effects

**Rounding Rules:**
- Always round DOWN (floor)
- Frail: 5 block → floor(5 * 0.75) = 3
- Vulnerable: 7 damage → floor(7 * 1.5) = 10

---

## 3. Card Keywords Reference

### 3.1 Slay the Spire Keywords

```typescript
enum CardKeyword {
  EXHAUST = 'exhaust',      // Removed from deck for this combat
  ETHEREAL = 'ethereal',    // Auto-exhausts if in hand at turn end
  INNATE = 'innate',        // Always in opening hand
  RETAIN = 'retain',        // Doesn't discard at turn end
  UNPLAYABLE = 'unplayable' // Cannot be played from hand
}
```

**Exhaust Interactions:**
- Exhausted cards go to separate Exhaust pile
- Exhume (Ironclad) can retrieve exhausted cards
- Feel No Pain: +3 block when card exhausted
- Dark Embrace: +1 card draw when card exhausted
- Dead Branch: Add random card when card exhausted

**Ethereal Interactions:**
- Triggers at END of turn (after discards)
- Retain does NOT prevent Ethereal exhaust
- Can be played/discarded normally before turn ends

**Innate Priority:**
- Multiple Innate cards: all go to opening hand
- If more Innate than hand size: random selection

### 3.2 X-Cost Cards

```typescript
interface XCostCard {
  effect: (energySpent: number) => void;
  minimumX: number;  // Usually 0
  scaling: 'linear' | 'exponential';
}
```

**Examples:**
| Card | Effect per X |
|------|--------------|
| Whirlwind | Deal 5 damage X times to ALL |
| Malaise | Apply X Weak, enemy loses X Strength |
| Skewer | Deal 7 damage X times |
| Multicast | Evoke orb X times |
| Omniscience | Play a card X times |

**Chemical X Relic:** +2 to all X effects

### 3.3 Inscryption Keywords/Sigils

```typescript
interface Sigil {
  name: string;
  powerLevel: 1 | 2 | 3 | 4 | 5;
  trigger: 'passive' | 'on_play' | 'on_death' | 'on_attack' | 'activated';
  effect: string;
}
```

**Combat Sigils:**
| Sigil | Trigger | Effect |
|-------|---------|--------|
| Airborne | Passive | Attacks directly, ignores blockers |
| Touch of Death | On Attack | Instantly kills damaged target |
| Bifurcated Strike | On Attack | Hits left and right lanes |
| Trifurcated Strike | On Attack | Hits all 3 opposing lanes |
| Stinky | Passive | Adjacent enemies have -1 power |

**Survival Sigils:**
| Sigil | Trigger | Effect |
|-------|---------|--------|
| Unkillable | On Death | Returns to hand |
| Many Lives | On Sacrifice | Does not die (9 uses) |
| Armored | Passive | Blocks first hit |
| Repulsive | Passive | Enemies won't attack this |
| Fledgling | End of Turn | Evolves after 1 turn |

**Economy Sigils:**
| Sigil | Trigger | Effect |
|-------|---------|--------|
| Worthy Sacrifice | On Sacrifice | Worth 3 blood |
| Bone King | On Death | Grants 4 bones instead of 1 |
| Corpse Eater | On Ally Death | Plays for free |

---

## 4. Slay the Spire Data

### 4.1 Silent Poison Cards

```typescript
interface PoisonCard {
  name: string;
  cost: number;
  type: 'attack' | 'skill' | 'power';
  poisonBase: number;
  poisonUpgraded: number;
  additionalEffects?: string;
}
```

| Card | Cost | Type | Poison | Poison+ | Notes |
|------|------|------|--------|---------|-------|
| Deadly Poison | 1 | Skill | 5 | 7 | Single target |
| Poisoned Stab | 1 | Attack | 3 | 4 | Also deals 6 damage |
| Bouncing Flask | 2 | Skill | 3×3 | 3×4 | Random enemies |
| Crippling Cloud | 2 | Skill | 4 | 7 | ALL enemies, +2 Weak, Exhaust |
| Corpse Explosion | 2 | Skill | 6 | 9 | On death: deal MAX HP to all |
| Noxious Fumes | 1 | Power | 2/turn | 3/turn | ALL enemies each turn |
| Envenom | 2 | Power | 1/hit | 1/hit | Per unblocked attack damage |
| Catalyst | 1 | Skill | ×2 | ×3 | Multiply existing poison, Exhaust |
| Bane | 1 | Attack | 0 | 0 | 7 dmg, if poisoned: 7 again |

**Poison Relics:**
| Relic | Effect |
|-------|--------|
| Snecko Skull | +1 poison per application |
| The Specimen | On kill: transfer poison to random enemy |
| Twisted Funnel | Combat start: 4 poison to ALL |

### 4.2 Ironclad Strength Cards

| Card | Cost | Effect | Effect+ |
|------|------|--------|---------|
| Inflame | 1 | +2 Strength | +3 Strength |
| Spot Weakness | 1 | If attacking: +3 Str | +4 Str |
| Demon Form | 3 | +2 Str per turn | +3 Str per turn |
| Limit Break | 1 | Double Strength, Exhaust | No Exhaust |
| Rupture | 1 | +1 Str when lose HP from card | +2 Str |
| Flex | 0 | +2 Str this turn only | +4 Str |

**Strength-Scaling Attacks:**
| Card | Base | Str Multiplier |
|------|------|----------------|
| Heavy Blade | 14 | ×3 (×5 upgraded) |
| Sword Boomerang | 3×3 | ×1 per hit |
| Pummel | 2×4 | ×1 per hit |
| Twin Strike | 5×2 | ×1 per hit |

### 4.3 Enemy Patterns

```typescript
interface EnemyPattern {
  name: string;
  health: { base: number; ascension7?: number };
  moves: Move[];
  pattern: string; // Probability/sequence description
}
```

**Jaw Worm (Act 1):**
```
HP: 40-44 (A7+: 42-46)
Moves:
- Chomp: 11-12 damage
- Thrash: 7 damage + 5 block
- Bellow: +3 Strength, +6 block

Pattern:
- Always starts with Chomp
- Then: 45% Bellow, 30% Thrash, 25% Chomp
- Cannot repeat same move twice
- Cannot Thrash 3× in a row
```

**Cultist (Act 1):**
```
HP: 48-54 (A7+: 50-56)
Moves:
- Incantation: Gain Ritual (4 Strength/turn)
- Dark Strike: 6 damage

Pattern:
- Turn 1: Always Incantation
- Turn 2+: Always Dark Strike
- Damage scales: 6 → 10 → 14 → 18...
```

**Gremlin Nob (Act 1 Elite):**
```
HP: 82-86 (A7+: 85-90)
Moves:
- Bellow: +2 Strength (enrages)
- Rush: 14-16 damage
- Skull Bash: 6 damage + 2 Vulnerable

Pattern:
- Turn 1: Always Bellow
- If player played Skill last turn: 33% Skull Bash
- Otherwise: alternates Rush/Skull Bash
- Gains +2 Str when you play any Skill
```

### 4.4 Relic Effects (Selected)

**Energy Relics (Boss):**
| Relic | Benefit | Drawback |
|-------|---------|----------|
| Coffee Dripper | +1 Energy | Cannot rest at campfires |
| Cursed Key | +1 Energy | Gain curse when opening chests |
| Ectoplasm | +1 Energy | Cannot gain gold |
| Fusion Hammer | +1 Energy | Cannot upgrade at campfires |
| Runic Dome | +1 Energy | Cannot see enemy intents |
| Philosopher's Stone | +1 Energy | Enemies start with +1 Strength |
| Sozu | +1 Energy | Cannot gain potions |
| Busted Crown | +1 Energy | 2 fewer card choices |

**Scaling Relics:**
| Relic | Effect |
|-------|--------|
| Kunai | Every 3 attacks: +1 Dexterity |
| Shuriken | Every 3 attacks: +1 Strength |
| Ornamental Fan | Every 3 attacks: +4 Block |
| Nunchaku | Every 10 attacks: +1 Energy |
| Pen Nib | Every 10 attacks: Double damage |
| Incense Burner | Every 6 turns: +1 Intangible |

---

## 5. Balatro Data

### 5.1 Joker Database (Full List)

```typescript
interface Joker {
  name: string;
  rarity: 'Common' | 'Uncommon' | 'Rare' | 'Legendary';
  cost: number;
  effect: {
    type: 'chips' | 'mult' | 'xmult' | 'money' | 'utility';
    value: number | string;
    condition?: string;
  };
}
```

**High-Value Jokers (×Mult):**

| Joker | Rarity | Cost | Effect |
|-------|--------|------|--------|
| Joker Stencil | Uncommon | $8 | ×1 Mult per empty Joker slot |
| Loyalty Card | Uncommon | $5 | ×4 Mult every 6 hands |
| Blackboard | Uncommon | $6 | ×3 Mult if all Spades or Clubs |
| Cavendish | Common | $4 | ×3 Mult (1/1000 destroy chance) |
| Card Sharp | Uncommon | $6 | ×3 Mult if hand type repeated |
| Baron | Rare | $8 | ×1.5 Mult per King held |
| Photograph | Common | $5 | First face card ×2 Mult |
| Ancient Joker | Rare | $8 | ×1.5 per suit card (suit changes) |
| The Duo | Rare | $8 | ×2 Mult if Pair in hand |
| The Trio | Rare | $8 | ×3 Mult if Three of Kind |
| The Family | Rare | $8 | ×4 Mult if Four of Kind |
| Blueprint | Rare | $10 | Copies Joker to right |
| Brainstorm | Rare | $10 | Copies leftmost Joker |

**+Chips Jokers:**

| Joker | Rarity | Cost | Effect |
|-------|--------|------|--------|
| Banner | Common | $5 | +30 Chips per discard remaining |
| Scary Face | Common | $4 | +30 Chips per face card scored |
| Sly Joker | Common | $3 | +50 Chips if Pair |
| Wily Joker | Common | $4 | +100 Chips if Three of Kind |
| Clever Joker | Common | $4 | +80 Chips if Two Pair |
| Ice Cream | Common | $5 | +100 Chips, -5 per hand |
| Stuntman | Rare | $7 | +250 Chips, -2 hand size |
| Arrowhead | Uncommon | $7 | +50 Chips per Spade scored |

**+Mult Jokers:**

| Joker | Rarity | Cost | Effect |
|-------|--------|------|--------|
| Joker | Common | $2 | +4 Mult |
| Jolly Joker | Common | $3 | +8 Mult if Pair |
| Zany Joker | Common | $4 | +12 Mult if Three of Kind |
| Mystic Summit | Common | $5 | +15 Mult when 0 discards |
| Half Joker | Common | $5 | +20 Mult if ≤3 cards |
| Fibonacci | Uncommon | $8 | +8 Mult for A/2/3/5/8 |
| Scholar | Common | $4 | +20 Chips, +4 Mult for Aces |
| Shoot the Moon | Common | $5 | +13 Mult per Queen held |
| Smiley Face | Common | $4 | +5 Mult per face card |
| Onyx Agate | Uncommon | $7 | +7 Mult per Club scored |

### 5.2 Card Modifiers

```typescript
interface CardModifier {
  category: 'enhancement' | 'edition' | 'seal';
  name: string;
  effect: string;
  stacksWithOthers: boolean;
}
```

**Enhancements (8 types, mutually exclusive):**

| Enhancement | Effect |
|-------------|--------|
| Bonus | +30 Chips when scored |
| Mult | +4 Mult when scored |
| Wild | Counts as all suits |
| Glass | ×2 Mult when scored, 1/4 break chance |
| Steel | ×1.5 Mult while held (not played) |
| Stone | +50 Chips, always scores, no rank/suit |
| Gold | +$3 when held at round end |
| Lucky | 1/5 chance +20 Mult, 1/15 chance +$20 |

**Editions (4 types, mutually exclusive):**

| Edition | Effect |
|---------|--------|
| Foil | +50 Chips |
| Holographic | +10 Mult |
| Polychrome | ×1.5 Mult |
| Negative (Jokers only) | +1 Joker slot |

**Seals (4 types, mutually exclusive):**

| Seal | Effect |
|------|--------|
| Gold | Earn $3 if in hand at round end |
| Red | Retrigger this card |
| Blue | Creates Planet if held at round end |
| Purple | Creates Tarot if discarded |

**Stacking Rules:**
- Each card can have 1 Enhancement + 1 Edition + 1 Seal
- Applying same category overwrites previous
- Maximum combinations: 8 × 4 × 4 = 128 unique modifier sets

### 5.3 Consumables

**Planet Cards (12):**
| Planet | Hand Upgraded | +Chips | +Mult |
|--------|---------------|--------|-------|
| Pluto | High Card | +10 | +1 |
| Mercury | Pair | +15 | +1 |
| Uranus | Two Pair | +20 | +1 |
| Venus | Three of Kind | +20 | +2 |
| Saturn | Straight | +30 | +3 |
| Jupiter | Flush | +15 | +2 |
| Mars | Full House | +25 | +2 |
| Earth | Four of Kind | +30 | +3 |
| Neptune | Straight Flush | +40 | +4 |
| Planet X | Five of Kind | +35 | +3 |
| Ceres | Flush House | +40 | +4 |
| Eris | Flush Five | +50 | +3 |

**Tarot Cards (22):**
| Tarot | Effect |
|-------|--------|
| The Fool | Copy last Tarot/Planet used |
| The Magician | Add Lucky to 1-2 cards |
| High Priestess | Create up to 2 Planet cards |
| The Empress | Add Mult enhancement to 1-2 cards |
| The Emperor | Create up to 2 Tarot cards |
| The Hierophant | Add Bonus enhancement to 1-2 cards |
| The Lovers | Add Wild enhancement to 1 card |
| The Chariot | Add Steel enhancement to 1 card |
| Justice | Add Glass enhancement to 1 card |
| The Hermit | Double money (up to $20) |
| Wheel of Fortune | 1/4 chance: add Foil/Holo/Poly to random Joker |
| Strength | Increase rank of up to 2 cards by 1 |
| The Hanged Man | Destroy up to 2 cards |
| Death | Select 2 cards: left converts to right |
| Temperance | Gain $ equal to total Joker sell value (max $50) |
| The Devil | Add Gold enhancement to 1 card |
| The Tower | Add Stone enhancement to 1 card |
| The Star | Convert up to 3 cards to Diamonds |
| The Moon | Convert up to 3 cards to Clubs |
| The Sun | Convert up to 3 cards to Hearts |
| Judgement | Create random Joker (max Uncommon) |
| The World | Convert up to 3 cards to Spades |

---

## 6. Monster Train Data

### 6.1 Status Effects

```typescript
interface MonsterTrainStatus {
  name: string;
  type: 'buff' | 'debuff';
  stackable: boolean;
  persistent: boolean; // Survives between floors
  effect: string;
}
```

**Unit Buffs:**
| Status | Stacks | Effect |
|--------|--------|--------|
| Rage | Yes | +1 Attack per stack |
| Armor | Yes | Absorbs damage, removed when depleted |
| Multistrike | Yes | Additional attacks per stack |
| Quick | No | Acts before enemies |
| Endless | No | Returns to hand on death |
| Largestone | No | +25 HP |
| Battlestone | No | +10 Attack |

**Unit Debuffs:**
| Status | Stacks | Effect |
|--------|--------|--------|
| Dazed | Yes | -1 Attack per stack |
| Sap | Yes | -Attack for one attack, then removed |
| Rooted | No | Cannot move to other floors |
| Spell Weakness | Yes | +1 damage from spells per stack |

### 6.2 Clan Mechanics

**Hellhorned (Demons):**
- Core: Rage scaling, Armor tanking
- Champions: Hornbreaker Prince (Rage/Multistrike)
- Key cards: Imp generation, self-damage for power

**Awoken (Plants):**
- Core: Healing, Regen, Spikes
- Champions: Wyldenten (tanking), Sentient (damage)
- Key mechanic: Damage Shields, heal-based scaling

**Stygian Guard (Magic):**
- Core: Spell damage, Incant (spell triggers), Frostbite
- Champions: Tethys (incant), Siren (spell power)
- Key mechanic: Spell Weakness, freeze effects

**Umbra (Shadow):**
- Core: Gorge (consume units for power), Morsels
- Champions: Penumbra (gorge), Primordium (morsel)
- Key mechanic: Eating allies for stats, capacity management

**Melting Remnant (Wax):**
- Core: Burnout (die after X turns), Reform (resurrect)
- Champions: Rector Flicker (reform), Little Fade
- Key mechanic: Temporary powerful units, death triggers

### 6.3 Upgrade System

**Unit Upgrades:**
| Upgrade | Effect |
|---------|--------|
| Multistrike | +1 Multistrike |
| Largestone | +25 HP |
| Battlestone | +10 Attack |
| Quick | Acts before enemies |
| Endless | Returns to hand on death |

**Spell Upgrades:**
| Upgrade | Effect |
|---------|--------|
| -1 Ember | Reduce cost by 1 |
| +10 Magic Power | Increase damage/effect |
| Consume | Remove from deck after use |
| Holdover | Returns to hand each turn |
| Permafrost | Doesn't consume draw |

---

## 7. Inscryption Data

### 7.1 Cost Systems

```typescript
interface CardCost {
  type: 'blood' | 'bone' | 'energy' | 'mox' | 'free';
  amount: number;
  moxColor?: 'green' | 'orange' | 'blue';
}
```

**Blood Cost Rules:**
- Sacrifice X creatures to summon (X = blood cost)
- Blood is temporary, not stored
- Worthy Sacrifice sigil = 3 blood per sacrifice
- Many Lives = can sacrifice repeatedly

**Bone Cost Rules:**
- Gain 1 bone when any friendly creature dies
- Bones persist across turns until spent
- Bone King sigil = 4 bones on death

**Special Costs:**
- Cat: Can be sacrificed 9 times (Many Lives)
- Black Goat: 1 blood cost, worth 3 blood as sacrifice
- Child 13: Costs 13 bones but extremely powerful

### 7.2 Card Stats

**Act 1 Notable Cards:**
| Card | Cost | Attack | Health | Sigils |
|------|------|--------|--------|--------|
| Squirrel | Free | 0 | 1 | - |
| Stoat | 1 Blood | 1 | 3 | - |
| Wolf | 2 Blood | 3 | 2 | - |
| Grizzly | 3 Blood | 4 | 6 | - |
| Mantis God | 1 Blood | 1 | 1 | Trifurcated Strike |
| Ouroboros | 2 Blood | 1 | 1 | Unkillable (grows +1/+1) |
| Cockroach | 4 Bones | 1 | 1 | Unkillable |
| Black Goat | 1 Blood | 0 | 1 | Worthy Sacrifice |
| Cat | Free | 0 | 1 | Many Lives |
| Urayuli | 4 Blood | 7 | 7 | - |
| Adder | 2 Blood | 1 | 1 | Touch of Death |

### 7.3 Sigil Transfer Rules

- At Sacrificial Altar: destroy card → transfer sigil to another
- Card can have multiple sigils
- Some sigils have anti-synergies (Waterborne + Airborne)
- Death Cards inherit sigils from cards at time of death

---

## 8. Hades Boon System

### 8.1 God Domains

```typescript
interface God {
  name: string;
  domain: string;
  statusEffect: string;
  attackBoon: string;
  attackBonus: string;
}
```

| God | Domain | Status Effect | Attack Bonus (Common) |
|-----|--------|---------------|----------------------|
| Zeus | Lightning | Jolted (chain damage) | +10-20 flat damage |
| Poseidon | Water | Ruptured (move = damage) | +100% knockback damage |
| Athena | Wisdom | Exposed (backstab vulnerable) | +40% damage, deflect |
| Ares | War | Doom (delayed burst) | +50-60 Doom damage |
| Artemis | Hunt | Marked (crit vulnerable) | +20% damage, +15% crit |
| Aphrodite | Love | Weak (deal less damage) | +50% damage |
| Dionysus | Wine | Hangover (DoT stacks) | +4-5 Hangover/hit |
| Demeter | Winter | Chill (slow, shatter at 10) | +40% damage, +1 Chill |

### 8.2 Duo Boon Requirements & Effects

```typescript
interface DuoBoon {
  name: string;
  gods: [string, string];
  requirements: string[];
  effect: string;
}
```

**Top Tier Duo Boons:**

| Duo Boon | Gods | Requirements | Effect |
|----------|------|--------------|--------|
| Merciful End | Ares + Athena | Ares attack/special + Athena attack/special/dash | Doom triggers instantly on deflect |
| Heart Rend | Aphrodite + Artemis | Aphro attack/special + Arty attack/special | Crits deal +150% to Weak enemies |
| Hunting Blades | Ares + Artemis | Ares cast + Arty attack/special | Blade Rifts seek enemies |
| Cold Fusion | Demeter + Zeus | Demeter attack/special + Zeus attack/special | Jolted doesn't expire on attack |
| Ice Wine | Demeter + Dionysus | Demeter attack/special + Dionysus Trippy Shot | Festive Fog inflicts Chill |
| Sea Storm | Poseidon + Zeus | Poseidon attack/special + Zeus attack/special | Knockback causes lightning |
| Curse of Longing | Ares + Aphrodite | Ares Doom boon + Aphro attack/special | Weak enemies take Doom damage/1.5s |
| Deadly Reversal | Athena + Artemis | Athena attack/special/dash + Arty attack/special | +20% crit chance after deflect |
| Lightning Rod | Zeus + Artemis | Zeus attack-type boon + Arty cast | Bloodstones strike enemies every 1.5s |

### 8.3 Rarity Scaling

| Rarity | Multiplier (approx) |
|--------|---------------------|
| Common | 1.0× |
| Rare | 1.2-1.3× |
| Epic | 1.4-1.5× |
| Heroic | 1.6-1.8× |

**Rarity Upgrade Methods:**
- Eurydice's Ambrosia (one boon to next rarity)
- Chaos boons
- Well of Charon: Yarn of Ariadne (forces Legendary/Duo)
- Mirror: God's Legacy (+40% Duo/Legendary chance)

---

## 9. Economy & Progression

### 9.1 Slay the Spire Economy

**Gold Sources:**
| Source | Amount |
|--------|--------|
| Monster combat | 10-20 |
| Elite combat | 25-35 + relic |
| Boss combat | 95-105 + relic choice |
| ? room (gold) | 30-100 |
| Chests | 50-100 (small), 75-150 (medium), 100-200 (large) |

**Shop Prices:**
| Item | Price |
|------|-------|
| Card (Common) | 50-75 |
| Card (Uncommon) | 75-100 |
| Card (Rare) | 150-175 |
| Card Removal | 75 (+25 per removal) |
| Relic (Common) | 150 |
| Relic (Uncommon) | 250 |
| Relic (Rare) | 300 |
| Potion (Common) | 50 |
| Colorless Card | +50% |

**Scaling:**
- Card removal cost increases with each removal
- Membership Card relic: 50% off everything
- Courier relic: Shop always has cards from your class

### 9.2 Balatro Economy

**Base Economy:**
| Source | Amount |
|--------|--------|
| Win Small Blind | $3 base |
| Win Big Blind | $4 base |
| Win Boss Blind | $5 base |
| Interest | $1 per $5 held (max $5) |
| Extra hand unused | $1 each |
| Extra discard unused | $0.50 each |

**Shop Prices:**
| Item | Price Range |
|------|-------------|
| Joker (Common) | $2-6 |
| Joker (Uncommon) | $4-8 |
| Joker (Rare) | $7-10 |
| Tarot Pack | $4 |
| Planet Pack | $4 |
| Spectral Pack | $4 |
| Standard Pack | $4 |
| Buffoon Pack | $4 |
| Celestial Pack | $6 |

### 9.3 Ascension/Difficulty Scaling (Slay the Spire)

```typescript
interface AscensionLevel {
  level: number;
  modifier: string;
}
```

| Level | Cumulative Modifier |
|-------|---------------------|
| 1 | Elites spawn more often |
| 2 | Normal monsters deal ~10% more damage |
| 3 | Elites deal ~10% more damage |
| 4 | Bosses deal ~10% more damage |
| 5 | Post-boss heal: 100% → 75% |
| 6 | Start with Ascender's Bane curse |
| 7 | Normal monsters have more HP |
| 8 | Elites have more HP |
| 9 | Bosses have more HP |
| 10 | Lose "gain 100g" Neow option |
| 11 | Rest site: upgrade requires 2 rests |
| 12 | -4 starting Max HP |
| 13 | Bosses gain +50% more HP |
| 14 | Start with extra Strike card |
| 15 | Boss heals when you lose |
| 16 | Elites +50% HP |
| 17 | Normal monsters +50% HP |
| 18 | Seal and Blood Vial potion healing halved |
| 19 | Boss special modifiers |
| 20 | Double boss (fight 2 bosses) |

---

## 10. Enemy Design Patterns

### 10.1 Pattern Types

```typescript
enum EnemyPatternType {
  FIXED_SEQUENCE = 'fixed',    // Always same order
  WEIGHTED_RANDOM = 'weighted', // Probability-based
  CONDITIONAL = 'conditional',  // Based on game state
  SCALING = 'scaling'           // Gets stronger over time
}
```

**Fixed Sequence (Predictable):**
- Cultist: Buff → Attack → Attack → Attack...
- Slime Boss: Attack → Preparing → Attack → Preparing...

**Weighted Random (Probability):**
- Jaw Worm: 45% buff, 30% defend+attack, 25% attack
- Rules: Usually can't repeat same move 2-3×

**Conditional (Reactive):**
- Gremlin Nob: Uses Skull Bash if player used Skill
- Guardian: Switches modes based on damage taken

**Scaling (Urgency):**
- Cultist: +4 Strength each turn
- Lagavulin: Sleeps, then starts scaling
- Time Eater: Ends turn every 12 cards played

### 10.2 Boss Design Principles

**Phase Transitions:**
- Slime Boss: Splits at 50% HP into 2 smaller slimes
- Guardian: Alternates Offensive/Defensive mode
- Donu/Deca: One buffs, one attacks (kill order matters)

**Punish Mechanics:**
- Time Eater: Punishes playing many cards
- Heart: Punishes not killing fast (scales)
- Gremlin Nob: Punishes playing Skills

**Telegraphing:**
- Always show intent (except Runic Dome)
- Multi-turn setups visible (Hexaghost 6-turn cycle)
- Phase transitions predictable (HP thresholds)

### 10.3 Example Enemy Implementation

```typescript
interface Enemy {
  name: string;
  hp: { min: number; max: number };
  moves: Move[];
  pattern: PatternFunction;
  eliteOnly?: boolean;
  act: 1 | 2 | 3;
}

interface Move {
  name: string;
  intent: 'attack' | 'defend' | 'buff' | 'debuff' | 'unknown';
  damage?: number;
  hits?: number;
  block?: number;
  effect?: StatusApplication;
}

// Example: Jaw Worm
const jawWorm: Enemy = {
  name: "Jaw Worm",
  hp: { min: 40, max: 44 },
  moves: [
    { name: "Chomp", intent: "attack", damage: 11 },
    { name: "Thrash", intent: "attack", damage: 7, block: 5 },
    { name: "Bellow", intent: "buff", effect: { strength: 3, block: 6 } }
  ],
  pattern: (turn, lastMove) => {
    if (turn === 1) return "Chomp";
    // 45% Bellow, 30% Thrash, 25% Chomp (with restrictions)
    const weights = { Bellow: 45, Thrash: 30, Chomp: 25 };
    // Apply restrictions...
    return weightedRandom(weights);
  },
  act: 1
};
```

---

## 11. TypeScript Interfaces

### 11.1 Core Card Interface

```typescript
interface Card {
  id: string;
  name: string;
  description: string;
  type: CardType;
  rarity: CardRarity;
  cost: number | 'X';

  // Effects
  damage?: number;
  damageMultiplier?: number; // For Strength scaling
  hits?: number;
  block?: number;

  // Keywords
  keywords: CardKeyword[];

  // Status effects applied
  applyToEnemy?: StatusEffect[];
  applyToSelf?: StatusEffect[];

  // Upgrade data
  upgraded: boolean;
  upgradeEffect?: Partial<Card>;

  // Targeting
  targetType: 'single' | 'all' | 'random' | 'self' | 'none';
}

enum CardType {
  ATTACK = 'attack',
  SKILL = 'skill',
  POWER = 'power',
  STATUS = 'status',
  CURSE = 'curse'
}

enum CardRarity {
  STARTER = 'starter',
  COMMON = 'common',
  UNCOMMON = 'uncommon',
  RARE = 'rare',
  SPECIAL = 'special'
}

enum CardKeyword {
  EXHAUST = 'exhaust',
  ETHEREAL = 'ethereal',
  INNATE = 'innate',
  RETAIN = 'retain',
  UNPLAYABLE = 'unplayable'
}
```

### 11.2 Status Effect Interface

```typescript
interface StatusEffect {
  type: StatusType;
  amount: number;
  duration?: number; // turns, or undefined for permanent
  source?: string;
}

enum StatusType {
  // Debuffs
  VULNERABLE = 'vulnerable',
  WEAK = 'weak',
  FRAIL = 'frail',
  POISON = 'poison',

  // Buffs
  STRENGTH = 'strength',
  DEXTERITY = 'dexterity',
  ARTIFACT = 'artifact',
  INTANGIBLE = 'intangible',
  BLOCK = 'block',
  THORNS = 'thorns',
  METALLICIZE = 'metallicize',
  PLATED_ARMOR = 'plated_armor',
  BARRICADE = 'barricade',

  // Special
  RITUAL = 'ritual', // Gain X strength/turn
  RAGE = 'rage'
}

// Status effect behavior configuration
const STATUS_CONFIG: Record<StatusType, StatusBehavior> = {
  [StatusType.VULNERABLE]: {
    stackType: 'duration',
    decrementTiming: 'turn_end',
    effect: (target, amount) => target.damageTakenMultiplier *= 1.5
  },
  [StatusType.POISON]: {
    stackType: 'intensity',
    decrementTiming: 'after_damage',
    tickTiming: 'turn_start',
    effect: (target, amount) => target.takeDamage(amount, { ignoreBlock: true })
  },
  [StatusType.STRENGTH]: {
    stackType: 'intensity',
    decrementTiming: 'never',
    effect: (target, amount) => target.attackBonus += amount
  }
  // ... etc
};
```

### 11.3 Relic Interface

```typescript
interface Relic {
  id: string;
  name: string;
  description: string;
  rarity: RelicRarity;

  // Trigger conditions
  trigger: RelicTrigger;

  // Effect
  effect: RelicEffect;

  // For counter-based relics
  counter?: {
    max: number;
    current: number;
    resetOn: 'trigger' | 'combat_end' | 'never';
  };

  // Character restriction
  characterOnly?: string;
}

enum RelicRarity {
  STARTER = 'starter',
  COMMON = 'common',
  UNCOMMON = 'uncommon',
  RARE = 'rare',
  BOSS = 'boss',
  EVENT = 'event',
  SHOP = 'shop'
}

enum RelicTrigger {
  COMBAT_START = 'combat_start',
  TURN_START = 'turn_start',
  TURN_END = 'turn_end',
  ON_ATTACK = 'on_attack',
  ON_CARD_PLAY = 'on_card_play',
  ON_CARD_EXHAUST = 'on_card_exhaust',
  ON_DAMAGE_TAKEN = 'on_damage_taken',
  ON_ENEMY_DEATH = 'on_enemy_death',
  PASSIVE = 'passive',
  ON_REST = 'on_rest',
  ON_CHEST_OPEN = 'on_chest_open'
}

// Example relic implementations
const RELICS: Relic[] = [
  {
    id: 'pen_nib',
    name: 'Pen Nib',
    description: 'Every 10th Attack deals double damage.',
    rarity: RelicRarity.UNCOMMON,
    trigger: RelicTrigger.ON_ATTACK,
    effect: { type: 'damage_multiplier', value: 2 },
    counter: { max: 10, current: 0, resetOn: 'trigger' }
  },
  {
    id: 'kunai',
    name: 'Kunai',
    description: 'Every 3 Attacks played, gain 1 Dexterity.',
    rarity: RelicRarity.UNCOMMON,
    trigger: RelicTrigger.ON_ATTACK,
    effect: { type: 'apply_status', status: StatusType.DEXTERITY, amount: 1 },
    counter: { max: 3, current: 0, resetOn: 'trigger' }
  },
  {
    id: 'snecko_skull',
    name: 'Snecko Skull',
    description: 'Whenever you apply Poison, apply 1 additional Poison.',
    rarity: RelicRarity.COMMON,
    trigger: RelicTrigger.ON_CARD_PLAY,
    effect: { type: 'modify_poison', bonus: 1 },
    characterOnly: 'silent'
  }
];
```

### 11.4 Combat State Interface

```typescript
interface CombatState {
  player: CombatantState;
  enemies: EnemyState[];

  turn: number;
  phase: CombatPhase;

  drawPile: Card[];
  hand: Card[];
  discardPile: Card[];
  exhaustPile: Card[];

  energy: number;
  maxEnergy: number;

  // Combat-wide effects
  relicCounters: Map<string, number>;
  temporaryEffects: TemporaryEffect[];
}

interface CombatantState {
  hp: number;
  maxHp: number;
  block: number;
  statusEffects: Map<StatusType, StatusEffect>;
}

interface EnemyState extends CombatantState {
  id: string;
  name: string;
  intent: EnemyIntent;
  pattern: EnemyPattern;
  moveHistory: string[];
}

interface EnemyIntent {
  type: 'attack' | 'defend' | 'buff' | 'debuff' | 'unknown';
  damage?: number;
  hits?: number;
  block?: number;
}

enum CombatPhase {
  PLAYER_TURN_START = 'player_turn_start',
  PLAYER_TURN = 'player_turn',
  PLAYER_TURN_END = 'player_turn_end',
  ENEMY_TURN_START = 'enemy_turn_start',
  ENEMY_TURN = 'enemy_turn',
  ENEMY_TURN_END = 'enemy_turn_end'
}
```

### 11.5 Damage Calculation Function

```typescript
function calculateDamage(
  baseDamage: number,
  attacker: CombatantState,
  defender: CombatantState,
  options: DamageOptions = {}
): number {
  let damage = baseDamage;

  // 1. Apply Strength (per hit)
  const strength = attacker.statusEffects.get(StatusType.STRENGTH)?.amount ?? 0;
  damage += strength;

  // 2. Apply Strength multiplier (Heavy Blade)
  if (options.strengthMultiplier) {
    damage += strength * (options.strengthMultiplier - 1);
  }

  // 3. Apply Weak (attacker debuff)
  if (attacker.statusEffects.has(StatusType.WEAK)) {
    damage = Math.floor(damage * 0.75);
  }

  // 4. Apply Vulnerable (defender debuff)
  if (defender.statusEffects.has(StatusType.VULNERABLE)) {
    const multiplier = options.vulnerableMultiplier ?? 1.5;
    damage = Math.floor(damage * multiplier);
  }

  // 5. Apply other multipliers
  if (options.multiplier) {
    damage = Math.floor(damage * options.multiplier);
  }

  // 6. Minimum damage is 0
  return Math.max(0, damage);
}

interface DamageOptions {
  strengthMultiplier?: number;  // Heavy Blade: 3 or 5
  vulnerableMultiplier?: number; // Paper Phrog: 1.75
  multiplier?: number;  // Pen Nib: 2
  ignoreBlock?: boolean; // Poison damage
}
```

---

## Quick Reference Tables

### Status Effect Quick Lookup

| Status | Type | Stacks | Expires | Effect |
|--------|------|--------|---------|--------|
| Vulnerable | Debuff | Duration | Turn end | +50% damage taken |
| Weak | Debuff | Duration | Turn end | -25% damage dealt |
| Frail | Debuff | Duration | Turn end | -25% block from cards |
| Poison | Debuff | Intensity | When 0 | Take stacks dmg, -1 |
| Strength | Buff | Intensity | Never | +1 damage/attack |
| Dexterity | Buff | Intensity | Never | +1 block/card |
| Artifact | Buff | Charges | On use | Block 1 debuff |
| Intangible | Buff | Duration | Turn end | All damage → 1 |
| Thorns | Buff | Intensity | Combat end | Deal X when attacked |
| Rage | Buff | Intensity | Combat end | +X attack |
| Multistrike | Buff | Intensity | Combat end | +X attacks |

### Rarity Drop Rates

| Game | Common | Uncommon | Rare | Legendary |
|------|--------|----------|------|-----------|
| Slay the Spire | ~60% | ~37% | ~3% | N/A |
| Balatro Jokers | 70% | 25% | 5% | 0.3% (Spectral) |
| Monster Train | 60% | 30% | 10% | N/A |

### Energy Systems Comparison

| Game | Start | Per Turn | Max | Special |
|------|-------|----------|-----|---------|
| Slay the Spire | 3 | 3 | 5+ | X-cost cards |
| Monster Train | 3 | +1/turn | 10 | Ember |
| Inscryption | N/A | N/A | N/A | Blood/Bone |
| Balatro | N/A | N/A | N/A | Hands/Discards |

---

## Sources

- [Slay the Spire Wiki](https://slaythespire.wiki.gg/)
- [Balatro Wiki](https://balatrowiki.org/)
- [Monster Train Wiki](https://monster-train.fandom.com/)
- [Inscryption Wiki](https://inscryption.fandom.com/)
- [Hades Wiki](https://hades.fandom.com/)
- Various Steam Community Guides
- Game source code analysis
