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

### Graph Database
- **Neo4j 5 Community Edition** — persisted adjacency graph for cross-session queries (natural-language search, shortest path, node degree, entry-point discovery)
- **Python driver**: `neo4j` async driver
- Optional APOC plugin (installed in compose) for variable-length traversal

### Container / Infrastructure
- **Docker** — multi-stage builds for backend and frontend
- **Docker Compose** — orchestrates API, frontend, Redis, and Neo4j
- **Redis** — broker (Celery), cache, and result backend

## API Endpoints

### Core
- `POST /api/analyze` — Analyze a repository
- `GET /api/summary/{id}` — Get analysis summary
- `GET /api/graph/{id}` — Get architecture graph (in-memory)
- `POST /api/chat` — Ask repository questions

### Graph Search (Neo4j)
- `POST /api/neo4j/sync/{analysis_id}` — Sync graph to Neo4j (run once per analysis)
- `GET /api/neo4j/graph/{analysis_id}` — Fetch persisted graph from Neo4j
- `GET /api/neo4j/entry-points/{analysis_id}` — Find entry-point files/modules
- `GET /api/neo4j/related/{analysis_id}/{node_id}` — Get connected nodes within N hops
- `GET /api/neo4j/path/{analysis_id}?source=...&target=...` — Shortest path between nodes

## Graph Search Examples

### Find all nodes mentioning "auth" in a large codebase
```bash
curl -X POST "http://localhost:8000/api/neo4j/search/{analysis_id}" \
  -H "Content-Type: application/json" \
  -d '{"query":"auth","hops":3}'
```

### Find everything connected to a specific file
```bash
curl "http://localhost:8000/api/neo4j/related/{analysis_id}/app/services/auth.py?hops=2"
```

### Shortest path from API to database
```bash
curl "http://localhost:8000/api/neo4j/path/{analysis_id}?source=api/routes/users.py&target=models/user.py"
```

### Find entry points
```bash
curl "http://localhost:8000/api/neo4j/entry-points/{analysis_id}?limit=20"
```

### Raw Cypher (via the backend `run_query` helper)
```cypher
MATCH (r:Repository {id: '<analysis_id>'})-[:HAS_NODE]->(n:Node)
WHERE n.label CONTAINS 'payment'
RETURN n
```

### Find everything connected to a specific file
```bash
curl "http://localhost:8000/api/neo4j/related/{analysis_id}/app/services/auth.py?hops=2"
```

### Shortest path from API to database
```bash
curl "http://localhost:8000/api/neo4j/path/{analysis_id}?source=api/routes/users.py&target=models/user.py"
```

### Raw Cypher (via the Chat agent)
```
MATCH (r:Repository {id: '<analysis_id>'})-[:HAS_NODE]->(n:Node)
WHERE n.label CONTAINS 'payment'
RETURN n
```

## Features

- 🗺️ Interactive architecture graph
- 🔎 Neo4j-backed graph search for large/undocumented repos
- 💬 Repository-specific AI chat
- 📋 AI-generated onboarding plans
- 🔍 Framework and language detection

## Supported Languages

Python, JavaScript, TypeScript, Go, Rust, Java, Ruby, PHP, C#, C++, and more.
