# Sedukopi SQL Practice Lab

An interactive, browser-based SQL learning environment built around the Sedukopi dataset. Learners can practice PostgreSQL queries against a hosted Neon database, inspect real query results, validate answers against reference outputs, and track their learning progress locally.

**Live app:** https://subhanaristiadi.github.io/sedukopi-sql-practice-lab/  
**Source code:** https://github.com/subhanaristiadi/sedukopi-sql-practice-lab

## Project highlights

- **47 SQL exercises** across 21 topics, from SQL fundamentals to more advanced analysis.
- Business questions with required tables, analytical grain, expected output, and learning notes.
- PostgreSQL query runner that returns real rows from the hosted database.
- Answer validation that compares a learner's result with a server-side reference result.
- Browser-based progress tracking, answer saving, personal notes, and progress import/export.
- Read-only API design intended for a public practice dataset.

## Architecture

```text
Learner's browser
  └── GitHub Pages: static HTML/CSS/JavaScript
        └── HTTPS API requests
              └── Render: Flask + Gunicorn API
                    └── Neon: PostgreSQL database
```

| Layer | Technology | Responsibility |
|---|---|---|
| Frontend | HTML, CSS, JavaScript, GitHub Pages | Exercise interface, SQL editor, results, progress UI |
| Backend | Python, Flask, Gunicorn, SQLGlot, Flask-Limiter, Render | SQL parsing, execution, validation, request limits |
| Database | PostgreSQL on Neon | Stores the Sedukopi practice tables |
| Local progress | Browser `localStorage` | Saves completion status, SQL answers, and notes in the current browser |

## Dataset

The database contains the following supplied Sedukopi tables:

| Table | Expected rows |
|---|---:|
| `outlets` | 20 |
| `staff` | 120 |
| `menu_items` | 80 |
| `orders` | 5,000 |
| `order_details` | 8,123 |

The Neon seed workflow checks CSV headers and row counts and checks for orphaned foreign keys before committing the seed transaction. The public repository should not contain source CSVs, database passwords, `.env` files, or database connection strings.

### Analytics conventions

- Use `orders.total_amount` for order-level revenue questions unless a business question explicitly defines another metric.
- Keep order-level and order-detail-level analysis separate to avoid double counting after joins.
- Exclude `temporarily_closed` outlets only for exercises whose stated business rule requires that exclusion.
- Do not assume `SUM(order_details.subtotal)` is interchangeable with `SUM(orders.total_amount)` without verifying the metric.

## Features

1. **Exercise browser:** search and filter by topic, difficulty, and completion status.
2. **SQL editor:** submit PostgreSQL `SELECT` queries and inspect returned columns and rows.
3. **Answer validation:** execute the submitted query and the trusted reference query independently, then compare outputs according to the exercise policy.
4. **Progress tools:** save answers and notes locally; export/import progress as JSON; reset local progress.
5. **API safety controls:** accept one SELECT-style query, parse SQL with SQLGlot, run database sessions in read-only mode, verify the hosted database role, and enforce query/result/request limits and per-IP rate limits.

## Validation performed

The following functional checks were performed against the deployed application:

- A valid outlet-details query returned 20 rows and 4 columns, and the answer validator reported a match.
- A query returning only `outlet_id` executed, but validation rejected it because its output did not match the expected columns.
- A `DELETE FROM outlets ...` test was rejected by the API's SQL validation.
- After a hard refresh, the browser still showed 1 completed exercise out of 47, confirming local progress persistence in the same browser profile.
- The Render `/health` endpoint returned `status: ok`, `database: connected`, and database name `neondb` when opened directly.

**Browser note:** a browser/client blocker prevented the frontend's `/health` fetch and produced `ERR_BLOCKED_BY_CLIENT`. The frontend was updated to continue checking `/api/exercises`; when exercises load successfully, it displays `Backend connected (health check unavailable)`. This indicator means the health-check request failed while the exercises API succeeded, not that the health endpoint itself was verified by the frontend.

These are basic functional checks, not a comprehensive security audit.

## Deployment overview

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for the full deployment procedure. The production layout is:

- GitHub Pages serves the frontend from the repository root.
- Render runs the Flask API from `server.py`.
- Neon hosts PostgreSQL.
- Render's `DATABASE_URL` must use the dedicated `sedukopi_reader` role, not the database owner/admin connection string.
- The reader role should have only the privileges needed to connect and read the required tables.

Never commit `.env`, passwords, connection strings, or source CSVs. Use a separate practice database rather than a private or production database.

## Limitations

- There are no user accounts or cloud-synced progress. Progress is stored in `localStorage` for the current browser profile and may not follow the user to another device or browser.
- The health-check indicator can report that its check is unavailable if a browser extension blocks `/health`, even while the exercise API remains usable.
- Functional checks do not replace ongoing dependency updates, monitoring, or a formal security review.

## Skills demonstrated

PostgreSQL, SQL analytics, Python, Flask API development, SQL parsing and validation, relational data loading, database privilege design, API safety controls, GitHub Pages, Render, Neon PostgreSQL, and deployment troubleshooting.
