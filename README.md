# Trip-API

A production-style backend service for managing trips, reservations, and structured financial budgeting.

- Built with Python, FastAPI, PostgreSQL, and SQLAlchemy, this system models relational data with enforced integrity, supports financial reporting endpoints, and provides structured export functionality.

---

## Overview

This backend API supports:

* Trip lifecycle management
* Reservation tracking
* Categorized expense recording
* Budget vs. actual financial reporting
* JSON and CSV data export
* API key authentication
* Per-key rate limiting
* Versioned database migrations

The system was designed with production-style architecture principles including relational modeling, constraints, indexed queries, and schema version control.

---

## Tech Stack

* Python 3.9+
* FastAPI
* PostgreSQL (Neon)
* SQLAlchemy (ORM)
* Alembic (migrations)
* SlowAPI (rate limiting)
* Pydantic (data validation)

---

## Core Features

### Trip Management

* Create, list, and manage trips
* Track trip status and metadata
* Pagination support

### Reservations

* Associate reservations with trips
* Timezone-aware scheduling
* Cost estimation
* Structured metadata (JSONB)
* Reservation summaries (grouped by type/status)

### Budget Categories

* Custom categories per trip
* Planned budget allocation
* Unique category constraints per trip

### Spend Entries

* Record categorized financial transactions
* Link expenses to reservations and categories
* Filter by date, currency, reservation, or category
* Spend summary aggregation

### Financial Reporting

* Budget vs. actual analysis
* Categorized expense totals
* Currency-based aggregation
* Uncategorized expense tracking

### Export

* Full trip export in JSON
* Spend ledger export in CSV

### Infrastructure

* API key authentication (Bearer token)
* Per-key rate limiting (30 requests/minute)
* Health and readiness endpoints
* Alembic-managed schema migrations

---

## API Structure

Base path:

```
/v1
```

Examples:

```
GET    /v1/trips
POST   /v1/trips
GET    /v1/trips/{trip_id}/reservations
GET    /v1/trips/{trip_id}/spend-entries
GET    /v1/trips/{trip_id}/budget-categories
GET    /v1/trips/{trip_id}/budget-summary
GET    /v1/trips/{trip_id}/export
```


## Architecture Highlights

* Relational data modeling using foreign keys and cascading relationships
* Check constraints and unique constraints to enforce data integrity
* Indexed fields for optimized query performance
* Aggregation queries for real-time financial reporting
* Version-controlled database schema evolution via Alembic
* Modular route separation by domain (trips, reservations, budgeting, exports)

---

## Steps for Running Locally

### 1. Clone repository

```
git clone <your-repo-url>
cd trip-planning-api
```

### 2. Create virtual environment

```
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```
DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>/<db>
API_KEY=<your_api_key>
```

### 5. Run migrations

```
alembic upgrade head
```

### 6. Start server

```
uvicorn app.main:app --reload
```

Server runs at:

```
http://127.0.0.1:8000
```


## Goals for Future

* Plan to have it designed around a Multi-tenant user model
* Should have Role-based authentication
* Scheduled reminders via cron/webhooks
* Dashboard visualization layer
* Cloud deployment configuration

---

## License

This project is intended for educational and portfolio purposes.
