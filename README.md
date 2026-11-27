# bnbingo

Search, verify, and score Airbnb stays against **your** criteria. CLI-first, Python-based, with review sentiment analysis, image-based amenity checks, and exact checkout pricing.

Unofficial tool — not affiliated with, endorsed by, or connected to Airbnb, Inc.

# Features

- Search Airbnb with dates, guests, price, property type, amenities, and neighborhood filters
- Fetch exact fee-inclusive checkout prices (with a clear warning when Airbnb withholds them)
- Pull listing details, calendars, and reviews
- Score listings with weighted metrics, penalties, and hard filters you define
- Review sentiment analysis, including Spanish noise/cleanliness signals
- Optional Gemini image verification (is that "workspace" actually a desk?)
- Verified fast Wi-Fi detection and climate enrichment
- Multi-city market survey mode for comparing destinations
- Compact table, CSV, and JSON reports

# Install

From PyPI (recommended):

```bash
uv tool install bnbingo
bnbingo --help
```

`uvx bnbingo --help` runs it without installing. Alternatives: `pipx install bnbingo`, or a venv with `python3 -m venv .venv && . .venv/bin/activate && pip install bnbingo`. Prefer a venv or tool installer over a global `pip install`.

From a source checkout:

```bash
uv tool install --force .
bnbingo --help
```

For development, use `uv sync` and `uv run bnbingo --help`.

# Setup

Your filters and benchmarks are personal and live **outside this repo**. Only the random example files are tracked here.

Config files are read from `~/.config/bnbingo` (override the directory with `BNBINGO_CONFIG_DIR`):

```bash
mkdir -p ~/.config/bnbingo
cp search_filters.example.json ~/.config/bnbingo/search_filters.json
cp benchmarks.example.json ~/.config/bnbingo/benchmarks.json
```

Then edit those two files to match your own trip defaults and scoring weights:

- `search_filters.json` — `defaults` (location bounds, dates, guests, price, amenities) and optional `amenity_ids`
- `benchmarks.json` — `metrics` (weights + scoring functions), `penalties`, `hard_filters`, `scoring_thresholds`

If you manage dotfiles with stow, keep those two files in your **private** dotfiles repo under `.config/bnbingo/` — stow links them into `~/.config/bnbingo` on install, so a fresh machine restores them automatically.

Reports, cache, and logs are separate from config:

- Running from a source checkout: written into the checkout directory
- Installed tool: `BNBINGO_HOME` if set, otherwise `~/.local/share/bnbingo`

`amenities.json` ships inside the Python package — no setup needed.

Optional credentials:

- `GEMINI_API_KEY` in the environment or a gitignored `.env` in your config directory (enables image verification and LLM sentiment)
- `AIRBNB_COOKIE` in the environment or `cookies.txt` in your config directory; otherwise `~/.config/airbnb/cookies.txt` is used if present

# Usage

```bash
# Search with your saved defaults
bnbingo

# Per-night cap, scaled to the stay length
bnbingo --location "Lisbon, Portugal" --check_in 2027-01-10 --check_out 2027-01-24 --max_nightly 90

# Whole-stay budget cap, sent as-is
bnbingo --location "Arequipa, Peru" --check_in 2027-01-11 --check_out 2027-02-08 --max_total 1200

# Multi-city survey (separate cities with ';'; commas inside city names are kept)
bnbingo --survey --cities "Lima, Peru;Buenos Aires, Argentina" --check_in 2027-03-01 --check_out 2027-03-29

# Inspect one listing
bnbingo --room 123456789 --calendar --reviews

# Machine-readable output
bnbingo --location "Valparaíso, Chile" --limit 10 --compact --json
```

`--min_price` / `--max_price` are deprecated aliases for the nightly flags and print a warning.

# Price filter semantics

Airbnb's search API applies `price_max` to a whole-stay figure, so nightly caps are multiplied by the number of nights before being sent. Its server-side filter is loose, though: listings above the requested cap can still come back. `bnbingo` therefore re-checks the fetched exact total against the requested range and skips listings outside it, in both search and survey mode. Listings whose exact price could not be fetched are kept (their search-API estimate is used) rather than dropped silently.

Price caps apply to the whole-stay total including fees. A listing with a missing price is not counted against the cap.

# Reports and cache

Reports (CSV/JSON), cached listings, and logs live in the data directory (source checkout root, `BNBINGO_HOME`, or `~/.local/share/bnbingo`) and are gitignored. Reports merge across runs for the same location and dates; `--json` output is filtered by the current run's price caps, so older over-budget rows do not appear as results. Cookies live in the config directory and are never tracked.

# MCP wrapper (roadmap)

The CLI stays the primary interface. If an MCP wrapper is added, it will live in this repo as an optional extra and expose small tools (`search`, `listing_details`, `survey`) that call the library functions directly — not by shelling out to the CLI. Long searches are better suited to a CLI than to blocking MCP tool calls.

# Development

```bash
uv sync
uv run pytest
make lint
make check
make setup   # install the lint/test pre-commit hook
```

Releases are tag-driven via GitHub Actions; see [RELEASING.md](RELEASING.md).

# License

MIT — see `LICENSE`.
