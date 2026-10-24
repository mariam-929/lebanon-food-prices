# SETUP — run this project locally

This file is written so that an AI coding agent (or a person) can set up and verify the project
without prior context. Follow the steps in order; each has a check that tells you it worked.

For *what* the project is and *why*, read `README.md`. For the source files, read `raw data/README.md`.

---

## 0. What you are setting up

- A **Streamlit** web app (`streamlit_app.py`) with four pages in `app_pages/`.
- It reads only the cleaned CSV tables in `data/` (already committed).
- `pipeline/build_data.py` can rebuild `data/` from the original files in `raw data/`.
- No API keys, secrets, databases or internet access are needed to run it.

## 1. Requirements

- **Python 3.10 or newer** (developed and tested on 3.12). The code uses `X | None` type syntax, so 3.9
  and older will not work.
- **git**
- Any OS. Windows, macOS and Linux all work.

Check:
```bash
python --version        # must print 3.10 or higher (on some systems use python3)
git --version
```

## 2. Get the code

```bash
git clone https://github.com/mariam-929/lebanon-food-prices.git
cd lebanon-food-prices
```

> The folder `raw data/` has a **space** in its name. Quote it in shell commands, e.g. `ls "raw data"`.

## 3. Create an isolated environment and install dependencies

```bash
python -m venv .venv
# activate it:
#   macOS / Linux:        source .venv/bin/activate
#   Windows PowerShell:   .venv\Scripts\Activate.ps1
#   Windows Git Bash:     source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Check:
```bash
python -c "import streamlit, pandas, altair, openpyxl; print('ok', streamlit.__version__)"
```
Streamlit must be **1.57 or newer** (the app uses `st.navigation`, `st.pills`, horizontal containers and
`st.metric(delta_arrow=...)`).

## 4. (Optional) Rebuild the cleaned data from the raw files

Skip this if you only want to run the app; `data/` is already committed. Run it after changing anything
in `raw data/` or in `pipeline/build_data.py`.

```bash
python pipeline/build_data.py
```

Check: it prints one line per table, ending with `world_vs_shelf_monthly.csv  1,062 rows`. With the
committed raw data the rebuild is byte-identical, so `git status` should show no changes in `data/`.

## 5. Verify everything

```bash
python tests/smoke_test.py
```

Check: the last line is `ALL CHECKS PASSED` and the exit code is 0. The test confirms the row counts of
every table in `data/`, a few key numbers quoted in the README, and that every page runs without an
error. Lines like `missing ScriptRunContext! This warning can be ignored` are normal.

## 6. Run the app

```bash
python -m streamlit run streamlit_app.py
```

Then open <http://localhost:8501>. Check: the top navigation shows **Overview, Price monitor,
Import dependence, About the data**, and the Overview page shows four headline figures.

To run it without opening a browser (e.g. on a server or in an agent sandbox):
```bash
python -m streamlit run streamlit_app.py --server.headless true --server.port 8501
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Filename too long` during `git clone` (Windows) | Clone into a short path such as `C:\dev\`, or run `git config --global core.longpaths true` first |
| `ModuleNotFoundError: lib` | Run commands from the repository root, not from `app_pages/` or `tests/` |
| `UnicodeEncodeError` printing Arabic/French text on Windows | Set `PYTHONIOENCODING=utf-8` before running Python |
| `PermissionError` reading an `.xlsx` in `raw data/` | The file is open in Excel; close it. The pipeline also falls back to a temp copy for the World Bank file |
| Dates in `raw data/wfp_food_prices_lbn.csv` look like `15-08-12` | Expected: the file was once saved by Excel. The pipeline parses both `dd-mm-yy` and ISO dates |
| Port 8501 already in use | Add `--server.port 8502` |
| `TypeError: ... unsupported operand type(s) for |` | Python is older than 3.10; upgrade |

## Project map (for agents making changes)

| Path | Role |
|---|---|
| `streamlit_app.py` | Page config and top navigation |
| `app_pages/overview.py` | Headline figures, CPI comparison, US$ change by item, affordability |
| `app_pages/price_monitor.py` | Three flag checks (shelf vs world, governorate gaps, stable-lira rises) |
| `app_pages/import_dependence.py` | Self-sufficiency, import bills, weighted priority screen, supplier countries |
| `app_pages/about.py` | Sources, cleaning, limits, downloads |
| `lib/data.py` | Cached CSV loaders (`st.cache_data`) |
| `lib/charts.py` | Altair chart builders and the colour palette |
| `lib/metrics.py` | Pure-pandas flag and score logic (no Streamlit; easy to test) |
| `pipeline/build_data.py` | Raw → cleaned tables; all cleaning rules live here |
| `tests/smoke_test.py` | Verification script |

Conventions to keep:
- Pages are plain scripts (no `main()`); shared logic goes in `lib/`.
- Use Altair via `st.altair_chart`; never dual y-axes; colours from `lib/charts.py` (`SLOTS`,
  `ORIGIN_SCALE`) so each category keeps the same colour everywhere.
- Price flags are worded as "investigate" / "worth a closer look", never as proof of overcharging.
- Keep the framing economic, not political.
- If you change the data, update the expected numbers in `tests/smoke_test.py` and the figures in `README.md`.

## Deploying (optional)

The app deploys as-is to Streamlit Community Cloud: sign in at <https://share.streamlit.io> with GitHub,
choose **Create app**, select this repository, branch `main`, file `streamlit_app.py`. Every push to
`main` redeploys.
