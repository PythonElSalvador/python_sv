# Python SV

Sitio web de la comunidad Python El Salvador — [pythonsv.com](https://pythonsv.com)

Built with FastAPI, Jinja2, and uv.

## Prerequisites

- [Python 3.12+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [prek](https://github.com/j178/prek) — `brew install prek` or `uv tool install prek`

## Getting Started

```bash
# Clone the repo
git clone https://github.com/PythonElSalvador/python_sv.git
cd python_sv

# Install dependencies
uv sync

# Copy the env file and edit as needed
cp .env.example .env

# Install pre-commit hooks
prek install

# Run the dev server
uv run uvicorn python_sv.main:app --reload
```

The site will be at http://localhost:8000.

## Docker

```bash
docker build -t pythonsv .
docker run -p 8000:8000 --env-file .env pythonsv
```

## Project Structure

```
src/
└── python_sv/
    ├── main.py            # FastAPI app, middleware, lifespan
    ├── config.py          # Settings (loaded from .env)
    ├── dependencies.py    # Shared deps (templates, page content)
    ├── notifications.py   # Email notifications via Resend
    ├── routers/
    │   └── pages.py       # Page routes
    ├── static/            # CSS, JS, images
    └── templates/         # Jinja2 HTML templates
content/
└── index.md               # Homepage content (markdown + frontmatter)
tests/                     # pytest test suite
```

## Tests

```bash
uv run pytest
```

## Linting

```bash
uv run ruff check .
uv run ruff format --check .
```

## Environment Variables

See [`.env.example`](.env.example) for the full list. Key variables:

| Variable | Description | Default |
|---|---|---|
| `BASE_URL` | Canonical site URL | `https://pythonsv.com` |
| `WHATSAPP_URL` | WhatsApp group invite link | — |
| `ALLOWED_HOSTS` | JSON list of allowed hostnames | `["localhost","127.0.0.1"]` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `RESEND_API_KEY` | Resend API key for email notifications | — |
| `WEB_CONCURRENCY` | Gunicorn worker count (Docker only) | `2` |

## Contributing

1. Create a branch off `main` and open a PR when ready
2. Prek runs `ruff check` and `ruff format --check` on every commit, and `pytest` on push
3. CI runs the same checks — format before committing: `uv run ruff format .`
4. Run all checks manually: `prek run --all-files`

### Adding a page

- **Content-driven pages** (like the homepage): add a markdown file in `content/` with YAML frontmatter, then load it in `src/python_sv/main.py` the same way `index.md` is loaded
- **Template-only pages** (like `/calendario`): add an HTML template in `src/python_sv/templates/` and a route in `src/python_sv/routers/pages.py`
- **Static assets** (CSS, JS, images, fonts): go in the matching subdirectory under `src/python_sv/static/`

## CI/CD

GitHub Actions runs on every PR and push to `main`:

- **ci.yml** — Lint + tests on PRs
- **deploy.yml** — Lint + tests + Docker build + push to ACR on merge to `main`
- **staging.yml** — Same pipeline for the `staging` branch

## Infrastructure

See [SETUP.md](SETUP.md) for the full infrastructure reference (Azure, MongoDB Atlas, DNS, etc.).
