# Python SV Roadmap

## Website

### Now (April–May 2026)

- [x] Landing page with community info
- [x] Code of Conduct page (conduct@pythonsv.com)
- [x] Calendar page with upcoming events
- [x] WhatsApp group link
- [x] SEO basics: sitemap.xml, robots.txt, Open Graph tags
- [x] Production deploy on GitHub Pages (pythonsv.com)
- [x] CI/CD: build static site + deploy to GitHub Pages on push to main
- [x] Join form via Cloudflare Worker + Resend
- [x] Speaker proposal form via Cloudflare Worker + Resend
- [x] /llms.txt page

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
- [x] Hosting: GitHub Pages
- [x] CI/CD: GitHub Actions builds on push to main
- [x] Forms backend: Cloudflare Worker
- [x] Email: Google Workspace (pythonsv.com domain)
- [x] Linear: linear.app/python-sv
- [x] Notion: "Python SV" workspace

### Pending

- [ ] Email: create hola@pythonsv.com (general contact alias or mailbox)
- [ ] Resend: configure for pythonsv.com domain (DNS records)
- [ ] Monitoring/alerting: uptime checks, error tracking
- [ ] Backup strategy for content/data
