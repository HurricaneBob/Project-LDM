# LDM — Leadership Development Mentor

A ChatGPT-style leadership simulation. Users describe any real situation they're sitting with and an AI team of 5 personas responds as their team. Sessions accumulate in a sidebar; an Analysis view aggregates a leadership signal across all sessions.

> Phase 1 (current): onboarding → chat with text input → session history → analysis.
> Phase 2: voice (Web Speech API).
> Phase 3: real auth.

## Quick start

```bash
npm install
npm run dev          # → http://localhost:5173
```

Requires a running Flask backend. Copy `.env.example` to `.env`:

```bash
cp .env.example .env
# VITE_API_BASE_URL=http://localhost:5000
```

1. Start the backend: `.\run.ps1` from the repo root.
2. Start the frontend: `npm run dev`.

If `VITE_API_BASE_URL` is missing, chat calls fail immediately with a clear error (no mock fallback).

## For the backend team

You implement **one** endpoint. The frontend mock in `src/lib/api.js` documents the exact contract.

### `POST /api/chat`

**Request body:**

```ts
{
  sessionId: string | null,   // null on the first message of a new session
  message: string,            // the user's latest message
  history: Array<{
    role: 'user' | 'persona' | 'system',
    personaId?: 'commander' | 'facilitator' | 'strategist' | 'supporter' | 'adaptive',
    content: string,
    timestamp: number
  }>
}
```

**Response:**

```ts
{
  sessionId: string,          // echo if given, else mint a new one
  sessionTitle?: string,      // only on first reply of a new session
  personaResponses: Array<{
    personaId: 'commander' | 'facilitator' | 'strategist' | 'supporter' | 'adaptive',
    message: string
  }>,
  parameterDeltas: { [parameterName: string]: number }
}
```

**Notes:**
- `personaResponses` is typically 1–3 personas reacting to the user's message. The frontend renders them in the order returned.
- `parameterDeltas` keys must come from the set in `src/data/personas.js` → `allParameters`.
- `sessionTitle` should be a short 4–8 word summary of the user's first message. Required on session creation.
- The frontend persists session history locally; the backend can be stateless if you prefer, or use `sessionId` to load server-side state.

The mock in `src/lib/api.js` is a good reference for response shape and what kinds of messages each persona produces.

## Stack

- **Vite 5** — build tool
- **React 18** — UI
- **React Router 6** — routing
- **Tailwind 3** — styling with CSS-variable theming
- **lucide-react** — icons
- **Pretendard** — font (CDN, loaded in `index.html`)

No other runtime deps. Don't add an LLM SDK to the frontend — all model calls go through the backend.

## Project structure

```
src/
├── main.jsx                          Entry — wraps providers
├── App.jsx                           Routes
├── index.css                         Design tokens (CSS variables)
├── components/
│   ├── AppLayout.jsx                 Sidebar + <Outlet/> for chat/history/analysis
│   ├── Sidebar.jsx                   "+ Add Scenario", session list, nav, user chip
│   ├── PersonaPortrait.jsx           Circular portrait + speaking glow
│   ├── OnboardingLayout.jsx          Onboarding chrome
│   ├── ProgressBar.jsx               Onboarding step bar
│   ├── Button.jsx                    4-variant button (hero/primary/secondary/ghost)
│   ├── Input.jsx                     Pill-shaped text input
│   ├── PillButton.jsx                Selection pill (single / multi)
│   └── PlaceholderHalftone.jsx       (legacy fallback, currently unused)
├── screens/
│   ├── Login.jsx                     Stub — navigates to onboarding (Phase 3)
│   ├── Chat.jsx                      Main chat screen (3 visual states)
│   ├── History.jsx                   Session card grid
│   ├── Analysis.jsx                  Leadership type + parameter bars
│   └── onboarding/
│       ├── Welcome.jsx
│       ├── Profile.jsx
│       ├── AboutYou.jsx
│       └── Ready.jsx                 Handoff to /
├── context/
│   ├── OnboardingContext.jsx         Form state (localStorage: ldm_onboarding)
│   └── SessionContext.jsx            Sessions + parameter scores (localStorage: ldm_sessions)
├── data/
│   ├── personas.js                   5 personas + allParameters + onboarding options
│   └── exampleScenarios.js           Reference scenarios (unused in Phase 1)
└── lib/
    └── api.js                        chat() — real fetch or mock
```

## The 5 personas

| ID            | Name              | Essence       | Color var                       |
| ------------- | ----------------- | ------------- | ------------------------------- |
| `commander`   | The Commander     | DECISIVE      | `--color-persona-commander`     |
| `facilitator` | The Facilitator   | COLLABORATIVE | `--color-persona-facilitator`   |
| `strategist`  | The Strategist    | ANALYTICAL    | `--color-persona-strategist`    |
| `supporter`   | The Supporter     | EMPATHETIC    | `--color-persona-supporter`     |
| `adaptive`    | The Adaptive      | FLEXIBLE      | `--color-persona-adaptive`      |

Each persona evaluates a subset of leadership parameters (see `evaluates` in `src/data/personas.js`). The union of those subsets is `allParameters`, which the Analysis view aggregates.

## Persona portrait images

Drop 1024×1024 PNGs in `public/personas/` using the persona IDs as filenames:

```
public/personas/commander.png
public/personas/facilitator.png
public/personas/strategist.png
public/personas/supporter.png
public/personas/adaptive.png
```

`PersonaPortrait` picks them up automatically. If a file is missing, it falls back to an initial-letter chip with a radial glow in the persona color.

## Design system

All design tokens live in `src/index.css` under `:root`. Tailwind reads them via `tailwind.config.js`. Change a CSS variable — every component updates instantly.

Key tokens:
- `--color-primary` — Deep Violet `#A855F7`
- `--color-bg` / `--color-surface` / `--color-surface-hi` — dark neutrals
- `--color-persona-*` — 5 persona signature colors

Button hierarchy (`src/components/Button.jsx`):
1. **hero** — large white pill + glow (1 per page)
2. **primary** — violet pill + glow (standard CTA)
3. **secondary** — white pill, no glow
4. **ghost** — transparent + border (back, skip)

## State + persistence

Two contexts. Both auto-persist to `localStorage`.

| Context             | Key               | Holds                                                    |
| ------------------- | ----------------- | -------------------------------------------------------- |
| `OnboardingContext` | `ldm_onboarding`  | `{ name, role, pressureResponse, conflictResponse, growthAreas }` |
| `SessionContext`    | `ldm_sessions`    | `{ sessions[], currentSessionId, parameterScores }`      |

Clear localStorage to reset.

## Scripts

```bash
npm run dev          # vite dev server
npm run build        # vite build → dist/
npm run preview      # serve dist/ locally
```

## Deploy

Push to GitHub, then connect on [Vercel](https://vercel.com) — auto-detects Vite. Set `VITE_API_BASE_URL` as an env var pointing at the backend.
