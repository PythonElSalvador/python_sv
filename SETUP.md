# Configuración de infraestructura de PythonSV

El sitio público de Python SV se publica en GitHub Pages como HTML estático generado desde las plantillas Jinja2 del repositorio.

## Hosting

- Producción: https://pythonsv.com
- Repositorio: `PythonElSalvador/python_sv`
- Hosting: GitHub Pages
- Dominio personalizado: `pythonsv.com`
- Build artifact: `dist/`

## GitHub Pages

En GitHub, configurar:

1. Repository settings > Pages.
2. Source: GitHub Actions.
3. Custom domain: `pythonsv.com`.
4. Enforce HTTPS: enabled once GitHub finishes provisioning the certificate.

The Pages workflow writes a `CNAME` file into the published artifact, so the custom domain remains attached across deploys.

## DNS

Set these records at the DNS provider for `pythonsv.com`:

| Host | Type | Value |
|---|---|---|
| `@` | `A` | `185.199.108.153` |
| `@` | `A` | `185.199.109.153` |
| `@` | `A` | `185.199.110.153` |
| `@` | `A` | `185.199.111.153` |
| `www` | `CNAME` | `PythonElSalvador.github.io` |

If DNS is managed in Cloudflare, use DNS-only mode while GitHub provisions HTTPS. After Pages is working, enable Cloudflare proxying for `pythonsv.com` and `www.pythonsv.com` so the Worker route can intercept `/api/*`.

## Forms Worker

GitHub Pages cannot store secrets or call Resend safely from browser JavaScript. The public site posts forms to same-origin `/api/signup` and `/api/proposal`; Cloudflare routes those paths to the `pythonsv-forms` Worker.

Worker files:

- `workers/forms/src/index.js`
- `workers/forms/wrangler.toml`
- `.github/workflows/forms-worker.yml`

Required Cloudflare Worker secrets:

```bash
cd workers/forms
npx wrangler secret put RESEND_API_KEY
npx wrangler secret put NOTIFICATION_TO
```

Required GitHub Actions secrets for Worker deploy:

| Secret | Description |
|---|---|
| `CLOUDFLARE_API_TOKEN` | Token with permission to deploy Workers and edit Worker routes for the `pythonsv.com` zone |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare account ID |

The Worker uses these non-secret vars from `wrangler.toml`:

| Var | Value |
|---|---|
| `ALLOWED_ORIGINS` | `https://pythonsv.com,https://www.pythonsv.com` |
| `WHATSAPP_URL` | WhatsApp community invite URL |

The Worker currently uses Resend's default onboarding sender in code. Add a configured sender later after `pythonsv.com` is verified in Resend.

## Static Build

Run the same static build locally:

```bash
uv run python scripts/build_static.py
```

The build:

- copies `src/python_sv/static/` into `dist/static/`
- renders `/`, `/calendario`, `/propuestas`, `/codigo-de-conducta`, and `/404.html`
- writes `robots.txt`, `sitemap.xml`, `llms.txt`, `.nojekyll`, and `CNAME`
- includes htmx forms that post to the Cloudflare Worker at `/api/signup` and `/api/proposal`

To preview locally:

```bash
cd dist
python -m http.server 8000
```

Then open http://localhost:8000.

## CI/CD

| Workflow | Trigger | What it does |
|---|---|---|
| `ci.yml` | PRs to `main` | Linting and tests |
| `deploy.yml` | Push to `main`, manual dispatch | Linting, tests, static build, deploy to GitHub Pages |
| `forms-worker.yml` | Push to Worker files, manual dispatch | Deploy Cloudflare Worker for `/api/*` forms |

No Azure, ACR, or container-app secrets are required for the public site.

## Backend Notes

The FastAPI app remains useful for local development and for any future server-backed version. Production form submissions are handled by the Cloudflare Worker, not FastAPI.

The Worker sends Resend notifications but does not currently store submissions in MongoDB. `/admin/signups` remains local/backend-only unless a server-backed production app is reintroduced.
