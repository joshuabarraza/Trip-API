# Trip-API
**Trip API** is a cloud-deployed REST API for planning trips. It was designed to support **trips**, **calendar-style itineraries**, **reservations**, **budgeting by custom categories**, and **Discord webhook reminders**, with production-style **logging, metrics, monitoring, and alerting**.

Proccesses Utilized: schema design, validation, auth, pagination, rate limiting, CI/CD, and observability (logs/metrics/alerts).

---

### Core features

* **Trips**: Create and manage trips with dates, destination, tags, and a lifecycle status (planning/upcoming/active/completed/archived).
* **Itinerary**: Calendar-style itinerary items with **start + end time**, location text, tags, and notes.
* **Reservations**: Standalone reservations (flights/hotels/events) with optional linkage to itinerary items, provider, confirmation data, links, status, and cost.
* **Budgeting**: Custom budget categories per trip (e.g., lodging/food/transport/activities/custom) and line items tied to reservations (and/or standalone spend entries).
* **Reporting**: Aggregated spend reporting (totals by category/day/status).
* **Templates**: Trip templates that can optionally create default budget categories and/or a starter itinerary skeleton.
* **Reminders**: Discord webhook notifications driven by customizable reminder rules (per trip and/or per reservation).
* **Exports**: Trip export in **JSON** (full data) and **CSV** (budget and itinerary-friendly formats).

---

### Tech stack

* **API Framework**: FastAPI (OpenAPI/Swagger built-in)
* **Database**: Postgres (Neon free tier)
* **Migrations**: Alembic
* **Deployment**: Render (or Fly.io)
* **Observability**:

  * Structured JSON logging (stdout)
  * Prometheus metrics (`/metrics`)
  * Grafana Cloud dashboards + alerting (free tier)
  * Optional: Sentry for error tracking

---

### High-level architecture

* Clients call the REST API using an **API key**.
* The API persists data to Postgres and records security-relevant actions in an **audit log**.
* Observability is first-class:

  * Requests emit structured logs including a `request_id`
  * Prometheus metrics expose latency/error-rate/rate-limit counters
  * Grafana Cloud scrapes metrics and triggers alerts
* Reminders are executed by an external scheduler (e.g., GitHub Actions cron) calling:

  * `POST /v1/jobs/run-reminders`

---

### Authentication & security

* **Auth**: Single-user API key (`Authorization: Bearer <key>`)
* **Rate limiting**: Per-key request limits (e.g., per-minute burst control)
* **Data hygiene**:

  * API keys are stored **hashed**
  * Logs never include raw secrets (keys, webhook URLs, confirmation numbers if sensitive)

# set in .env
API_KEY = tQen-4bOyT-r0Um-Pa1Zt

# example request
curl -H "Authorization: Bearer $API_KEY" http://127.0.0.1:8000/v1/trips

---

### Data model (conceptual)

* **Trip**

  * `id, title, destination, start_date, end_date, status, tags[], notes, currency`
* **ItineraryItem**

  * `id, trip_id, start_at, end_at, title, location_text, tags[], notes`
* **Reservation**

  * `id, trip_id, itinerary_item_id?`
  * `type (flight/hotel/event/etc), provider, status`
  * `confirmation_code?, link_url?, cost_amount?, cost_category_id?`
* **BudgetCategory**

  * `id, trip_id, name` (custom per trip)
* **SpendEntry** (optional; can also be derived from reservations)

  * `id, trip_id, category_id, amount, occurred_at, notes`
* **ReminderRule**

  * `id, trip_id, scope (trip|reservation), target_id?, offset_minutes, enabled`
* **AuditEvent**

  * `id, actor, action, entity_type, entity_id, payload_json, created_at`

---

### API design highlights

* **Versioned API**: `/v1/...`
* **Pagination**: list endpoints use `limit` + `offset`
* **Filtering**: basic filters per resource (e.g., by trip, date range, status)
* **Consistent errors**: structured error responses with a stable shape for clients
* **Health endpoints**:

  * `GET /health` (liveness)
  * `GET /ready` (readiness: DB connectivity)
* **Metrics endpoint**:

  * `GET /metrics` (Prometheus format)

---

### Example endpoints

**Trips**

* `POST /v1/trips`
* `GET /v1/trips?limit=&offset=`
* `GET /v1/trips/{trip_id}`
* `PATCH /v1/trips/{trip_id}`
* `DELETE /v1/trips/{trip_id}`

**Itinerary**

* `POST /v1/trips/{trip_id}/itinerary`
* `GET /v1/trips/{trip_id}/itinerary?from=&to=&limit=&offset=`
* `PATCH /v1/itinerary/{item_id}`
* `DELETE /v1/itinerary/{item_id}`

**Reservations**

* `POST /v1/trips/{trip_id}/reservations`
* `GET /v1/trips/{trip_id}/reservations?status=&limit=&offset=`
* `PATCH /v1/reservations/{reservation_id}`
* `DELETE /v1/reservations/{reservation_id}`

**Budget + reporting**

* `POST /v1/trips/{trip_id}/budget/categories`
* `GET /v1/trips/{trip_id}/budget/categories`
* `GET /v1/trips/{trip_id}/reports/spend?group_by=category|day|status`

**Templates**

* `POST /v1/templates`
* `GET /v1/templates`
* `POST /v1/trips/{trip_id}/apply-template/{template_id}` (options for “categories only” vs “categories + itinerary seed”)

**Reminders**

* `POST /v1/trips/{trip_id}/reminders/rules`
* `POST /v1/jobs/run-reminders` (invoked by cron)
* Sends notifications to a configured Discord webhook

**Export**

* `GET /v1/trips/{trip_id}/export.json`
* `GET /v1/trips/{trip_id}/export.itinerary.csv`
* `GET /v1/trips/{trip_id}/export.budget.csv`

---

### Observability (logging, monitoring, alerting)

**Structured logs**

* Every request includes: `request_id`, method, path, status_code, latency_ms
* Errors include exception name + stack trace (without leaking secrets)

**Metrics**

* Request counters by route/status
* Latency histograms (p50/p95/p99)
* Error counters
* Rate-limit counters
* Reminder job success/fail counters + duration

**Dashboards + alerts**

* Grafana dashboards for:

  * error rate
  * p95 latency
  * traffic volume
  * reminder job health
* Alerts for:

  * elevated 5xx error rate
  * latency regression
  * repeated reminder job failures

---

### Deployment & CI/CD

* GitHub Actions runs:

  * lint + tests on every PR
  * deploy on merge to `main`
* Environment variables are used for:

  * database URL
  * API key secret(s)
  * Discord webhook configuration
  * optional Sentry DSN

---

### Roadmap

* Multi-user: accounts, shared trips, roles
* Map support: optional `lat/lng` fields + bounding-box queries
* Strong search: full-text query for title/notes/location
* File attachments: store ticket PDFs/images in object storage
* Mobile/web UI client

---

If you want, next I can generate:

1. the **exact endpoint schemas** (request/response JSON) and error format, and
2. a **database schema** (tables + key constraints) that matches this README section.
