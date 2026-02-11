# Trip-API
A cloud-deployed REST API to create trips, build itineraries, generate packing lists from templates, and send reminders

## Goals to integrate
### A) Product goals (usefulness)
- Plan trips: store destination, dates, notes, time zone
- Itinerary: day-by-day items (time, title, location, tags)
- Packing: apply templates to generate a trip-specific pack list
- Personal gear closet: reusable gear inventory, weight optional
- Export: JSON + CSV export for offline use (and “real-world” feel)

### B) Engineering goals (the “hire me” stuff)
- Cloud deployment: public base URL + versioned API (/v1)
- Auth: API key (simple + realistic) with rate limiting
- Validation: strict request/response schemas
- Database + migrations: proper schema with migrations (shows maturity)
- Testing: unit + API tests (at least the critical flows)

- Observability: structured JSON logs w/ request_id, metrics endpoint (/metrics) for Prometheus, dashboards + alerts (Grafana Cloud), CI/CD: GitHub Actions (tests on PR, deploy on main)

### C) Cost goals
- $0/mo target with free tiers
- avoid paid SMS/email; use Discord webhook reminders (free) or just in-app reminders
