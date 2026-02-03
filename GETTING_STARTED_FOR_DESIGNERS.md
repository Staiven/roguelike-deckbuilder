# Getting Started - For Game Designers

Welcome! This guide will help you set up the project and use Claude Code to design and improve the game - **no coding experience required**.

---

## What is This Project?

A **Slay the Spire-style roguelike deck-builder** game with:
- Turn-based card combat
- Multiple characters with unique cards
- Enemies with attack patterns
- Items/relics that modify gameplay
- A map to navigate through

**Live game:** https://roguelike-deckbuilder.vercel.app

---

## Step 1: Install Required Tools

### Install VS Code (optional but helpful)
Download from: https://code.visualstudio.com/

### Install Claude Code
Open Terminal (Mac) or Command Prompt (Windows) and run:

```bash
npm install -g @anthropic-ai/claude-code
```

If you don't have npm, first install Node.js from: https://nodejs.org/

### Get the Project
```bash
git clone https://github.com/Staiven/roguelike-deckbuilder.git
cd roguelike-deckbuilder
```

---

## Step 2: Start Claude Code

In your terminal, inside the project folder, run:

```bash
claude
```

Claude will start and you can talk to it in plain English!

---

## Step 3: How to Talk to Claude (Examples)

### Asking Questions
```
"What cards does the Warrior have?"
"How does poison work in this game?"
"Show me all the enemies in Act 1"
"What relics are implemented?"
```

### Designing New Content
```
"Add a new card called 'Fireball' that costs 2 energy and deals 15 damage to all enemies"

"Create a new enemy called 'Goblin' with 30 HP that alternates between attacking for 8 damage and buffing itself with 2 strength"

"Add a relic called 'Vampire Fang' that heals 2 HP whenever you play an attack card"
```

### Balancing & Tweaking
```
"Make the 'Strike' card deal 8 damage instead of 6"
"Reduce the Slime enemy's health from 50 to 40"
"Change the poison mechanic so it deals damage at the end of turn instead of start"
```

### Describing Mechanics
```
"I want a 'Burn' status effect that works like this: enemies take 3 damage per stack at the end of their turn, but stacks don't decrease - they stay until combat ends"

"Add a 'Rage' mechanic where the player gains +1 damage for every 10% HP they're missing"
```

### World & Story
```
"The game is set in a corrupted forest. Update the enemy names and descriptions to fit this theme"

"Add flavor text to all the Warrior's cards that references their backstory as a fallen knight"
```

---

## Step 4: Useful Commands

| Command | What it does |
|---------|--------------|
| `/help` | Show help |
| `/clear` | Clear conversation |
| `/cost` | Show token usage |
| `Ctrl+C` | Cancel current action |
| `exit` | Close Claude Code |

---

## Project Structure (What's Where)

```
roguelike-deckbuilder/
├── src/                    # Game logic (Python)
│   ├── entities/           # Player, Enemy, Card definitions
│   ├── combat/             # Combat system
│   └── map/                # Map generation
├── frontend/               # Visual interface (React)
│   └── src/components/     # UI components
├── DECKBUILDER_MECHANICS_RESEARCH.md      # Summary of mechanics from other games
├── DECKBUILDER_IMPLEMENTATION_REFERENCE.md # Detailed technical reference
└── this file
```

---

## Design Resources

### Research Documents
Two files contain research on mechanics from games like Slay the Spire, Balatro, Monster Train:

1. **DECKBUILDER_MECHANICS_RESEARCH.md** - High-level overview of cool mechanics
2. **DECKBUILDER_IMPLEMENTATION_REFERENCE.md** - Detailed numbers and formulas

Ask Claude about them:
```
"Summarize the cool mechanics from the research document"
"What status effects do other deckbuilders use?"
"How does Balatro's scoring system work?"
```

### Proposing New Features

When describing a new feature, include:

**For Cards:**
- Name
- Energy cost (0-3 typically)
- Card type (Attack, Skill, Power)
- Effect (damage, block, status effects)
- Any keywords (Exhaust, Ethereal, etc.)
- Which character it belongs to

**For Enemies:**
- Name
- Health range
- Attack pattern (what they do each turn)
- Any special abilities

**For Relics/Items:**
- Name
- When it triggers
- What it does
- Any downside?

---

## Example Design Session

```
You: "I want to add a new character called the Pyromancer who focuses on burn damage"

Claude: "I'll create a Pyromancer character. What cards should they start with?"

You: "They should have:
- Ember (0 cost): Deal 4 damage, apply 2 Burn
- Flame Shield (1 cost): Gain 5 block, enemies that attack you gain 1 Burn
- Ignite (1 cost): Deal 3 damage to ALL enemies, apply 1 Burn to ALL"

Claude: [Creates the character and cards]

You: "Now add a unique relic for them called 'Molten Core' that makes Burn deal 1 extra damage"

Claude: [Adds the relic]

You: "Let's test it - run the game locally"

Claude: [Starts the dev server so you can test]
```

---

## Tips for Working with Claude

1. **Be specific** - "Add a card that deals 10 damage" is better than "add a damage card"

2. **Describe behavior** - "When the player plays 3 attacks in one turn, gain 5 block" is clear

3. **Reference other games** - "Make it work like Slay the Spire's Poison" is helpful

4. **Ask Claude to explain** - If you're not sure how something works, just ask!

5. **Test changes** - After Claude makes changes, ask it to run the game so you can test

6. **Iterate** - "That's too strong, reduce the damage to 8" is totally fine

---

## Need Help?

Ask Claude:
```
"I'm stuck, what can I do with this project?"
"Show me what features are already implemented"
"What would be a good next feature to add?"
```

Or reach out to Steven!

---

Happy designing! 🎮
