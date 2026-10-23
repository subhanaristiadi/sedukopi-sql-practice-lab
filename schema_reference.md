# Sedukopi hosted schema reference

This describes the schema created by `seed_neon.py` from the **supplied CSV files** for the hosted Neon practice database. It is not a live introspection of the user's local PostgreSQL database. The CSV headers are the import source of truth for this hosted copy.

## `outlets` — 20 rows expected

| Column | Type | Key / note |
|---|---|---|
| `outlet_id` | `VARCHAR(10)` | Primary key |
| `name` | `VARCHAR(150)` | |
| `city` | `VARCHAR(100)` | |
| `province` | `VARCHAR(100)` | |
| `address` | `TEXT` | |
| `manager_name` | `VARCHAR(100)` | |
| `opening_date` | `DATE` | |
| `status` | `VARCHAR(20)` | |
| `seating_capacity` | `INTEGER` | |

## `staff` — 120 rows expected

| Column | Type | Key / note |
|---|---|---|
| `staff_id` | `VARCHAR(10)` | Primary key |
| `name` | `VARCHAR(150)` | |
| `role` | `VARCHAR(100)` | |
| `outlet_id` | `VARCHAR(10)` | Foreign key to `outlets.outlet_id` |
| `hire_date` | `DATE` | |
| `monthly_salary` | `NUMERIC(12,2)` | Present in `staff.csv` |
| `status` | `VARCHAR(20)` | |

## `menu_items` — 80 rows expected

| Column | Type | Key / note |
|---|---|---|
| `item_id` | `VARCHAR(10)` | Primary key |
| `name` | `VARCHAR(150)` | |
| `category` | `VARCHAR(100)` | |
| `price` | `NUMERIC(12,2)` | |
| `cost_price` | `NUMERIC(12,2)` | |
| `is_available` | `BOOLEAN` | |
| `calories` | `INTEGER` | |

## `orders` — 5,000 rows expected

| Column | Type | Key / note |
|---|---|---|
| `order_id` | `VARCHAR(10)` | Primary key |
| `outlet_id` | `VARCHAR(10)` | Foreign key to `outlets.outlet_id` |
| `order_date` | `DATE` | |
| `order_time` | `TIME` | |
| `total_amount` | `NUMERIC(12,2)` | Order-level amount |
| `payment_method` | `VARCHAR(50)` | |
| `order_type` | `VARCHAR(50)` | |
| `staff_id` | `VARCHAR(10)` | Foreign key to `staff.staff_id` |

## `order_details` — 8,123 rows expected

| Column | Type | Key / note |
|---|---|---|
| `detail_id` | `VARCHAR(10)` | Primary key |
| `order_id` | `VARCHAR(10)` | Foreign key to `orders.order_id` |
| `item_id` | `VARCHAR(10)` | Foreign key to `menu_items.item_id` |
| `quantity` | `INTEGER` | |
| `unit_price` | `NUMERIC(12,2)` | |
| `subtotal` | `NUMERIC(12,2)` | Order-detail line amount |
| `notes` | `TEXT` | |

## Relationships

```text
outlets 1 ──< staff
outlets 1 ──< orders >── 1 staff
orders 1 ──< order_details >── 1 menu_items
```

## Schema differences to be aware of

The supplied `staff.csv` header has `monthly_salary` and does not have `phone`. The supplied `orders.csv` does not have `customer_name`. The hosted copy intentionally follows the five CSV headers so the import process is reproducible. Check the live database separately if comparing it with a pre-existing local schema.
