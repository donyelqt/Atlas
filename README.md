# Atlas

AI-powered repository intelligence platform that transforms GitHub repositories into interactive architecture maps.

## Quick Start

```bash
# Clone and enter
git clone https://github.com/donyelqt/Atlas.git
cd Atlas

# Backend
cd backend
cp .env.example .env   # add your API keys
poetry install
poetry run uvicorn app.app:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## Tech Stack

### Backend
| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| Framework | FastAPI 0.111 |
| ASGI Server | Uvicorn (with `standard` extras) |
| Package Manager | Poetry + `requirements.txt` fallback |
| Configuration | Pydantic v2 + `pydantic-settings` (`.env`) |
| GitHub API | `httpx` (async REST — no `git clone` needed) |
| Code Parsing | `tree-sitter` + `tree-sitter-languages` |
| Graph Processing | `networkx` |
| Repo Access | GitHub REST API (primary), GitPython (fallback) |
| LLM Clients | `openai`, `anthropic`, `google-generativeai` |
| Caching / Queue | `redis` + `celery[redis]` |
| Retries | `tenacity` |
| Env Management | `python-dotenv` |
| Async File I/O | `aiofiles` |
| Testing | `pytest` + `pytest-asyncio` |
| Linting | `ruff` |
| Type Checking | `mypy` (strict) |

### Frontend
| Layer | Technology |
|-------|-----------|
| Framework | Next.js 14 (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS v3 + PostCSS + Autoprefixer |
| Graph Visualization | `@xyflow/react` (React Flow v12) |
| State Management | Zustand |
| Data Fetching | TanStack Query (React Query v5) |
| Icons | `lucide-react` |
| Utilities | `clsx` + `tailwind-merge` |
| Linting | ESLint |

### AI / LLM Providers
- **OpenAI** — `gpt-4o` (default)
- **Anthropic** — Claude models
- **Google** — Gemini models

### Container / Infrastructure
- **Docker** — multi-stage builds for backend and frontend
- **Docker Compose** — orchestrates API, frontend, and Redis
- **Redis** — broker (Celery), cache, and result backend

## API Endpoints

- `POST /api/analyze` — Analyze a repository
- `GET /api/summary/{id}` — Get analysis summary
- `GET /api/graph/{id}` — Get architecture graph
- `POST /api/chat` — Ask repository questions

## Features

- 🗺️ Interactive architecture graph
- 💬 Repository-specific AI chat
- 📋 AI-generated onboarding plans
- 🔍 Framework and language detection

## Supported Languages

Python, JavaScript, TypeScript, Go, Rust, Java, Ruby, PHP, C#, C++, and more.
