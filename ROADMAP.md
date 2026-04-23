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

- **May 2, 2026** — Python SV Meetup: AI, Memory & Security (in-person, venue TBD)
- **June 2026** — Python SV Meetup: Virtual (date & topic TBD)

### Venue Leads (contact in this order)

1. **Universidad Evangélica de El Salvador (UEES)** — they contacted us first
   - Contact: Miguel Angel Chavez, coordinador académico (+503 6434 3705, miguel.chavez@uees.edu.sv)
   - Status: Very interested. Reached out proactively (3/16), followed up again (4/1). Will pass info to dean for logistics.
   - Last contact: 4/14 — we said we'd start organizing again
   - Action: Follow up with May 2 date

2. **Universidad Francisco Gavidia (UFG)** — confirmed rooms available
   - Contact: Dr. Víctor Manuel Cuchilla (WhatsApp DM)
   - Status: Confirmed "si tenemos salones." Supports open source communities. Referred by Denis of BRI Sistemas via Marco Gonzalez.
   - Last contact: 3/16 — waiting for us to send dates
   - Action: Message him with May 2 date

3. **UCA (Universidad Centroamericana José Simeón Cañas)** — contact through Emilio
   - Contact: Emilio knows the department head of electronics & informatics (his former professor)
   - Status: Emilio went in person, sent formal email. Couldn't do one specific Saturday (no staff), but relationship is open.
   - Last contact: 3/13 in Organizadores group
   - Action: Ask Emilio to re-engage for May 2

Also mentioned but no active lead:
- **UDB (Universidad Don Bosco)** — Computer Science Hub student group is in the community
- **Walter** has done events at UCA, UES, UFG, Café Luz Negra, La Biblioteca Café

### Event Pipeline

- [ ] Secure venue for May meetup — follow up with UEES, UFG, and UCA
- [ ] Find 2–3 speakers for May (AI/ML, memory management, security topics)
- [ ] Set up Meetup.com group (blocked — account disabled, support ticket #2018550 open)
- [ ] Create event registration flow (Meetup or custom RSVP)
- [ ] Post-event: publish slides, recordings, and photos
- [ ] Monthly cadence: alternate in-person (odd months) and virtual (even months)

### Event Format

- 2–3 short talks (15–20 min each)
- Lightning talks / demos welcome
- Networking time
- Bilingual: Spanish primary, English-friendly

---

## Community Growth

### Channels

- [x] WhatsApp group (active)
- [ ] Meetup.com group (blocked on account restore)
- [ ] Twitter/X (@pythonsv)
- [ ] LinkedIn page
- [ ] Discord or Slack (evaluate after 50+ members)
- [ ] YouTube channel for recordings

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

- [x] PSF Meetup Pro Network — application submitted (April 2026)

### Targets

- [ ] PSF grant for event costs (venue, food, swag)
- [ ] Local universities: UEES (warm), UFG (warm), UCA (warm via Emilio), UDB (community member)
- [ ] Tech companies in SV for sponsorship: Applaudo, Grupo Sega, etc.
- [ ] Food sponsors (easier ask — free food in exchange for publicity): Pollo Campero, Campestre, local restaurants
  - If cash sponsorship is hard to get, in-kind food donations are a lower barrier
  - Offer logo on event materials, social media shoutouts, mention during event
- [ ] Regional Python communities: Python Guatemala, Python Costa Rica, Python Colombia
- [ ] PyCon Latam participation or satellite event

---

## Infrastructure

### Done

- [x] Domain: pythonsv.com
- [x] Hosting: Azure Container Apps (production + staging)
- [x] CI/CD: GitHub Actions builds on push to main
- [x] ACR: pythonsvcr.azurecr.io
- [x] Email: Google Workspace (pythonsv.com domain)
  - hola@pythonsv.com — general contact
  - conduct@pythonsv.com — Code of Conduct reports
  - kevinturcios@pythonsv.com — organizer

### Pending

- [ ] Auto-deploy: grant Contributor role to SP `github-pythonsv` (appId: `4493f559-a697-4db9-b881-6a11851bbcd3`)
  ```
  az role assignment create \
    --assignee 4493f559-a697-4db9-b881-6a11851bbcd3 \
    --role Contributor \
    --scope /subscriptions/923d59dc-54b7-47d4-ab81-c7cb9061dac5/resourceGroups/pythonsv
  ```
- [ ] Resend: configure for pythonsv.com domain (DNS records)
- [ ] Monitoring/alerting: uptime checks, error tracking
- [ ] Backup strategy for content/data
