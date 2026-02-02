# Building a Roguelike Deck-Builder with Claude Code

This document summarizes a Claude Code session where we built and deployed a full-stack web game.

## What We Built

A **Slay the Spire-style roguelike deck-builder** with:
- **Backend:** Python + FastAPI (REST API)
- **Frontend:** React + TypeScript + Framer Motion animations
- **Deployment:** Render (backend) + Vercel (frontend)

**Live URL:** https://roguelike-deckbuilder.vercel.app

---

## Session Workflow

### 1. Planning & Exploration

Claude first explored the existing Python game engine:
```
"Explore the codebase at /Users/stevenqu/rogue_project to understand the existing Python game engine structure..."
```

### 2. Parallel Task Execution

Claude spawned **5 agents in parallel** to work on different parts simultaneously:
- FastAPI backend API
- React frontend setup
- TypeScript types & API client
- Combat UI components
- Map UI components

This dramatically sped up development.

### 3. Iterative Bug Fixing

When issues arose (blank page after selecting character), Claude:
1. Identified the API response format mismatch (snake_case vs camelCase)
2. Created transform functions in the API client
3. Fixed component prop passing

### 4. Deployment

**Setting up GitHub:**
```bash
# Claude ran these commands:
git init
git add .
git commit -m "Initial commit"
gh auth login --web  # Opens browser for GitHub auth
git push -u origin main
```

**Deploying to Render (backend):**
- Created `app.py` entry point for Render to find FastAPI
- Created `render.yaml` with build/start commands

**Deploying to Vercel (frontend):**
- Set Root Directory to `frontend`
- Set Framework Preset to `Vite`
- Added environment variable: `VITE_API_URL=https://roguelike-deckbuilder.onrender.com/api`

### 5. Fixing Build Errors

TypeScript errors in production build were fixed by:
- Adding proper types to Framer Motion variants: `Record<string, any>`
- Removing unused imports

---

## Useful Claude Code Patterns

### Ask Claude to explore first
```
"Explore the codebase to understand how X works"
```

### Run tasks in parallel
```
"Spawn multiple agents to work on these tasks in parallel"
```

### Fix and iterate
When something breaks, share the error message or screenshot. Claude will diagnose and fix.

### Deploy with guidance
Claude can run git commands, but needs your interaction for:
- GitHub authentication (opens browser)
- Vercel/Render account setup (you click through UI)

---

## Key Commands Used

```bash
# Install dependencies
pip install fastapi uvicorn pydantic
npm install framer-motion zustand

# Run locally
uvicorn src.api.main:app --reload --port 8000  # Backend
npm run dev                                      # Frontend

# Deploy (after setup)
git add . && git commit -m "message" && git push
# Vercel & Render auto-deploy on push!
```

---

## Project Structure

```
roguelike-deckbuilder/
├── src/                    # Python game engine
│   ├── api/                # FastAPI endpoints
│   │   ├── main.py         # API routes
│   │   └── schemas.py      # Pydantic models
│   ├── combat/             # Combat system
│   ├── entities/           # Player, Enemy, Card
│   └── map/                # Map generation
├── frontend/               # React app
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── api/client.ts   # API client
│   │   ├── store/          # Zustand state
│   │   └── types/          # TypeScript types
│   └── package.json
├── app.py                  # Entry point for Render
├── render.yaml             # Render config
└── requirements.txt        # Python dependencies
```

---

## Tips for Using Claude Code

1. **Be specific** - "Fix the TypeScript error in Card.tsx" is better than "fix the error"

2. **Share context** - Screenshots, error messages, and URLs help Claude understand the problem

3. **Let Claude explore** - For unfamiliar codebases, ask Claude to explore first before making changes

4. **Use parallel agents** - For large tasks, Claude can spawn multiple agents to work simultaneously

5. **Iterate** - Don't expect perfection on first try. Review, test, and ask for fixes.

6. **Trust but verify** - Claude will run commands and make changes. Review the output.

---

## Links

- **Live Game:** https://roguelike-deckbuilder.vercel.app
- **GitHub Repo:** https://github.com/Staiven/roguelike-deckbuilder
- **Render Dashboard:** https://dashboard.render.com
- **Vercel Dashboard:** https://vercel.com/dashboard
