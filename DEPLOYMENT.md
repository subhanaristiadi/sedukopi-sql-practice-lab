# Sedukopi SQL Practice Lab — GitHub Pages + Render + Neon

This setup copies the deployment pattern used by the Gayanara SQL Practice Lab. It does not change the existing Gayanara repository or any local PostgreSQL database. Use a **new, empty Neon database** for the hosted Sedukopi copy.

## 1. Prepare the repository

1. On GitHub, create a new repository named `sedukopi-sql-practice-lab` under `subhanaristiadi`.
2. Download/extract this package to a folder. Run `publish_to_github.bat`, paste the URL of the empty repository, inspect the listed files, then confirm commit/push. It uses Git installed on Windows and does not upload CSVs or `.env`; `.gitignore` excludes them.
3. Do **not** upload the CSV files, `.env`, passwords, or database connection strings.

## 2. Create an empty Neon database

1. Open https://console.neon.tech and create a new project. Choose a region close to Render; this package currently configures Render for Singapore.
2. From Neon, copy the owner/admin connection string privately. Do not paste it into GitHub or this chat.
3. Put the five local CSVs (`outlets.csv`, `staff.csv`, `menu_items.csv`, `orders.csv`, `order_details.csv`) in one folder. This script expects the column headers that are present in the supplied files.
4. On Windows PowerShell, from the repository folder run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:SEDUKOPI_SEED_DATABASE_URL = "PASTE_NEON_OWNER_CONNECTION_STRING_HERE"
$env:SEDUKOPI_CSV_DIR = "C:\path	oolder\with	heive\csvs"
python .\seed_neon.py
```

Replace the CSV folder path. The script will prompt for the Neon owner connection string with hidden input, so the secret does not appear on screen or in the shell command itself. The string is held only in the Python process and is not written to a project file.

`seed_neon.py` refuses to run if any target tables already exist. It performs its work in one transaction and rolls back on an error. It verifies expected CSV headers, row counts, and foreign-key orphan checks. If the script stops because a table already exists, do not drop it automatically; inspect the Neon project and choose a new empty database/project.

**Data/schema caveat:** these tables are built from the supplied CSVs, including `staff.monthly_salary`. The CSVs do not include `staff.phone` or `orders.customer_name`, which are mentioned in parts of the earlier local data reference. This hosted copy follows the supplied CSV columns so import is reproducible. It is not a claim that this newly created Neon database is identical to the local PostgreSQL schema.

## 3. Create the read-only API role

1. In Neon SQL Editor connected as owner/admin, open `create_reader_role.sql`.
2. Replace `REPLACE_WITH_A_UNIQUE_STRONG_PASSWORD` locally with a new password and execute the script. This creates `sedukopi_reader` with no superuser, database-creation, or role-creation privileges and grants only CONNECT, schema USAGE, and table SELECT.
3. If the Neon database name is not `neondb`, change the database name in the `GRANT CONNECT` statement before running it.
4. From Neon's connection details, select the `sedukopi_reader` role and copy its connection string. This becomes Render's `DATABASE_URL`. **Never use the owner/admin URL in the public API.**

## 4. Deploy the API on Render

1. Open https://dashboard.render.com and choose **New → Blueprint**.
2. Connect the newly created GitHub repository and allow Render to read `render.yaml`.
3. Create the web service defined in the blueprint. If the requested service name is unavailable, accept a unique Render service name.
4. In Render → Environment set `DATABASE_URL` to the **reader-role Neon connection string**. Other limits/origin are declared in `render.yaml`.
5. Deploy and inspect build/runtime logs. Do not post screenshots containing the connection string.
6. Open `https://YOUR-RENDER-SERVICE.onrender.com/health`. Expect JSON with `status: ok` and `database: connected`. If health fails, check the Render logs and the Neon reader grants.

The Render Free service may sleep after inactivity, so its first request can be slow. Check current plan limits in the Render dashboard.

## 5. Point the GitHub Pages frontend at Render

The default API constant at the beginning of the script in `index.html` is:

```js
const API_BASE = "https://sedukopi-sql-practice-lab-api.onrender.com";
```

If Render assigns a different URL, replace that one constant with the exact HTTPS service URL shown in Render and commit the change.

Then in GitHub repository **Settings → Pages**, choose **Deploy from a branch**, branch `main`, folder `/ (root)`, and Save. Wait until GitHub Pages shows the published URL. For this username/repository, the expected project site is `https://subhanaristiadi.github.io/sedukopi-sql-practice-lab/`.

Render CORS is configured to allow the origin `https://subhanaristiadi.github.io`, which is the origin used by project pages. Do not change it to `*`.

## 6. Smoke test

1. Open the GitHub Pages website and hard-refresh.
2. The header should report that the PostgreSQL connection is available.
3. Run a simple read-only query, for example `SELECT COUNT(*) AS outlet_count FROM outlets;`.
4. Validate exercise `REV-01` against the reference answer.
5. Confirm a query such as `DELETE FROM outlets;` is rejected before execution.
6. Confirm your answers and notes persist after reloading the same browser; progress is browser-local, not synced to other devices.

## Troubleshooting

- **Render health returns 503:** confirm reader `DATABASE_URL`, Neon is reachable, and the role is not a superuser and has SELECT on all five tables but no table write privileges.
- **CORS error:** set `CORS_ALLOWED_ORIGINS` in Render to exactly `https://subhanaristiadi.github.io`.
- **Browser says backend unavailable:** open the Render `/health` URL directly and confirm `API_BASE` in `index.html` is correct.
- **Validation mismatches:** the reference SQL is a proposed baseline. Schema/data differences or exercise-specific ordering can cause mismatches; report the exercise ID and visible result, not credentials.
- **Seed script safety stop:** it never drops tables. Use a fresh empty Neon database instead of manually dropping tables without inspection.

Never share real passwords, the full Neon connection string, or Render environment values in chat, screenshots, or the public repository.
