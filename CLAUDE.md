# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Saude Pessoal** — a personal health application for personal health tracking.

**Stack:** FastAPI + SQLAlchemy (SQLite) + Jinja2 templates, Python 3.12

**To run:** `start.bat` (or `python run.py`) → opens browser at http://127.0.0.1:8080

**Domains:**
- `app/domains/blood_pressure/` — tensão arterial (`/tensao-arterial`)
- `app/domains/weight/` — peso (`/peso`)
- `app/domains/urinary/` — urologia (`/urologia`)

Each domain follows the same structure: `models.py`, `schemas.py`, `service.py`, `router.py`.
Templates live in `app/templates/<domain>/` (list, form, charts).

**Key behaviors confirmed by testing:**
- BP form classifies in real-time (OMS table visible on the right)
- Charts support period filters: 7 dias / 30 dias / 3 meses / 1 ano
- Dashboard shows cards + recent BP table; updates immediately after new records
- All pages are mobile-responsive
- Urinary form uses only select/radio inputs (no free-text number fields)
- Export page exists at `/exportar`

**Known gotcha — Jinja2 in Alpine.js attributes:**
Escaped quotes (`\'`) inside `{{ }}` expressions are invalid in Jinja2.
When building Alpine.js `@click` strings that include formatted dates, pre-format
with `{% set label = ... ~ obj.field.strftime('%d/%m/%Y') %}` and reference
`{{ label }}` in the attribute. All three `list.html` templates already use this pattern.

## Design System

Design tokens were extracted from finantech.pt using the `extract-design-system` skill and live in `design-system/`:

- `tokens.json` — source-of-truth token data (spacing scale, typography fonts)
- `tokens.css` — CSS custom properties ready to import

**Typography:** `GothamRoundedMedium` for both headings and body text.

**Spacing scale** (`--space-1` through `--space-20`): ranges from 2px to 140px. Use these variables rather than hardcoding pixel values.

Color palette was defined directly in `static/css/main.css` (CSS custom properties under `:root`).
Primary: `#1B5EA6`, Secondary: `#0891B2`. Do not edit `tokens.json` for colors — use `main.css`.
