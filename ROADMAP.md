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

## Events

### Confirmed

- **May 9, 2026** — Python SV Workshop (in-person @ UEES, ~3–4 hours, topic TBD with university)
- **June 2026** — Python SV Meetup (in-person @ UFG, date & format TBD)

### Venue Leads (contact in this order)

1. **Universidad Evangélica de El Salvador (UEES)** — May 2026 venue (confirmed)
   - Contact: Miguel Angel Chavez, coordinador académico (+503 6434 3705, miguel.chavez@uees.edu.sv)
   - Status: Confirmed for May 9. Sent formal proposal 4/23, Miguel asked to push one week (4/26), confirmed May 9 (4/28). Waiting on schedule, room, and topic preferences.
   - Last contact: 5/1 — sent message asking for horario, salón, and topics
   - Action: Wait for Miguel's reply on logistics

2. **Universidad Francisco Gavidia (UFG)** — June 2026 venue (proposed)
   - Contact: Dr. Víctor Manuel Cuchilla (WhatsApp DM)
   - Status: Confirmed rooms available. Prefers 3–4 hour workshop format. Proposed as June venue on 5/1 per monthly rotation plan.
   - Last contact: 5/1 — sent June event proposal
   - Action: Wait for Cuchilla's reply on June date and logistics

3. **UCA (Universidad Centroamericana José Simeón Cañas)** — contact through Emilio
   - Contact: Emilio knows the department head of electronics & informatics (his former professor)
   - Status: Emilio went in person, sent formal email. Couldn't do one specific Saturday (no staff), but relationship is open.
   - Last contact: 3/13 in Organizadores group
   - Action: Re-engage for July or later in the rotation

Also mentioned but no active lead:
- **UDB (Universidad Don Bosco)** — Computer Science Hub student group is in the community
- **Walter** has done events at UCA, UES, UFG, Café Luz Negra, La Biblioteca Café

### Event Pipeline

- [x] Secure venue for May meetup — UEES confirmed for May 9
- [ ] Get schedule, room, and topic preferences from UEES (waiting on Miguel)
- [ ] Find speakers for May 9 (topics TBD — letting university poll students first)
- [ ] Confirm UFG for June event (proposal sent 5/1, waiting on Cuchilla)
- [ ] Set up Meetup.com group (blocked — account reinstated but group deleted, emailed support requesting restoration)
- [ ] Create event registration flow (Meetup or custom RSVP)
- [ ] Post-event: publish slides, recordings, and photos
- [ ] Monthly cadence: rotate between universities (May: UEES, June: UFG, July+: UCA or others)

### Event Format

- 2–3 short talks (15–20 min each)
- Lightning talks / demos welcome
- Networking time
- Bilingual: Spanish primary, English-friendly

---

## Community Growth

### Channels

- [x] WhatsApp Community (active — needs restructuring, see docs/whatsapp-community-analysis.md)
- [ ] Meetup.com group (blocked on account restore)
- [ ] Twitter/X (@pythonsv)
- [ ] LinkedIn page
- [ ] Discord or Slack (evaluate after 50+ members)
- [ ] YouTube channel for recordings

### WhatsApp Community Structure

Current state: 3 groups (Announcements, Python SV general, Fotos). General dormant since 4/4, Fotos low-value.

- [ ] Restructure Python SV WhatsApp Community (see docs/whatsapp-community-analysis.md)
  - Rename "Python SV general" to "☕ Charla General"
  - Replace "Fotos" with "🐍 Ayuda & Código" (tech questions, debugging, code review)
  - Add "📅 Eventos" group (meetup logistics, RSVPs, post-event links)
  - Add "💼 Oportunidades" group (jobs, freelance, internships)
- [ ] Set up weekly engagement rhythm
  - Monday: Python challenge (Exercism, LeetCode Easy)
  - Friday: Show & Tell / solutions
  - Post-event: recap + photos in Announcements
- [ ] Pin welcome message and rules in each group
- [ ] Audit communities we're active in (Ai /abs, PyCon Colombia, Python Colombia) for cross-promotion opportunities

### Content

- [ ] Monthly newsletter via Resend (once join form is live)
- [ ] Blog posts: event recaps, Python tips, member spotlights
- [ ] Social media presence: share events, Python news, community wins
- [ ] Beginner-friendly content in Spanish — tutorials, guides, FAQs

### Membership Targets

- May 2026: 30 WhatsApp members, 15 at first meetup
- August 2026: 100 members across platforms
- December 2026: 200+ members, 6 events completed

---

## Partnerships

### Active

- [x] PSF Community Partner (already listed)

### Targets

- [ ] PSF grant for event costs (venue, food, swag)
- [ ] Local universities: UEES (warm), UFG (warm), UCA (warm via Emilio), UDB (community member)
- [ ] Tech companies in SV for sponsorship: Applaudo, Grupo Sega, etc.
- [ ] Food sponsors (easier ask — free food in exchange for publicity): Pollo Campero, Campestre, local restaurants
  - If cash sponsorship is hard to get, in-kind food donations are a lower barrier
  - Offer logo on event materials, social media shoutouts, mention during event
- [ ] Regional Python communities: Python Guatemala, Python Costa Rica, Python Colombia (already in their WhatsApp Community)
- [ ] PyCon Latam participation or satellite event

---

## Infrastructure

### Done

- [x] Domain: pythonsv.com
- [x] Hosting: Azure Container Apps (production + staging)
- [x] CI/CD: GitHub Actions builds on push to main
- [x] ACR: pythonsvcr.azurecr.io
- [x] Email: Google Workspace (pythonsv.com domain)
  - conduct@pythonsv.com — Code of Conduct reports
  - kevinturcios@pythonsv.com — organizer
  - emilioserrano@pythonsv.com — organizer
- [x] Linear: workspace at linear.app/python-sv (kevinturcios@pythonsv.com)
  - GitHub integration connected (PythonElSalvador org)
  - Emilio invited
- [x] Notion: workspace "Python SV" (kevinturcios@pythonsv.com, free plan)
  - Emilio invited

### Pending

- [ ] Auto-deploy: grant Contributor role to SP `github-pythonsv` (appId: `4493f559-a697-4db9-b881-6a11851bbcd3`)
  ```
  az role assignment create \
    --assignee 4493f559-a697-4db9-b881-6a11851bbcd3 \
    --role Contributor \
    --scope /subscriptions/923d59dc-54b7-47d4-ab81-c7cb9061dac5/resourceGroups/pythonsv
  ```
- [ ] Email: create hola@pythonsv.com (general contact alias or mailbox)
- [ ] Resend: configure for pythonsv.com domain (DNS records)
- [ ] Monitoring/alerting: uptime checks, error tracking
- [ ] Backup strategy for content/data
