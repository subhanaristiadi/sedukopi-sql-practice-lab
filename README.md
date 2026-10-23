# Sedukopi SQL Practice Lab

An interactive SQL learning lab based on the Sedukopi dataset. This project follows the deployment pattern used by [Gayanara SQL Practice Lab](https://github.com/subhanaristiadi/gayanara-sql-practice-lab): GitHub Pages for the static frontend, Render for a Flask API, and Neon PostgreSQL for the hosted practice database.

## Architecture

- **Frontend:** `index.html`, hosted as a GitHub Pages project site.
- **Backend:** `server.py`, deployed to Render using `render.yaml`.
- **Database:** PostgreSQL on Neon. Only the dedicated `sedukopi_reader` role is used by the public API.
- **Progress:** answer text, notes, and completion status stay in that browser's `localStorage`; there are no user accounts or cross-device sync.

## Included learning material

- 47 sub-exercises across 21 topics.
- Business prompts, required tables, output columns, analytical grain, limitations, and reference SQL.
- Query runner with actual rows from PostgreSQL and automatic result validation.
- Progress save, import, export, and reset in the browser.
- Revenue analysis uses `orders.total_amount` at order grain. `temporarily_closed` outlets are excluded from the specific ranking exercises. Do not treat line-item revenue and order-level revenue as interchangeable without verifying the metric.

## Important data note

The package was built using the supplied Sedukopi CSVs and project documentation. The CSV headers differ from portions of the earlier schema reference: `staff.csv` contains `monthly_salary` (not `phone`) and `orders.csv` contains the eight columns shown in the dataset file. The Neon seed script uses the **actual supplied CSV headers** and includes the monthly salary field. The user's local PostgreSQL instance is not accessible from this build environment, so the hosted Neon data is a separate copy and was not queried or validated yet.

Expected supplied CSV counts: outlets 20, staff 120, menu_items 80, orders 5,000, order_details 8,123. `seed_neon.py` checks headers/counts and foreign-key orphan rows before committing. Keep these CSV files local; they are not included in this repository package.

## Deploy overview

Follow [`DEPLOYMENT.md`](DEPLOYMENT.md) in order. In summary:

1. Create a new public GitHub repository named `sedukopi-sql-practice-lab` and upload the repository files. Do not upload `.env`, CSVs, passwords, or connection strings.
2. Create a fresh Neon project/database and run `seed_neon.py` locally against it, using the Neon owner connection string only for initial data loading.
3. Run `create_reader_role.sql` in Neon SQL Editor, substituting a unique strong password. The role has only `CONNECT`, schema `USAGE`, and table `SELECT` grants.
4. Create a Render Web Service from the repo using `render.yaml`. Set `DATABASE_URL` to the **reader-role connection string**, not the Neon owner/admin URL.
5. Enable GitHub Pages from the `main` branch root. Confirm `BACKEND_BASE` in `index.html` matches the Render URL if its actual URL differs from the default.
6. Verify Render `/health`, then run a query and validation in the page.

## API safety controls

The API accepts one SELECT/SELECT-based CTE, parses PostgreSQL syntax with SQLGlot, uses read-only transactions, enforces the non-superuser/read-only-role guard in hosted mode, and caps rows, output bytes, query time, request size, concurrent executions, and requests per IP. CORS allows the configured frontend origin. These controls reduce risk but are not a guarantee of security for arbitrary SQL; the database role's privileges are the primary boundary. This app is intended for practice data, not private or production databases.

## Local development (optional)

Install Python 3.11+ and requirements, copy `.env.example` to `.env`, set local PostgreSQL credentials, and run `python server.py`. For a public Render deployment, use `DATABASE_URL` and never use the `postgres` administrator role.
