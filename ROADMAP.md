# Python SV Roadmap

## Website

### Now (April–May 2026)

- [x] Landing page with community info
- [x] Code of Conduct page (conduct@pythonsv.com)
- [x] Calendar page with upcoming events
- [x] WhatsApp group link
- [x] SEO basics: sitemap.xml, robots.txt, Open Graph tags
- [x] Production deploy on Azure Container Apps (pythonsv.com)
- [x] CI: build + push to ACR on push to main
- [ ] Auto-deploy from GitHub Actions (blocked — need Azure SP permissions)
- [ ] Join form: collect name + email via Resend for announcements
- [ ] Speaker proposal form (simple: name, topic, description, experience level)
- [ ] /llms.txt page (reference: anthropic, openai, llmstxt.org for format)

### Next

- [ ] Blog/posts section — markdown-based, no CMS
- [ ] Event detail pages (individual URLs per event, not just the grid)
- [ ] Past events archive with slides/recordings links
- [ ] Members page — featured speakers, organizers
- [ ] i18n: full English translation (currently partial via JS toggle)
- [ ] Analytics (Plausible or Umami — privacy-friendly, no cookies)

### Later

- [ ] Sponsors/partners page
- [ ] Job board or community classifieds
- [ ] Resources page: curated Python learning links for SV developers
- [ ] Dark mode
- [ ] RSS feed for blog posts and events

---

## Infrastructure

### Done

- [x] Domain: pythonsv.com
- [x] Hosting: Azure Container Apps (production + staging)
- [x] CI/CD: GitHub Actions builds on push to main
- [x] ACR: pythonsvcr.azurecr.io
- [x] Email: Google Workspace (pythonsv.com domain)
- [x] Linear: linear.app/python-sv
- [x] Notion: "Python SV" workspace

### Pending

- [ ] Auto-deploy: grant Contributor role to SP `github-pythonsv` (appId: `4493f559-a697-4db9-b881-6a11851bbcd3`)
- [ ] Email: create hola@pythonsv.com (general contact alias or mailbox)
- [ ] Resend: configure for pythonsv.com domain (DNS records)
- [ ] Monitoring/alerting: uptime checks, error tracking
- [ ] Backup strategy for content/data
