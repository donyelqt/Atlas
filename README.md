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

**Backend**: FastAPI, Poetry, tree-sitter, NetworkX, LangGraph  
**Frontend**: Next.js 14, TypeScript, Tailwind CSS, React Flow (XYFlow), Zustand, TanStack Query  
**AI**: OpenAI / Anthropic / Gemini

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
