"""Create/populate a fresh Neon database from the five supplied Sedukopi CSV files.

Run locally after setting SEDUKOPI_SEED_DATABASE_URL to a Neon OWNER/admin connection string.
This script refuses to proceed if any target tables already exist. It does not drop tables.
"""
import csv, os, sys, getpass
from pathlib import Path
import psycopg2

BASE = Path(__file__).resolve().parent
CSV_DIR = Path(os.getenv("SEDUKOPI_CSV_DIR", str(BASE / "data"))).resolve()
URL = os.getenv("SEDUKOPI_SEED_DATABASE_URL", "").strip()
TABLE_FILES = {
    "outlets": ("outlets.csv", "outlet_id, name, city, province, address, manager_name, opening_date, status, seating_capacity"),
    "staff": ("staff.csv", "staff_id, name, role, outlet_id, hire_date, monthly_salary, status"),
    "menu_items": ("menu_items.csv", "item_id, name, category, price, cost_price, is_available, calories"),
    "orders": ("orders.csv", "order_id, outlet_id, order_date, order_time, total_amount, payment_method, order_type, staff_id"),
    "order_details": ("order_details.csv", "detail_id, order_id, item_id, quantity, unit_price, subtotal, notes"),
}
DDL = [
"""CREATE TABLE public.outlets (
 outlet_id VARCHAR(10) PRIMARY KEY, name VARCHAR(150), city VARCHAR(100), province VARCHAR(100),
 address TEXT, manager_name VARCHAR(100), opening_date DATE, status VARCHAR(20), seating_capacity INTEGER
)""",
"""CREATE TABLE public.staff (
 staff_id VARCHAR(10) PRIMARY KEY, name VARCHAR(150), role VARCHAR(100), outlet_id VARCHAR(10),
 hire_date DATE, monthly_salary NUMERIC(12,2), status VARCHAR(20),
 CONSTRAINT staff_outlet_fk FOREIGN KEY (outlet_id) REFERENCES public.outlets(outlet_id)
)""",
"""CREATE TABLE public.menu_items (
 item_id VARCHAR(10) PRIMARY KEY, name VARCHAR(150), category VARCHAR(100), price NUMERIC(12,2),
 cost_price NUMERIC(12,2), is_available BOOLEAN, calories INTEGER
)""",
"""CREATE TABLE public.orders (
 order_id VARCHAR(10) PRIMARY KEY, outlet_id VARCHAR(10), order_date DATE, order_time TIME,
 total_amount NUMERIC(12,2), payment_method VARCHAR(50), order_type VARCHAR(50), staff_id VARCHAR(10),
 CONSTRAINT orders_outlet_fk FOREIGN KEY (outlet_id) REFERENCES public.outlets(outlet_id),
 CONSTRAINT orders_staff_fk FOREIGN KEY (staff_id) REFERENCES public.staff(staff_id)
)""",
"""CREATE TABLE public.order_details (
 detail_id VARCHAR(10) PRIMARY KEY, order_id VARCHAR(10), item_id VARCHAR(10), quantity INTEGER,
 unit_price NUMERIC(12,2), subtotal NUMERIC(12,2), notes TEXT,
 CONSTRAINT order_details_order_fk FOREIGN KEY (order_id) REFERENCES public.orders(order_id),
 CONSTRAINT order_details_item_fk FOREIGN KEY (item_id) REFERENCES public.menu_items(item_id)
)""",
]
EXPECTED = {"outlets":20,"staff":120,"menu_items":80,"orders":5000,"order_details":8123}

def main():
    url = URL or getpass.getpass("Paste Neon owner connection string (input hidden): ").strip()
    if not url:
        sys.exit("No Neon connection string supplied; no database changes were made.")
    for table,(filename,_cols) in TABLE_FILES.items():
        p=CSV_DIR/filename
        if not p.is_file(): sys.exit(f"Missing file: {p}. Set SEDUKOPI_CSV_DIR to the folder containing all five CSVs.")
        with p.open(encoding="utf-8-sig", newline="") as fp:
            reader=csv.DictReader(fp)
            got=list(reader.fieldnames or [])
            expected=[x.strip() for x in _cols.split(",")]
            if got != expected:
                sys.exit(f"Unexpected header in {filename}: {got}; expected {expected}. No database changes were made.")
    conn=psycopg2.connect(url, sslmode="require", connect_timeout=10, application_name="SedukopiNeonSeeder")
    try:
        conn.autocommit=False
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user")
            db,user=cur.fetchone()
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name = ANY(%s)", (list(TABLE_FILES),))
            existing=[r[0] for r in cur.fetchall()]
            if existing:
                raise RuntimeError(f"Safety stop: these target tables already exist in {db}: {', '.join(existing)}. Use a fresh empty Neon database; this script never drops tables.")
            print(f"Connected to database {db} as {user}. Creating fresh Sedukopi tables...")
            for ddl in DDL: cur.execute(ddl)
            for table,(filename, cols) in TABLE_FILES.items():
                path=CSV_DIR/filename
                with path.open("r", encoding="utf-8-sig", newline="") as fp:
                    cur.copy_expert(f"COPY public.{table} ({cols}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE, ENCODING 'UTF8')", fp)
                cur.execute(f"SELECT COUNT(*) FROM public.{table}")
                n=cur.fetchone()[0]
                if n != EXPECTED[table]: raise RuntimeError(f"Row count mismatch for {table}: expected {EXPECTED[table]}, loaded {n}.")
                print(f"  {table}: {n} rows")
            cur.execute("SELECT COUNT(*) FROM public.staff s LEFT JOIN public.outlets o ON s.outlet_id=o.outlet_id WHERE o.outlet_id IS NULL")
            if cur.fetchone()[0]: raise RuntimeError("Orphan staff.outlet_id values detected.")
            cur.execute("SELECT COUNT(*) FROM public.orders x LEFT JOIN public.outlets o ON x.outlet_id=o.outlet_id LEFT JOIN public.staff s ON x.staff_id=s.staff_id WHERE o.outlet_id IS NULL OR s.staff_id IS NULL")
            if cur.fetchone()[0]: raise RuntimeError("Orphan orders foreign keys detected.")
            cur.execute("SELECT COUNT(*) FROM public.order_details d LEFT JOIN public.orders o ON d.order_id=o.order_id LEFT JOIN public.menu_items m ON d.item_id=m.item_id WHERE o.order_id IS NULL OR m.item_id IS NULL")
            if cur.fetchone()[0]: raise RuntimeError("Orphan order_details foreign keys detected.")
        conn.commit()
        print("\nSUCCESS: all five tables loaded and foreign-key orphan checks passed.")
        print("Next: run create_reader_role.sql in Neon SQL Editor, then configure Render DATABASE_URL with the reader role.")
    except Exception as exc:
        conn.rollback()
        print(f"FAILED; the transaction was rolled back. {exc}", file=sys.stderr)
        sys.exit(1)
    finally: conn.close()
if __name__ == "__main__": main()
