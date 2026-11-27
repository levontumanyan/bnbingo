# bnbingo

Search, verify, and score Airbnb stays against **your** criteria. CLI-first, Python-based, with review sentiment analysis, image-based amenity checks, and exact checkout pricing.

Unofficial tool — not affiliated with, endorsed by, or connected to Airbnb, Inc.

[![PyPI](https://img.shields.io/pypi/v/bnbingo.svg)](https://pypi.org/project/bnbingo/)

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

No config file is required: every search knob is a CLI flag, and scoring uses a packaged default `benchmarks.json` that ships inside the wheel.

To customize scoring (weights, penalties, hard filters), either:

- put your own `benchmarks.json` in `~/.config/bnbingo/` (override the directory with `BNBINGO_CONFIG_DIR`), or
- pass any file explicitly with `--benchmarks PATH`.

Resolution order is `--benchmarks PATH`, then the config-dir file, then the packaged default. A malformed or missing `--benchmarks` file fails loudly — it never silently scores listings as zero. If you manage dotfiles with stow, keep your personal `benchmarks.json` in your **private** dotfiles repo under `.config/bnbingo/`.

All prices default to CAD on airbnb.ca; pass `--currency` to override. `--check_in` and `--check_out` are required for every mode (a `--room` URL may carry them).

Reports, cache, and logs are separate from config:

- Running from a source checkout: written into the checkout directory
- Installed tool: `BNBINGO_HOME` if set, otherwise `~/.local/share/bnbingo`

`amenities.json` and the default `benchmarks.json` ship inside the Python package — no setup needed.

Optional credentials:

- `GEMINI_API_KEY` in the environment or a gitignored `.env` in your config directory (enables image verification and LLM sentiment)
- `AIRBNB_COOKIE` in the environment or `cookies.txt` in your config directory; otherwise `~/.config/airbnb/cookies.txt` is used if present

# Usage

```bash
# Search a city
bnbingo --location "Lisbon, Portugal" --check_in 2027-01-10 --check_out 2027-01-24

# Per-night cap, scaled to the stay length
bnbingo --location "Lisbon, Portugal" --check_in 2027-01-10 --check_out 2027-01-24 --max_nightly 90

# Whole-stay budget cap, sent as-is
bnbingo --location "Arequipa, Peru" --check_in 2027-01-11 --check_out 2027-02-08 --max_total 1200

# Must-have amenities beyond the benchmarks hard filters
bnbingo --location "Valdivia, Chile" --check_in 2027-05-03 --check_out 2027-05-17 --amenities "wifi,kitchen"

# Multi-city survey (separate cities with ';'; commas inside city names are kept)
bnbingo --survey --cities "Lima, Peru;Buenos Aires, Argentina" --check_in 2027-03-01 --check_out 2027-03-29

# Inspect one listing
bnbingo --room 123456789 --calendar --reviews --check_in 2027-01-10 --check_out 2027-01-24

# Machine-readable output with an explicit scoring policy
bnbingo --location "Valparaíso, Chile" --limit 10 --compact --json --benchmarks ~/my-benchmarks.json

# Consolidated review of a host: every listing, every review
bnbingo --host 482816256 --check_in 2027-01-10 --check_out 2027-02-07
bnbingo --host "https://www.airbnb.ca/h/premium-bed-by-olvia-full-equipped-2" --check_in 2027-01-10 --check_out 2027-02-07 --json --compact
```

`--min_price` / `--max_price` are deprecated aliases for the nightly flags and print a warning.

# Search completeness

A city search geocodes the city name to its administrative bounding box and pages through every listing inside it. Airbnb caps the number of pages it will serve per query, so in dense markets the sweep stops early (`SearchResultsTruncatedWarning`) and listings in any neighborhood — not a specific one — can be missed. Pass `--complete` to subdivide the bounding box until every page fits; it is slower and uses many more requests, but avoids the cap. If the subdivision budget is exhausted, the partial results are still returned with a warning.

# Host review

`--host` accepts a numeric host ID or an Airbnb `/h/...`, `/users/...`, or `/rooms/...` URL. It enumerates every listing owned by that host, fetches all reviews across them, and prints a per-listing breakdown (with full `airbnb.ca` links and CAD total + nightly prices), overall rating distribution, total review count cross-checked against the listing counts, review date range, and recurring praise/issue themes. Listings whose house rules or description restrict visitors are flagged. `--json` keeps the whole report machine-readable; `--compact` drops the individual review texts.

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
