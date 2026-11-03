# Sedukopi Web App — Project Context

## Overview

The Sedukopi dataset has been developed into an interactive, browser-based SQL learning application: **Sedukopi SQL Practice Lab**.

- **Live application:** https://subhanaristiadi.github.io/sedukopi-sql-practice-lab/
- **Source repository:** https://github.com/subhanaristiadi/sedukopi-sql-practice-lab
- **Dataset source:** https://ngulikdata.com/datasets/sedukopi
- **Default branch inspected:** `main`

This application is a companion learning product built from the Sedukopi dataset. It complements the separate Sedukopi SQL analytics work, where business questions are analyzed and documented against the project's PostgreSQL database.

## Verified application scope

According to the repository README and application configuration:

- 47 SQL exercises organized across 21 learning topics.
- Exercises cover all 10 business-question themes documented for Sedukopi, from outlet revenue ranking through menu engineering, cross-selling, and outlet/staff efficiency.
- Each exercise can define its business question, required tables, analytical grain, expected output, learning objectives, limitations, and validation policy.
- Learners can write and submit PostgreSQL queries and inspect returned columns and rows.
- Submitted answers can be compared with server-side reference query results.
- Learners can save exercise completion status, SQL answers, and notes in browser storage, and import/export progress as JSON.

The repository's `coverage_matrix.md` maps exercise IDs to the ten business-question themes. The matrix explicitly treats exercise definitions and reference SQL as proposed baselines, not as proof that every exercise or analysis has been validated.

## Verified architecture and technology

```text
Learner browser
  └── GitHub Pages — static HTML/CSS/JavaScript frontend
        └── HTTPS API requests
              └── Render — Python Flask + Gunicorn API
                    └── Neon — hosted PostgreSQL database
```

| Layer | Verified technology | Responsibility |
|---|---|---|
| Frontend | HTML, CSS, JavaScript; GitHub Pages | Exercise interface, SQL editor, query results, progress UI |
| Backend | Python, Flask, Gunicorn, SQLGlot, Flask-Limiter; Render | SQL parsing, query execution, answer validation, request controls |
| Hosted database | PostgreSQL on Neon | Stores the hosted Sedukopi practice tables |
| Browser progress | `localStorage` | Saves completion status, submitted answers, and notes in the current browser profile |

The backend source confirms that it parses SQL using the PostgreSQL dialect, accepts a single query expression, rejects non-query/write operations, opens database sessions in read-only mode, applies query and result limits, and checks the configured database role when the non-superuser requirement is enabled. The README documents a dedicated `sedukopi_reader` role for the public deployment.

## Dataset and schema context

The application repository documents these five Sedukopi tables and expected CSV row counts:

| Table | Expected rows |
|---|---:|
| `outlets` | 20 |
| `staff` | 120 |
| `menu_items` | 80 |
| `orders` | 5,000 |
| `order_details` | 8,123 |

The application repository's deployment notes state that its hosted Neon schema is seeded from the supplied CSV files. They also document a schema difference that must not be silently reconciled with the separate local PostgreSQL project:

- The hosted seed uses `staff.monthly_salary`.
- The supplied CSVs do not include `staff.phone` or `orders.customer_name`, which appear in parts of the earlier local data reference.
- Therefore, do not assume the hosted Neon schema and the local `sedukopi` PostgreSQL schema are identical. Verify the target database before writing SQL or transferring assumptions.

The application README records that the seed workflow checks CSV headers, row counts, and orphaned foreign keys before committing the seed transaction.

## Analytics conventions shared with the SQL analytics project

The application README documents these conventions:

1. Use `orders.total_amount` for order-level revenue questions unless a business question explicitly defines another metric.
2. Keep order-level and order-detail-level analysis separate to avoid double counting after joins.
3. Exclude outlets with status `temporarily_closed` only when the stated exercise/business rule requires it.
4. Do not assume `SUM(order_details.subtotal)` is interchangeable with `SUM(orders.total_amount)` without verification.

These conventions are consistent with the separate Sedukopi analytics project's source-of-truth and validation principles.

## Recorded functional checks

The repository README reports the following checks against the deployed application:

- An outlet-details query returned 20 rows and 4 columns, and answer validation reported a match.
- A query with only `outlet_id` executed, but validation rejected it because the output columns did not match the expected schema.
- A `DELETE FROM outlets ...` query was rejected by SQL validation.
- After a hard refresh, the same browser profile still showed 1 completed exercise out of 47.
- The Render `/health` endpoint returned `status: ok`, `database: connected`, and database name `neondb` when opened directly.

The README also records a browser/client blocker affecting the frontend `/health` fetch. When the exercises API succeeds despite that check being unavailable, the frontend reports that the backend is connected with the health check unavailable. These checks are basic functional tests, not a comprehensive security audit.

## Known limitations

- There are no user accounts or cloud-synced progress. Progress is stored in `localStorage` and is limited to the current browser profile.
- Progress should not be expected to follow the learner across devices or different browser profiles.
- The health-check indicator can be unavailable when a browser extension or client blocker prevents the `/health` request, even if the exercises API works.
- The repository explicitly says functional checks do not replace dependency maintenance, monitoring, or a formal security review.
- Exercise reference SQL and coverage documentation are not equivalent to completed, independently validated business analyses.

## Relationship to the separate Sedukopi SQL analytics project

Treat the work as two connected but distinct deliverables:

| Workstream | Purpose | Primary output |
|---|---|---|
| Sedukopi SQL analytics project in this ChatGPT project | Perform business analysis progressively, validate results against the actual local PostgreSQL database, and derive evidence-based insights | Analysis SQL, validation notes, results, business insights, and portfolio presentation |
| Sedukopi SQL Practice Lab web app | Provide an interactive learning environment for practicing PostgreSQL using a hosted copy of the Sedukopi dataset | Deployed web app, 47 exercises, API, reference answers, and learning progress UI |

The web app is now an established companion project in the overall Sedukopi portfolio. It does **not** replace the analytical workflow or make an analysis complete automatically.

### Current analytics status

The separate analytics project is still working on **Analysis #1 — Ranking Revenue per Gerai**. Its business question is which outlets generate the highest and lowest revenue. The documented methodology uses `SUM(orders.total_amount)`, joins `orders` to `outlets`, displays outlet name and city, and excludes `temporarily_closed` outlets from the main ranking. Results, validation, and business insights must still be completed against the actual local PostgreSQL database before this analysis is marked complete.

## Source files inspected

This context was prepared from the repository's current `main` branch, including:

- `README.md`
- `DEPLOYMENT.md`
- `coverage_matrix.md`
- `portfolio_description.md`
- `exercises.json`
- `server.py`

For future changes, re-check the live repository because the application and deployment may evolve.
