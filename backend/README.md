# InteGrow — Backend

This folder contains the FastAPI backend for InteGrow (Phase 0 foundation).
The backend provides authentication, project management APIs, GitHub and Git agents, and integrates with Supabase for storage.

## Quick overview
- Framework: FastAPI (Python 3.11+ / 3.12 tested)
- Server: Uvicorn
- Database: Supabase (Postgres)
- Auth: GitHub OAuth (planned)
- Agents: PyGithub + GitPython

## Prerequisites
- Python 3.11+ (3.12 is supported)
- Git
- A Supabase project (for dev/test) — URL + anon/service keys
- (Optional) Redis for session/blacklist

## Setup (Windows PowerShell)
1. Open PowerShell and navigate to the `backend` folder.

2. Create (if not already created) and activate the virtual environment:

```powershell
python -m venv integrow_env
.\integrow_env\Scripts\Activate.ps1
```

3. Upgrade pip and install requirements:

```powershell
python -m pip install --upgrade pip

# Install production dependencies
pip install -r requirements.txt

# Install testing dependencies (for running unit tests)
pip install -r requirements-test.txt
```

4. Generate a `.env` file (secrets generator). This script will create a `.env` file from `.env.example` and fill in secure secrets (JWT + Fernet key).

```powershell
python utils/setup_env.py
```

After running the script, open `.env` and update the following values with your Supabase / GitHub credentials:
- `SUPABASE_URL` (should be the HTTP API url, e.g. `https://<project>.supabase.co`)
- `SUPABASE_KEY` (anon/public key)
- `SUPABASE_SERVICE_KEY` (service role key)
- `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET`
- Optionally adjust `PROJECTS_BASE_DIR` and other vars

> Note: Do NOT commit your `.env` to version control.

## Verify Supabase connection (quick)
A simple connection test script is provided:

```powershell
python tests/test_connection.py
```

This will assert the client can connect and will show a helpful message if tables are not yet created.

## Verify GitHub OAuth Configuration
Test that your GitHub OAuth credentials are properly configured:

```powershell
python tests/test_github_oauth.py
```

This will verify your `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` are set correctly.

## Database schema
A ready-to-run SQL file is available at `schema.sql`. To setup the database tables and RLS policies, open the Supabase Dashboard > SQL Editor and run the contents of `schema.sql`.

Steps:
1. Open Supabase project dashboard
2. Go to SQL Editor
3. Copy & paste `schema.sql`, then run

After schema setup you can re-run `python tests/test_connection.py` or run `python tests/test_database.py` to exercise basic queries.

## Run the development server
Once `.env` is configured and required tables exist, start the FastAPI server:

```powershell
# from backend/
.\integrow_env\Scripts\activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- API docs: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── integrow_env/           # Python virtual environment
├── main.py                 # FastAPI app entry point
├── config.py              # Environment configuration (Pydantic)
├── dependencies.py        # Auth dependencies (JWT validation)
├── requirements.txt       # Python dependencies
├── schema.sql            # Database schema for Supabase
├── .env                  # Environment variables (DO NOT COMMIT)
├── .env.example          # Template for .env
├── .gitignore            # Git exclusions
├── README.md             # This file
├── api/                  # API route handlers
│   ├── __init__.py
│   ├── auth_router.py    # GitHub OAuth endpoints
│   ├── project_router.py # Project CRUD endpoints
│   ├── requirements_router.py  # Requirements analysis endpoints
│   ├── user_stories_router.py  # User stories endpoints
│   └── user_router.py    # User profile endpoints
├── agents/               # Modular AI agents
│   ├── __init__.py       # Package exports with backward compatibility
│   ├── requirements/     # Requirement analysis agents
│   │   ├── __init__.py
│   │   ├── parser_agent.py        # Entity extraction (NLP)
│   │   ├── ambiguity_agent.py     # Ambiguity detection
│   │   ├── completeness_agent.py  # Completeness checking
│   │   ├── ethics_agent.py        # Ethics auditing
│   │   └── orchestrator_agent.py  # Workflow coordination
│   ├── user_stories/     # User story generation
│   │   ├── __init__.py
│   │   ├── user_story_agent.py       # Story generation
│   │   └── story_refinement_agent.py # Story refinement
│   └── integration/      # External integrations
│       ├── __init__.py
│       ├── git_agent.py      # Local Git operations
│       └── github_agent.py   # GitHub API operations
├── models/               # Pydantic data models
│   ├── __init__.py
│   ├── user.py          # User models
│   ├── project.py       # Project models
│   └── requirement.py   # Requirement models
├── services/            # Business logic layer
│   ├── __init__.py
│   ├── supabase_service.py  # Database operations
│   ├── encryption.py        # Token encryption
│   ├── llm_service.py       # LLM provider management
│   └── websocket_service.py # WebSocket chat service
├── workflows/           # Analysis workflows
│   ├── __init__.py
│   └── analysis_workflow.py  # Requirement analysis workflow
├── tests/               # Test scripts
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
└── utils/               # Utility scripts
    ├── __init__.py
    └── setup_env.py     # .env file generator
```

## Useful scripts
- `utils/setup_env.py` — generate `.env` with secure secrets
- `tests/test_connection.py` — minimal Supabase connection test
- `tests/test_github_oauth.py` — verify GitHub OAuth credentials
- `tests/test_database.py` — database schema verification
- `schema.sql` — SQL schema and RLS policies to run in Supabase SQL Editor

## Development checklist (Phase 0)
- [x] Project skeleton and virtualenv
- [x] Requirements installed
- [x] Supabase client wired
- [x] Config + `.env` generator
- [x] Basic FastAPI app and routers scaffolded
- [ ] Create DB schema in Supabase (`schema.sql`)
- [ ] Implement GitHub OAuth flow + token encryption
- [ ] Implement `GitHubAgent` & `GitAgent` end-to-end flows
- [ ] Add unit tests and CI

## Security & notes
- Keep `.env` private. If keys leak, rotate them immediately in Supabase / GitHub.
- `SUPABASE_SERVICE_KEY` grants high privileges; only use from trusted server-side code.
- Use HTTPS in production and limit origin access in `config.py`.

## Troubleshooting
- `Invalid URL` or `Invalid API key` from Supabase: ensure `SUPABASE_URL` is the HTTP project domain (https://<project>.supabase.co) and `SUPABASE_KEY` is set.
- Permission errors creating files/directories: check `PROJECTS_BASE_DIR` path and permissions.

## How to contribute
- Create feature branches off `develop`
- Keep changes limited and well-tested
- Add unit tests for new endpoints/agents

## Contact & Next steps
- After DB schema is applied, I can help wire up the full project creation flow (create GitHub repo, initialize local repo, initial commit, Supabase record).

---
Generated on: 2025-10-04
