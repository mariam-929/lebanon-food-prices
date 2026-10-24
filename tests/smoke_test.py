"""Smoke test: checks the cleaned data against known values and runs every page headlessly.

Run from the repository root:  python tests/smoke_test.py
Exit code 0 = everything passed.
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DATA = ROOT / "data"
failures: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{' - ' + detail if detail else ''}")
    if not ok:
        failures.append(name)


# 1. cleaned tables exist and have the expected size
EXPECTED_ROWS = {
    "prices_governorate_monthly.csv": 17_063, "prices_national_monthly.csv": 2_279,
    "world_vs_shelf_monthly.csv": 1_062, "cpi_monthly.csv": 3_620, "fx_monthly.csv": 176,
    "items.csv": 29, "affordability_yearly.csv": 9, "trade_yearly.csv": 548,
    "self_sufficiency_yearly.csv": 90, "unido_screen.csv": 12, "imports_by_partner.csv": 930,
}
for f, n in EXPECTED_ROWS.items():
    path = DATA / f
    rows = len(pd.read_csv(path)) if path.exists() else -1
    check(f"data/{f} rows", rows == n, f"got {rows}, expected {n}")

# 2. key numbers quoted in the README
cpi = pd.read_csv(DATA / "cpi_monthly.csv", parse_dates=["month"]).pivot_table(
    index="month", columns="division", values="index_dec2013_100")
food = cpi.loc["2026-08-01", "Food and non-alcoholic beverages"] / cpi.loc["2019-12-01", "Food and non-alcoholic beverages"]
check("food CPI multiple Dec 2019 -> Aug 2026 is ~304", abs(food - 304) < 1, f"{food:.1f}")

nat = pd.read_csv(DATA / "prices_national_monthly.csv", parse_dates=["month"])
sugar = nat[(nat.commodity == "Sugar (white)") & (nat.month == "2026-03-01")].price_usd_std.iloc[0]
check("sugar shelf price Mar 2026 ~ US$0.94/kg (USD recomputed at market rate)", abs(sugar - 0.94) < 0.01, f"{sugar:.3f}")

screen = pd.read_csv(DATA / "unido_screen.csv").set_index("group")
lent = screen.loc["Lentils", "self_sufficiency"]
check("lentil self-sufficiency ~14%", abs(lent - 0.143) < 0.005, f"{lent:.3f}")

# 3. every page runs without an exception
from streamlit.testing.v1 import AppTest  # noqa: E402

for page in ["app_pages/overview.py", "app_pages/price_monitor.py", "app_pages/import_dependence.py",
             "app_pages/about.py", "streamlit_app.py"]:
    at = AppTest.from_file(str(ROOT / page), default_timeout=120)
    at.run()
    errs = [str(e.value)[:200] for e in at.exception]
    check(f"{page} runs", not errs, "; ".join(errs))

print(f"\n{'ALL CHECKS PASSED' if not failures else f'{len(failures)} CHECK(S) FAILED: ' + ', '.join(failures)}")
sys.exit(1 if failures else 0)
