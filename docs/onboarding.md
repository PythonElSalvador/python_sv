# Onboarding — Python SV

Guide for getting a new organizer set up with all Python SV systems.

## 1. Google Workspace

All organizer emails live under the pythonsv.com domain, managed via Google Workspace.

- **Admin console:** admin.google.com (sign in with kevinturcios@pythonsv.com)
- **Create a new user:** Admin console > Directory > Users > Add new user
- **Email format:** firstnamelastname@pythonsv.com (e.g. emilioserrano@pythonsv.com)
- The new organizer signs in at mail.google.com with their @pythonsv.com email

Existing accounts:
- hola@pythonsv.com — general contact
- conduct@pythonsv.com — Code of Conduct reports
- kevinturcios@pythonsv.com — organizer
- emilioserrano@pythonsv.com — organizer

## 2. GitHub

The org is **PythonElSalvador** on GitHub. The main repo is `python_sv`.

- **Invite:** github.com/orgs/PythonElSalvador/people > Invite member
- Give them **Member** role (not Owner unless necessary)
- They need a GitHub account — if they sign up with their @pythonsv.com Google account, it links automatically

Repo: github.com/PythonElSalvador/python_sv

## 3. Linear

Project management lives in Linear.

- **Workspace:** linear.app/python-sv
- **Invite:** Settings > Members > Invite by email (use their @pythonsv.com email)
- GitHub integration is already connected to the PythonElSalvador org — issues sync automatically

## 4. Notion

Documentation and internal notes live in Notion.

- **Workspace:** "Python SV" (free plan)
- **Invite:** Settings > Members > Invite by email (use their @pythonsv.com email)
- Sign in with "Continue with Google" using the @pythonsv.com account

## 5. WhatsApp

The community WhatsApp group is the primary communication channel.

- **Invite link:** Share the group link directly (stored in `app/config.py` as `whatsapp_url`)
- There's also an **Organizadores** group for organizer-only discussions — add them manually

## 6. Website & Repo

The website is pythonsv.com, hosted on Azure Container Apps.

### Local setup

```bash
git clone git@github.com:PythonElSalvador/python_sv.git
cd python_sv
uv sync
uv run fastapi dev app/main.py
```

The site runs at http://localhost:8000.

### Repo structure

```
app/
  main.py          — FastAPI app entry point
  config.py        — Settings (env vars, URLs)
  routers/pages.py — All page routes
  templates/       — Jinja2 HTML templates
  static/          — CSS, images, JS
docs/
  onboarding.md    — This file
  outreach/        — Venue proposals, outreach templates
tests/             — Test suite
ROADMAP.md         — Full roadmap and status tracking
```

### Deploy

- Pushes to `main` trigger a GitHub Actions build that pushes to Azure Container Registry (pythonsvcr.azurecr.io)
- Auto-deploy to Azure Container Apps is pending (needs Azure SP permissions)
- Staging environment exists for testing

## 7. Checklist

For each new organizer:

- [ ] Create @pythonsv.com email in Google Workspace
- [ ] Send them their temporary password (they'll reset on first login)
- [ ] Invite to GitHub org (PythonElSalvador)
- [ ] Invite to Linear workspace
- [ ] Invite to Notion workspace
- [ ] Add to WhatsApp Organizadores group
- [ ] Share this doc
