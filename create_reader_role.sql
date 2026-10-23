-- Run in Neon SQL Editor as the project owner/admin AFTER seed_neon.py succeeds.
-- Replace the password placeholder yourself. Do not commit a real password.
CREATE ROLE sedukopi_reader LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT
  PASSWORD 'REPLACE_WITH_A_UNIQUE_STRONG_PASSWORD';
GRANT CONNECT ON DATABASE neondb TO sedukopi_reader;
GRANT USAGE ON SCHEMA public TO sedukopi_reader;
GRANT SELECT ON TABLE public.outlets, public.staff, public.menu_items, public.orders, public.order_details
  TO sedukopi_reader;
