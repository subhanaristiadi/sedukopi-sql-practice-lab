"""Sedukopi SQL Practice Lab API for Render + Neon, with optional local development."""
from __future__ import annotations
import json, math, os, re, threading, time
from collections import Counter
from decimal import Decimal
from pathlib import Path
from typing import Any
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import sqlglot
from sqlglot import exp

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
REFERENCE_PATH = BASE_DIR / "reference_queries.json"
EXERCISES_PATH = BASE_DIR / "exercises.json"
RENDER_ENV = os.getenv("RENDER", "").lower() == "true"
PORT = int(os.getenv("PORT", os.getenv("SEDUKOPI_APP_PORT", "8000")))
MAX_ROWS = max(1, min(int(os.getenv("SEDUKOPI_MAX_ROWS", os.getenv("MAX_ROWS", "500"))), 5000))
MAX_RESULT_BYTES = max(100_000, min(int(os.getenv("SEDUKOPI_MAX_RESULT_BYTES", "1000000")), 2_000_000))
QUERY_TIMEOUT_MS = max(1000, min(int(os.getenv("SEDUKOPI_QUERY_TIMEOUT_MS", os.getenv("STATEMENT_TIMEOUT_MS", "10000"))), 30000))
LOCK_TIMEOUT_MS = max(500, min(int(os.getenv("LOCK_TIMEOUT_MS", "2000")), 10000))
MAX_SQL_CHARS = 20000
MAX_REQUEST_BYTES = 50000
REQUIRE_NON_SUPERUSER = os.getenv("REQUIRE_NON_SUPERUSER", "true" if RENDER_ENV else "false").lower() in {"true", "1", "yes"}
DEFAULT_ORIGINS = "https://subhanaristiadi.github.io,http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:8000,http://localhost:8000"
CORS_ALLOWED_ORIGINS = {x.strip().rstrip("/") for x in os.getenv("CORS_ALLOWED_ORIGINS", DEFAULT_ORIGINS).split(",") if x.strip()}
WRITE_PRIVILEGES = ("INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER")
TABLES = ("outlets", "staff", "menu_items", "orders", "order_details")
FORBIDDEN_NODES = (exp.Insert, exp.Update, exp.Delete, exp.Create, exp.Drop, exp.Alter, exp.Command, exp.Copy, exp.Transaction, exp.Grant, exp.Revoke, exp.Merge, exp.TruncateTable, exp.Into)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_REQUEST_BYTES
limiter = Limiter(key_func=get_remote_address, app=app, default_limits=[], storage_uri="memory://")
QUERY_SEMAPHORE = threading.BoundedSemaphore(value=3)

with EXERCISES_PATH.open(encoding="utf-8") as f:
    raw_exercises = json.load(f)
EXERCISES = {x["id"]: x for x in raw_exercises}
with REFERENCE_PATH.open(encoding="utf-8") as f:
    REFERENCES = json.load(f)


def validate_sql(sql: str) -> str:
    if not isinstance(sql, str) or not sql.strip():
        raise ValueError("Enter a SQL query before submitting.")
    if len(sql) > MAX_SQL_CHARS:
        raise ValueError(f"Query exceeds the {MAX_SQL_CHARS:,}-character limit.")
    try:
        statements = sqlglot.parse(sql, read="postgres")
    except Exception:
        raise ValueError("PostgreSQL could not parse this SQL. Check syntax and column names.") from None
    if len(statements) != 1 or statements[0] is None:
        raise ValueError("Submit exactly one SQL statement at a time.")
    tree = statements[0]
    if not isinstance(tree, exp.Query):
        raise ValueError("Only read-only SELECT queries and SELECT-based CTEs are allowed.")
    for node in tree.walk():
        if isinstance(node, FORBIDDEN_NODES):
            raise ValueError("This query contains a disallowed SQL operation. Use SELECT/CTE only.")
        if isinstance(node, exp.Func) and node.sql_name().upper() in {"PG_READ_FILE", "PG_READ_BINARY_FILE", "PG_LS_DIR", "PG_STAT_FILE"}:
            raise ValueError("Database file-system functions are not allowed.")
    return tree.sql(dialect="postgres")


def connect_db():
    database_url = os.getenv("DATABASE_URL", "").strip()
    if database_url:
        conn = psycopg2.connect(database_url, connect_timeout=5, sslmode="require", application_name="SedukopiSQLPracticeLab")
    else:
        # Optional local development only. Do not use this mode for public deployment.
        required = ["SEDUKOPI_DB_USER", "SEDUKOPI_DB_PASSWORD"]
        missing = [k for k in required if not os.getenv(k)]
        if missing:
            raise RuntimeError("Database credentials are not configured. Set " + ", ".join(missing) + ".")
        conn = psycopg2.connect(
            host=os.getenv("SEDUKOPI_DB_HOST", "127.0.0.1"), port=int(os.getenv("SEDUKOPI_DB_PORT", "5432")),
            dbname=os.getenv("SEDUKOPI_DB_NAME", "sedukopi"), user=os.getenv("SEDUKOPI_DB_USER"),
            password=os.getenv("SEDUKOPI_DB_PASSWORD"), connect_timeout=5, application_name="SedukopiSQLPracticeLab",
        )
    conn.set_session(readonly=True, autocommit=False)
    if REQUIRE_NON_SUPERUSER:
        try:
            with conn.cursor() as cur:
                select_expr = ", ".join(f"has_table_privilege(current_user, 'public.{t}', 'SELECT')" for t in TABLES)
                write_expr = ", ".join(f"has_table_privilege(current_user, 'public.{t}', '{p}')" for t in TABLES for p in WRITE_PRIVILEGES)
                cur.execute("SELECT r.rolsuper, has_database_privilege(current_user, current_database(), 'CREATE'), has_schema_privilege(current_user, 'public', 'CREATE'), " + select_expr + ", " + write_expr + " FROM pg_roles r WHERE r.rolname=current_user")
                row = cur.fetchone()
            if not row:
                raise RuntimeError("Could not verify the configured database role.")
            if row[0]:
                raise RuntimeError("The configured database role is a superuser. Configure the dedicated sedukopi_reader role.")
            if row[1] or row[2]:
                raise RuntimeError("The configured database role can create database/schema objects. Use a read-only role.")
            if not all(row[3:3+len(TABLES)]):
                raise RuntimeError("The configured role must have SELECT access to all five Sedukopi tables in schema public.")
            if any(row[3+len(TABLES):]):
                raise RuntimeError("The configured database role has write-related table privileges. Use a SELECT-only role.")
            conn.rollback()
        except Exception:
            conn.close()
            raise
    return conn


def json_safe(value: Any):
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else str(value)
    if isinstance(value, Decimal):
        return float(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.hex()
    return str(value)


def execute_query(sql: str) -> dict[str, Any]:
    normalized = validate_sql(sql)
    started = time.perf_counter()
    conn = connect_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT set_config('statement_timeout', %s, true)", (f"{QUERY_TIMEOUT_MS}ms",))
            cur.execute("SELECT set_config('lock_timeout', %s, true)", (f"{LOCK_TIMEOUT_MS}ms",))
            cur.execute("SELECT set_config('idle_in_transaction_session_timeout', %s, true)", (f"{QUERY_TIMEOUT_MS + 2000}ms",))
            cur.execute(normalized)
            if cur.description is None:
                raise ValueError("The statement did not return a result set. Submit a SELECT query.")
            columns = [d.name for d in cur.description]
            raw_rows = cur.fetchmany(MAX_ROWS + 1)
            truncated = len(raw_rows) > MAX_ROWS
            raw_rows = raw_rows[:MAX_ROWS]
            rows = [[json_safe(row.get(c)) for c in columns] for row in raw_rows]
            payload = json.dumps({"columns": columns, "rows": rows}, ensure_ascii=False, default=str)
            if len(payload.encode("utf-8")) > MAX_RESULT_BYTES:
                raise ValueError("Result payload is too large. Select fewer columns or rows.")
            conn.rollback()
            return {"columns": columns, "rows": rows, "row_count": len(rows), "column_count": len(columns), "truncated": truncated, "duration_ms": round((time.perf_counter()-started)*1000, 2), "normalized_sql": normalized}
    finally:
        try: conn.rollback()
        except Exception: pass
        conn.close()


def comparable(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return ("number", round(float(value), 6))
    if value is None:
        return ("null",)
    return ("value", str(value))


def compare_results(actual, expected, policy):
    if actual["truncated"] or expected["truncated"]:
        return {"passed": False, "message": "Validation is inconclusive because a result exceeded the row limit."}
    if policy.get("compare_column_names", True) and actual["columns"] != expected["columns"]:
        return {"passed": False, "message": "Result column names or order do not match the expected output.", "expected_columns": expected["columns"], "actual_columns": actual["columns"]}
    if len(actual["rows"]) != len(expected["rows"]):
        return {"passed": False, "message": f"Row count differs: expected {len(expected['rows'])}, received {len(actual['rows'])}."}
    if len(actual["columns"]) != len(expected["columns"]):
        return {"passed": False, "message": "Column count differs from the expected output."}
    a = [tuple(comparable(v) for v in row) for row in actual["rows"]]
    b = [tuple(comparable(v) for v in row) for row in expected["rows"]]
    passed = a == b if policy.get("order_matters", False) else Counter(a) == Counter(b)
    return {"passed": passed, "message": "Correct: your result matches the reference output." if passed else "The query ran, but the result differs from the reference. Check filters, joins, grouping, duplicates, NULLs, and sorting."}


def error_response(message, status, detail=None):
    data = {"error": message}
    if detail: data["detail"] = str(detail)[:300]
    return jsonify(data), status


@app.after_request
def add_cors(response):
    origin = request.headers.get("Origin")
    normalized = origin.rstrip("/") if origin else None
    if normalized and normalized in CORS_ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Max-Age"] = "600"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.errorhandler(413)
def request_too_large(_): return error_response("Request body is too large.", 413)
@app.errorhandler(429)
def rate_limited(_): return error_response("Too many requests. Please wait before trying again.", 429)

@app.get("/")
def root():
    return jsonify({"service":"Sedukopi SQL Practice Lab API", "status":"online", "health":"/health"})

@app.get("/health")
def health():
    conn = None
    try:
        conn = connect_db()
        with conn.cursor() as cur:
            cur.execute("SELECT current_database()")
            name = cur.fetchone()[0]
        conn.rollback()
        return jsonify({"status":"ok", "database":"connected", "database_name":name}), 200
    except Exception:
        app.logger.exception("Health check failed")
        return jsonify({"status":"error", "database":"unavailable"}), 503
    finally:
        if conn:
            try: conn.rollback()
            except Exception: pass
            conn.close()

@app.get("/api/exercises")
def list_exercises():
    return jsonify([{k:v for k,v in exercise.items() if k != "reference_sql"} for exercise in EXERCISES.values()])

@app.get("/api/exercises/<string:exercise_id>/reference")
def reveal_reference(exercise_id):
    if exercise_id not in REFERENCES: return error_response("Unknown exercise ID.", 404)
    return jsonify({"exercise_id":exercise_id, "sql":REFERENCES[exercise_id]["sql"]})


def _run_query(sql):
    try: return execute_query(sql), None
    except ValueError as e: return None, error_response("Query rejected or invalid", 422, str(e))
    except psycopg2.errors.QueryCanceled: return None, error_response("Query timed out. Simplify the query and retry.", 408)
    except psycopg2.errors.LockNotAvailable: return None, error_response("Query could not acquire a required database lock.", 408)
    except psycopg2.ProgrammingError as e: return None, error_response("PostgreSQL rejected the query", 422, str(e).strip())
    except psycopg2.Error as e:
        app.logger.warning("Database query failed: SQLSTATE %s", getattr(e,"pgcode",None))
        return None, error_response("Database query failed. Check column names, permissions, and query complexity.", 422, getattr(e,"pgcode",None))
    except RuntimeError as e: return None, error_response("Database role configuration error", 503, str(e))
    except Exception:
        app.logger.exception("Unexpected query failure")
        return None, error_response("Query execution failed. Check service logs if the problem continues.", 500)

@app.post("/api/query")
@limiter.limit("20 per minute")
def query():
    body = request.get_json(silent=True)
    if not isinstance(body, dict): return error_response("Request body must be JSON.", 400)
    if not isinstance(body.get("sql"), str) or not body["sql"].strip(): return error_response("Enter a SQL query first.", 400)
    if not QUERY_SEMAPHORE.acquire(blocking=False): return error_response("The query service is busy. Retry shortly.", 429)
    try:
        result, err = _run_query(body["sql"].strip())
        if err: return err
        result.pop("normalized_sql", None)
        return jsonify(result)
    finally: QUERY_SEMAPHORE.release()

@app.post("/api/validate")
@limiter.limit("20 per minute")
def validate():
    body = request.get_json(silent=True)
    if not isinstance(body, dict): return error_response("Request body must be JSON.", 400)
    exercise_id = body.get("exercise_id")
    user_sql = body.get("sql", "")
    if not isinstance(exercise_id, str) or exercise_id not in EXERCISES or exercise_id not in REFERENCES: return error_response("Unknown exercise ID.", 404)
    if not isinstance(user_sql, str) or not user_sql.strip(): return error_response("Enter a SQL query first.", 400)
    if not QUERY_SEMAPHORE.acquire(blocking=False): return error_response("The query service is busy. Retry shortly.", 429)
    try:
        expected, err = _run_query(REFERENCES[exercise_id]["sql"])
        if err: return error_response("Reference query validation is unavailable. Check the live schema and database role.", 503)
        actual, err = _run_query(user_sql.strip())
        if err: return err
        comparison = compare_results(actual, expected, REFERENCES[exercise_id].get("policy", {}))
        actual.pop("normalized_sql", None)
        return jsonify({"result":actual, "validation":comparison})
    finally: QUERY_SEMAPHORE.release()

if __name__ == "__main__":
    host = os.getenv("SEDUKOPI_APP_HOST", "127.0.0.1")
    if host not in ("127.0.0.1", "localhost"):
        raise SystemExit("For local development, bind to localhost only; Render runs this app through Gunicorn.")
    app.run(host=host, port=PORT, debug=False)
