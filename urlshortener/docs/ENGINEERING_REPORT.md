# Engineering Report: AI-Assisted URL Shortener

## Executive overview

This repository delivers a runnable URL-shortening API with custom aliases, safe random aliases, expiry handling, redirects, and aggregate click analytics. The engineer owns requirements, design choices, acceptance decisions, and every merge; AI is used as a bounded accelerator for drafts, test cases, refactoring suggestions, and review checklists.

The design deliberately favors a small modular service over premature distributed architecture. SQLite enables an end-to-end local prototype; SQLAlchemy isolates persistence so a production deployment can move to PostgreSQL without changing HTTP handlers.

## Requirement normalization

### Functional scope

- Create a short link from an absolute HTTP(S) URL.
- Allow an optional unique custom code; otherwise create a cryptographically strong random code.
- Redirect a request for a valid code and increment aggregate click count.
- Return analytics for a code.
- Support an optional expiry timestamp; expired links must not redirect.
- Expose a health endpoint and machine-readable OpenAPI documentation.

### Assumptions and boundaries

- Analytics means aggregate clicks, not user-level tracking; no IP, user-agent, or personal data is retained.
- Links are public in this prototype. Authentication, ownership, deletion, and administrative controls are deferred.
- Only HTTP(S) destinations are accepted through Pydantic URL validation.
- Redirect uses HTTP 307 to preserve the request method.

## Architecture

```text
Client -> FastAPI route -> service layer -> SQLAlchemy session -> SQLite
              |                |
              |                +-> validation, collision, and expiry rules
              +-> OpenAPI, HTTP status mapping, redirect response
```

| Component | Responsibility | Design decision |
|---|---|---|
| `app/main.py` | HTTP endpoints and response mapping | Thin routes; business rules remain outside handlers |
| `app/services.py` | Code generation and domain rules | Bounded retry for generated-code collisions |
| `app/models.py` | `ShortLink` persistence model | Code is the uniqueness boundary and primary key |
| `app/schemas.py` | Request and response contracts | Validate input at the API boundary |
| `tests/` | Regression coverage | Exercise success paths and failure semantics |

## API contract

| Endpoint | Success | Error behavior |
|---|---|---|
| `POST /api/v1/links` | `201` with code and short URL | `409` duplicate alias; `422` invalid URL or past expiry; `503` allocation exhaustion |
| `GET /{code}` | `307` redirect | `404` unknown code; `410` expired code |
| `GET /api/v1/links/{code}/analytics` | `200` click count and metadata | `404` unknown code |
| `GET /health` | `200` with status | Liveness endpoint |

## Work plan and dependencies

| Order | Task | Dependency | Acceptance criteria |
|---|---|---|---|
| 1 | Normalize requirements and record non-goals | None | API behavior and open questions captured |
| 2 | Define data model and API schemas | 1 | URL, code, expiry, and analytics contract agreed |
| 3 | Implement create and resolve services | 2 | Collision, not-found, and expiry rules covered |
| 4 | Implement HTTP routes and OpenAPI | 3 | Endpoints return documented status codes |
| 5 | Add regression tests | 3–4 | Happy path and failure cases run locally |
| 6 | Run quality and security review | 5 | Tests, lint, and review gates completed |

## Three scenarios

### Greenfield: base service

**Intent:** Build the minimum useful service from a blank repository. **Decomposition:** define contracts, choose a persistence abstraction, implement creation and redirect behavior, expose analytics, and add tests. **Execution:** FastAPI supplies typed validation and OpenAPI; SQLAlchemy isolates persistence; a service layer centralizes business rules. **Validation:** create a link, request a redirect with automatic following disabled, then verify analytics reports one click.

### Brownfield: custom aliases and expiry

**Change request:** Customers need memorable links that can expire. **Impact analysis:** the schema gains nullable `expires_at`; creation gains `custom_code` and `expires_at`; the service enforces uniqueness and future timestamps; redirect returns `410 Gone`; analytics exposes expiry. **Validation:** test duplicate aliases and invalid past expiry. The database primary key remains the concurrency-safe uniqueness boundary; an `IntegrityError` maps to `409 Conflict`.

### Ambiguous: analytics definition

Analytics could mean an aggregate count, event history, referrer data, geography, bot filtering, or privacy-sensitive tracking. The prototype implements only `click_count`, creation time, destination, and expiry. This meets the observability intent without collecting personal data or creating a stream platform. Product follow-ups: Is analytics owner-only? What retention applies? Must counts be exact under concurrency? Should bots be filtered? A production version could publish redirect events to Kafka or Kinesis and aggregate asynchronously with explicit idempotency.

## AI-assisted execution record

AI was used only with non-sensitive, synthetic code and requirements. No credentials, customer data, proprietary source, production configuration, or confidential URLs were supplied to an external model.

| Activity | AI contribution | Engineer decision |
|---|---|---|
| Initial design | Drafted module boundaries and candidate endpoints | Edited and accepted thin routes and service layer; removed speculative components |
| Link generation | Suggested random code and database uniqueness | Used `secrets`, bounded retry, and integrity-error mapping; rejected predictable timestamp IDs |
| Test design | Generated candidate happy-path and negative scenarios | Implemented core regression tests; retained load/concurrency tests as release gates |
| Review | Flagged URL abuse, race conditions, and PII concerns | Added validation and no-PII boundaries; documented production controls |
| Documentation | Drafted report structure | Engineer verified, revised, and approved all claims |

AI output is never merged blindly. The engineer reviews changes, runs tests and linting, and retains sign-off responsibility. Schema migrations, redirect-policy changes, authentication, retention changes, and deployment require peer review and explicit human approval.

## Validation and quality gates

```bash
pytest -q
ruff check .
uvicorn app.main:app --reload
```

Before production: pass unit/API tests; lint; dependency vulnerability scan such as `pip-audit`; secret scan such as `gitleaks`; review OpenAPI; execute a fresh-database smoke test; and obtain peer approval. Use k6 or Locust to measure redirect throughput and p95 latency against the real datastore; do not claim capacity without measurements.

## Risks and production path

| Risk | Prototype control | Production hardening |
|---|---|---|
| Abuse or phishing links | HTTP(S) parsing only | Authentication, allow/deny policy, reputation scanning, reporting, rate limits |
| Counter contention | Transactional increment | Atomic SQL update or event stream with idempotent aggregation |
| SQLite constraints | Appropriate for local execution | PostgreSQL, migrations, pooling, backups, multi-AZ deployment |
| Code enumeration | Random code and alias validation | Longer codes, WAF/rate limits, monitoring |
| Expiry cleanup | Block expired links at read time | Scheduled archive/purge aligned to retention policy |
| Observability gaps | Health endpoint | Metrics, tracing, dashboards, SLOs, alerts, audit events |

## Limitations and sign-off

The prototype intentionally omits authentication, tenant isolation, delete/update APIs, migrations, owner authorization, per-event analytics, rate limits, cache/CDN, abuse tooling, and production secrets/configuration management. It is a runnable, reviewable engineering artifact rather than a production deployment claim.

I reviewed the implementation against normalized requirements, examined AI-derived suggestions before adoption, and would require the stated quality gates and peer review before production release. The engineer owns correctness and production readiness; AI is a drafting and review accelerator.
