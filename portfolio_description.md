# Portfolio Project: Sedukopi SQL Practice Lab

**Category:** SQL Analytics · Python Backend · Database Deployment  
**Live demo:** https://subhanaristiadi.github.io/sedukopi-sql-practice-lab/  
**GitHub:** https://github.com/subhanaristiadi/sedukopi-sql-practice-lab

## Short description

Built and deployed an interactive PostgreSQL practice lab using the Sedukopi dataset. The application includes 47 SQL exercises, live query execution against Neon PostgreSQL, reference-based answer validation, and browser-based progress tracking.

## What I built

- Designed an interactive SQL learning interface using HTML, CSS, and JavaScript.
- Developed a Flask API to execute and validate PostgreSQL queries.
- Connected the API to Neon PostgreSQL and deployed it on Render.
- Implemented SQL parsing and read-only query restrictions, database-role checks, query limits, and rate limiting.
- Added local progress persistence plus JSON import/export.
- Tested successful query execution, rejection of incorrect answer output, rejection of a `DELETE` query, and progress persistence after refresh.

## Stack

PostgreSQL · SQL · Python · Flask · SQLGlot · HTML · CSS · JavaScript · GitHub Pages · Render · Neon

## Outcome

The deployed app successfully returned live outlet data, validated a correct answer, rejected a query with the wrong output schema, blocked a data-deletion statement, and retained completion progress after a page refresh.

**Note:** Progress is saved in the current browser only. Functional testing was performed, but the project has not undergone a comprehensive security audit.
