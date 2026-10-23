# Exercise coverage matrix

This matrix maps the included exercise set to the documented ten business questions. The exercise definitions and SQL are proposed implementation artifacts, not verified query results. Run them against the live PostgreSQL database before treating an exercise as validated.

| Business question | Exercise IDs | Objective / core SQL | Tables | Expected output | Validation |
|---|---|---|---|---|---|
| #1 Ranking Revenue per Gerai | REV-01–REV-05 | Revenue aggregation, eligible outlet population, ranking, status distribution | `orders`, `outlets` | Revenue by outlet, ranks, stored status counts | Result comparison; inspect status values and zero-order outlets |
| #2 Menu Terlaris per Kategori | MENU-01–MENU-05 | Quantity sold, category aggregation, top-per-category ranking, unsold items | `menu_items`, `order_details` | Sales by item/category, top items, availability counts | Result comparison; verify category and quantity data |
| #3 Jam Ramai (Peak Hour) | PEAK-01–PEAK-04 | Extract hour, count orders, revenue and average order amount | `orders` | Hourly orders and metrics | Result comparison; verify time range and null times |
| #4 Tren Revenue Bulanan 2022–2025 | TREND-01–TREND-04 | Monthly aggregation, `LAG`, period comparisons | `orders` | Monthly revenue, order counts, period deltas | Result comparison; inspect actual date coverage and incomplete periods |
| #5 Pergeseran Metode Bayar dari Tahun ke Tahun | PAY-01–PAY-04 | Payment method grouping, year trends, conditional percentage / window aggregation | `orders` | Payment method counts, revenue and yearly shares | Result comparison; inspect stored payment method values |
| #6 AOV per Tipe Order | AOV-01–AOV-03 | Average, median, top order type | `orders` | AOV, volume, median by type | Result comparison; define population and inspect outliers |
| #7 Kontribusi Revenue tiap Menu | CONTR-01–CONTR-04 | Detail subtotal, contribution %, cumulative share, subtotal consistency | `order_details`, `menu_items` | Menu revenue and contribution | Result comparison; reconcile detail subtotal with order-level revenue before interpretation |
| #8 Menu Engineering Matrix (Boston Matrix) | ENG-01–ENG-03 | Listed unit margin, sales quantity, explicit median-based popularity segmentation | `menu_items`, `order_details` | Margin estimates and popularity segment | Result comparison; thresholds are data-relative and not universal |
| #9 Cross-Sell: Item yang Sering Dibeli Bareng | CROSS-01–CROSS-02 | Self-join, unique unordered item pairs, count orders together | `order_details`, `menu_items` | Co-purchased item pairs | Result comparison; distinct item presence per order prevents quantity duplicates |
| #10 Efisiensi Gerai: Revenue per Staff vs Turnover | EFF-01–EFF-03 | Staff status counts, revenue per staff record, order attribution | `orders`, `outlets`, `staff` | Outlet staffing and recorded revenue ratios | Result comparison; ratio is not a full efficiency metric; staffing period needs definition |
| SQL fundamentals and data quality | FND-01–FND-05, DQ-01–DQ-03 | Projection, filtering, distinct, subquery, NULL, aggregate diagnostics | Relevant individual tables | Basic query outputs and data-quality summaries | Result comparison and manual inspection |

## Curriculum skill mapping

`curriculum_topics.json` maps 21 parent learning topics to the relevant exercise IDs and learning objectives. The sidebar groups exercises by business-analysis theme, while this file provides the SQL skill progression.

## Count
- Parent learning topics: 21 (see `curriculum_topics.json`).
- Independently answerable exercises: 47.
- Business-question coverage: all 10 are represented.
- Completion status: **not verified**. No analysis should be marked complete until its reference SQL executes successfully, results are checked, and business interpretation is documented.

| Staff Salary Analysis | SAL-01–SAL-02 | Average monthly salary by role and outlet | `staff`, `outlets` | Staff counts and average recorded monthly salary | Requires `staff.monthly_salary` to be present in the live PostgreSQL schema |
