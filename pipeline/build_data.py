"""Build the cleaned tables used by the dashboard (and reusable in Tableau).

Reads the raw files in ../raw data/ and writes tidy CSVs to ../data/.
Run:  python pipeline/build_data.py
"""
from pathlib import Path
import re
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw data"
OUT = ROOT / "data"
OUT.mkdir(exist_ok=True)

GOVERNORATES = ["Akkar", "Baalbek-El Hermel", "Beirut", "Bekaa", "El Nabatieh", "Mount Lebanon", "North", "South"]

# ---------------------------------------------------------------- item metadata
# origin_class is assigned at the food-type level (not per product). Basis is documented per item.
ORIGIN = {
    "Rice (imported, Egyptian)": ("Mostly imported", "No domestic rice production recorded (FAOSTAT)"),
    "Sugar (white)": ("Mostly imported", "Domestic sugar-beet output ~10k t vs >100k t refined-sugar imports"),
    "Tea": ("Mostly imported", "No domestic tea production recorded (FAOSTAT)"),
    "Milk (powder)": ("Mostly imported", "No domestic milk-powder production recorded; US$35-45M imports/yr"),
    "Oil (sunflower)": ("Mostly imported", "Domestic crude sunflower oil 2-6k t vs ~US$140M imports/yr"),
    "Lentils": ("Mostly imported", "Self-sufficiency ~15% (FAOSTAT + Comtrade)"),
    "Lentils (green)": ("Mostly imported", "Self-sufficiency ~15% (FAOSTAT + Comtrade)"),
    "Lentils (red)": ("Mostly imported", "Self-sufficiency ~15% (FAOSTAT + Comtrade)"),
    "Chickpeas": ("Mostly imported", "Self-sufficiency ~18% (FAOSTAT + Comtrade)"),
    "Beans (white)": ("Mostly imported", "Self-sufficiency ~38% (FAOSTAT + Comtrade)"),
    "Fish (tuna, canned)": ("Mostly imported", "Imported processed product"),
    "Fish (sardine, canned)": ("Mostly imported", "Imported processed product"),
    "Meat (beef, canned)": ("Mostly imported", "Imported processed product"),
    "Cheese (picon)": ("Mostly imported", "Imported branded product"),
    "Bread (pita)": ("Locally processed / mixed", "Baked locally from imported wheat (wheat self-sufficiency ~18%)"),
    "Wheat flour": ("Locally processed / mixed", "Milled locally from imported wheat"),
    "Pasta (spaghetti)": ("Locally processed / mixed", "Made locally and imported, from imported wheat"),
    "Bulgur (brown)": ("Locally processed / mixed", "Processed locally from mostly imported wheat"),
    "Tomatoes (paste)": ("Locally processed / mixed", "Local tomatoes and imported paste"),
    "Salt": ("Locally processed / mixed", "Some local sea salt, some imports"),
    "Cabbage": ("Mostly local", "Self-sufficiency ~95% (FAOSTAT + Comtrade)"),
    "Cucumbers (greenhouse)": ("Mostly local", "Self-sufficiency ~100% (FAOSTAT + Comtrade)"),
    "Potatoes": ("Mostly local", "Self-sufficiency ~95-100% (FAOSTAT + Comtrade)"),
    "Apples": ("Mostly local", "Net exporter (FAOSTAT + Comtrade)"),
    "Carrots": ("Mostly local", "Self-sufficiency ~65% (FAOSTAT + Comtrade)"),
    "Eggs": ("Mostly local", "Negligible imports (Comtrade)"),
    "Lettuce": ("Mostly local", "Fresh local produce"),
    "Spinach": ("Mostly local", "Fresh local produce"),
    "Meat (chicken, whole, frozen)": ("Mostly local", "Domestic production ~137k t vs small imports"),
}
REGULATED = {"Bread (pita)"}  # government-set price: excluded from pricing flags

# unit string -> (quantity, standard unit label)
UNITS = {
    "KG": (1, "kg"), "5 KG": (5, "kg"), "900 G": (0.9, "kg"), "800 G": (0.8, "kg"), "750 G": (0.75, "kg"),
    "700 G": (0.7, "kg"), "660 G": (0.66, "kg"), "500 G": (0.5, "kg"), "200 G": (0.2, "kg"),
    "185 G": (0.185, "kg"), "160 G": (0.16, "kg"), "125 G": (0.125, "kg"),
    "5 L": (5, "litre"), "30 pcs": (30, "egg"), "Head": (1, "head"),
    "20 L": (20, "litre"), "10 KG": (10, "kg"),
}


def parse_wfp_dates(s: pd.Series) -> pd.Series:
    """WFP dates arrive as ISO (2012-08-15) or, after an Excel save, as dd-mm-yy (15-08-12)."""
    iso = pd.to_datetime(s, format="%Y-%m-%d", errors="coerce")
    short = pd.to_datetime(s, format="%d-%m-%y", errors="coerce")
    out = iso.fillna(short)
    assert out.notna().all(), "unparsed WFP dates"
    return out


# ---------------------------------------------------------------- exchange rate
def build_fx() -> pd.Series:
    rt = pd.read_csv(RAW / "real-time-currency-prices-for-lebanon.csv", low_memory=False)
    rt = rt[rt["mkt_name"] == "Market Average"]
    rtp = pd.Series(rt["exchange_rate_unofficial"].values, index=pd.PeriodIndex(rt["DATES"], freq="M"))

    w = pd.read_csv(RAW / "wfp_food_prices_lbn.csv")
    w["month"] = parse_wfp_dates(w["date"]).dt.to_period("M")
    wfx = w[w["commodity"] == "Exchange rate (unofficial)"].groupby("month")["price"].median()

    fx = rtp.copy()
    fx.loc[wfx.index] = wfx  # WFP's observed parallel rate wins where it exists (May 2020 onward)
    fx = fx.sort_index()
    src = pd.Series("World Bank RTP estimate", index=fx.index)
    src.loc[wfx.index] = "WFP observed"
    pd.DataFrame({"month": fx.index.to_timestamp(), "lbp_per_usd": fx.values, "source": src.values}).to_csv(
        OUT / "fx_monthly.csv", index=False)
    return fx


# ---------------------------------------------------------------- retail prices
def build_prices(fx: pd.Series) -> pd.DataFrame:
    w = pd.read_csv(RAW / "wfp_food_prices_lbn.csv")
    w["month"] = parse_wfp_dates(w["date"]).dt.to_period("M")
    w = w[(w["category"] != "non-food") & (w["priceflag"] == "actual")].copy()

    qty = w["unit"].map(lambda u: UNITS[u][0])
    w["std_unit"] = w["unit"].map(lambda u: UNITS[u][1])
    w["price_lbp_std"] = w["price"] / qty
    w["lbp_per_usd"] = w["month"].map(fx)
    w["price_usd_std"] = w["price_lbp_std"] / w["lbp_per_usd"]  # replaces WFP's official-rate usdprice

    # Governorate median per month. Harmonises the 2025 break (27 district markets -> 8 governorates).
    gov = (w.groupby(["month", "admin1", "commodity", "category", "std_unit"])
             .agg(price_lbp_std=("price_lbp_std", "median"), price_usd_std=("price_usd_std", "median"),
                  n_markets=("market", "nunique"))
             .reset_index())
    gov["origin_class"] = gov["commodity"].map(lambda c: ORIGIN[c][0])
    gov["regulated_price"] = gov["commodity"].isin(REGULATED)
    gov["month"] = gov["month"].dt.to_timestamp()
    gov.to_csv(OUT / "prices_governorate_monthly.csv", index=False)

    # National = median of governorate medians (consistent across the coverage break).
    nat = (gov.groupby(["month", "commodity", "category", "std_unit", "origin_class", "regulated_price"])
              .agg(price_lbp_std=("price_lbp_std", "median"), price_usd_std=("price_usd_std", "median"),
                   n_governorates=("admin1", "nunique"))
              .reset_index())
    nat.to_csv(OUT / "prices_national_monthly.csv", index=False)

    items = pd.DataFrame([(c, *ORIGIN[c], c in REGULATED) for c in sorted(gov["commodity"].unique())],
                         columns=["commodity", "origin_class", "origin_basis", "regulated_price"])
    span = nat.groupby("commodity")["month"].agg(first_month="min", last_month="max").reset_index()
    items.merge(span, on="commodity").to_csv(OUT / "items.csv", index=False)
    return nat


# ---------------------------------------------------------------- world prices
WORLD = {  # WFP item -> (Pink Sheet column, divisor to $/kg, shelf-unit -> kg factor, note)
    "Rice (imported, Egyptian)": ("Rice, Thai 5%", 1000, 1, "Thai 5% broken is the closest world benchmark; shelf item is Egyptian rice"),
    "Sugar (white)": ("Sugar, world", 1, 1, ""),
    "Oil (sunflower)": ("Sunflower oil", 1000, 1 / 0.92, "Shelf price per litre converted at 0.92 kg/L"),
    "Wheat flour": ("Wheat, US HRW", 1000, 1, "World price is for wheat grain, shelf item is flour"),
    "Tea": ("Tea, avg 3 auctions", 1, 1, "Auction price for bulk tea; shelf item is packaged tea"),
    "Meat (chicken, whole, frozen)": ("Chicken **", 1, 1, ""),
}


def read_excel_unlocked(path: Path, **kw) -> pd.DataFrame:
    """Excel/OneDrive lock files the user has open; fall back to reading a temp copy."""
    try:
        return pd.read_excel(path, **kw)
    except PermissionError:
        import shutil, tempfile
        tmp = Path(tempfile.gettempdir()) / f"copy_{path.name}"
        shutil.copyfile(path, tmp)
        return pd.read_excel(tmp, **kw)


def build_world(nat: pd.DataFrame) -> None:
    p = read_excel_unlocked(RAW / "world_bank_commodity_prices" / "CMO-Historical-Data-Monthly.xlsx",
                            sheet_name="Monthly Prices", header=None)
    hdr = p.iloc[4].fillna("").astype(str).str.strip().tolist()
    body = p.iloc[6:].copy()
    body.columns = ["m"] + hdr[1:]
    body["month"] = pd.PeriodIndex(body["m"].str.replace("M", "-"), freq="M").to_timestamp()

    rows = []
    for item, (col, div, kg_factor, note) in WORLD.items():
        world = pd.to_numeric(body.set_index("month")[col], errors="coerce") / div
        shelf = nat[nat["commodity"] == item].set_index("month")["price_usd_std"] * kg_factor
        df = pd.DataFrame({"world_usd_per_kg": world, "shelf_usd_per_kg": shelf}).dropna(how="all")
        df = df[df.index >= "2012-01-01"]
        df["commodity"], df["benchmark"], df["note"] = item, col, note
        rows.append(df.reset_index().rename(columns={"index": "month"}))
    pd.concat(rows).to_csv(OUT / "world_vs_shelf_monthly.csv", index=False)


# ---------------------------------------------------------------- CPI
MONTHS = {m: i for i, m in enumerate(["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"], 1)}


def build_cpi() -> None:
    d = pd.read_excel(RAW / "cas_cpi" / "CPI_2007-2026.xlsx", header=None)
    hdr = d.iloc[12].fillna("").astype(str).str.upper().str.strip()
    cols = {}
    for i, h in hdr.items():
        mon = re.search(r"(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)", h)
        yr = re.search(r"(20\d\d)", h)
        if mon and yr and "WEIGHT" not in h:
            cols[i] = pd.Timestamp(int(yr.group(1)), MONTHS[mon.group(1)], 1)
    body = d.iloc[14:32].set_index(0)
    body = body[list(cols)].rename(columns=cols)
    long = body.reset_index().melt(id_vars=0, var_name="month", value_name="index_dec2013_100")
    long = long.rename(columns={0: "division"})
    long["division"] = long["division"].str.strip()

    # Jul/Aug 2026 from the latest release (division level). Apr-Jun 2026 are not published as data.
    snap = pd.read_excel(RAW / "cas_cpi" / "CPI_AUGUST2026.xlsx", sheet_name="CPI_monthly", header=None).iloc[9:27, :4]
    snap.columns = ["division", "chg", "2026-08-01", "2026-07-01"]
    snap = snap.melt(id_vars=["division"], value_vars=["2026-07-01", "2026-08-01"], var_name="month",
                     value_name="index_dec2013_100")
    snap["month"] = pd.to_datetime(snap["month"])
    snap["division"] = snap["division"].str.strip()
    long = pd.concat([long, snap], ignore_index=True)
    long["index_dec2013_100"] = pd.to_numeric(long["index_dec2013_100"], errors="coerce")
    long = long.dropna(subset=["index_dec2013_100"]).sort_values(["division", "month"])
    long.to_csv(OUT / "cpi_monthly.csv", index=False)


# ---------------------------------------------------------------- affordability
def build_affordability() -> None:
    f = pd.read_csv(RAW / "lbn_faostat_cost_affordability_healthy_diet.csv")
    keep = {
        "Prevalence of unaffordability (PUA)": "pct_unable_to_afford",
        "Number of people unable to afford a healthy diet (NUA)": "million_unable_to_afford",
    }
    t = f[f["Item"].isin(keep)].pivot_table(index="Year", columns="Item", values="Value").rename(columns=keep)
    cohd = f[(f["Item"] == "Cost of a healthy diet (CoHD)") & (f["Unit"].str.startswith("LCU"))].set_index("Year")["Value"]
    t["healthy_diet_lbp_per_day"] = cohd
    t.reset_index().rename(columns={"Year": "year"}).to_csv(OUT / "affordability_yearly.csv", index=False)


# ---------------------------------------------------------------- trade + UNIDO screen
GROUPS = {  # staple group -> (WFP items for shelf volatility, HS6 codes, FAOSTAT self-sufficiency item or None)
    "Wheat products": (["Wheat flour", "Bulgur (brown)", "Pasta (spaghetti)"], ["100119", "110100", "190430", "190219"], "Wheat"),
    "Lentils": (["Lentils", "Lentils (green)", "Lentils (red)"], ["071340"], "Lentils, dry"),
    "Chickpeas": (["Chickpeas"], ["071320"], "Chick peas, dry"),
    "Dry beans": (["Beans (white)"], ["071333"], "Beans, dry"),
    "Rice": (["Rice (imported, Egyptian)"], ["100630"], None),
    "Sugar": (["Sugar (white)"], ["170199"], None),
    "Sunflower oil": (["Oil (sunflower)"], ["151219", "151211"], None),
    "Milk powder": (["Milk (powder)"], ["040221", "040210"], None),
    "Tea": (["Tea"], ["090230"], None),
    "Tomato paste": (["Tomatoes (paste)"], ["200290"], None),
    "Potatoes": (["Potatoes"], ["070190"], "Potatoes"),
    "Cabbage": (["Cabbage"], ["070490"], "Cabbages"),
}
NO_DOMESTIC = {"Rice", "Sugar", "Milk powder", "Tea"}  # treated as 100% import-dependent; flagged as assumption


def build_trade_and_screen(nat: pd.DataFrame) -> None:
    c = pd.read_csv(RAW / "un_comtrade" / "comtrade_lbn_food_hs6_2015_2025_raw.csv", dtype={"cmdCode": str})
    trade = c[["refYear", "flowCode", "cmdCode", "hs_label", "wfp_item", "primaryValue", "netWgt"]].rename(columns={
        "refYear": "year", "flowCode": "flow", "cmdCode": "hs6", "primaryValue": "value_usd", "netWgt": "net_kg"})
    trade["usd_per_kg"] = trade["value_usd"] / trade["net_kg"].replace(0, np.nan)
    trade.to_csv(OUT / "trade_yearly.csv", index=False)

    ss = pd.read_csv(RAW / "faostat" / "self_sufficiency_lbn_2015_2024.csv")
    ss.to_csv(OUT / "self_sufficiency_yearly.csv", index=False)

    partners_path = RAW / "un_comtrade" / "comtrade_lbn_imports_by_partner_2022_2024.csv"
    partners = pd.read_csv(partners_path, dtype={"cmdCode": str}) if partners_path.exists() else None

    # Sunflower oil self-sufficiency from crude-oil production vs net imports (kg).
    prod = pd.read_csv(RAW / "faostat" / "faostat_production_crops_livestock_lbn.csv", low_memory=False)
    sun = prod[(prod["Item"] == "Sunflower-seed oil, crude") & (prod["Element"] == "Production")]

    rows = []
    for g, (items, codes, ss_item) in GROUPS.items():
        imp = trade[(trade["flow"] == "M") & trade["hs6"].isin(codes)]
        exp = trade[(trade["flow"] == "X") & trade["hs6"].isin(codes)]
        bill_2024 = imp.loc[imp["year"] == 2024, "value_usd"].sum()
        bill_2019 = imp.loc[imp["year"] == 2019, "value_usd"].sum()

        if ss_item:
            s = ss[(ss["faostat_item"] == ss_item) & ss["year"].between(2022, 2024)]["self_sufficiency"]
            self_suff, ss_basis = s.mean(), "FAOSTAT production + Comtrade, 2022-24 mean"
        elif g == "Sunflower oil" and not sun.empty:
            vals = []
            for y in (2022, 2023):
                p_t = sun[f"Y{y}"].iloc[0]
                m_t = imp.loc[imp["year"] == y, "net_kg"].sum() / 1000
                x_t = exp.loc[exp["year"] == y, "net_kg"].sum() / 1000
                vals.append(p_t / (p_t + m_t - x_t))
            self_suff, ss_basis = float(np.mean(vals)), "FAOSTAT crude-oil production + Comtrade, 2022-23 mean"
        elif g in NO_DOMESTIC:
            self_suff, ss_basis = 0.0, "Assumed ~0: no domestic production recorded in FAOSTAT"
        else:
            self_suff, ss_basis = np.nan, "Not computable from public data"

        # Shelf-price volatility: std of month-on-month % change in USD, Jan 2023 onward (stable-lira period).
        sh = (nat[nat["commodity"].isin(items) & (nat["month"] >= "2023-01-01")]
              .groupby("month")["price_usd_std"].median().sort_index())
        vol = sh.pct_change().std() * 100 if len(sh) > 6 else np.nan

        hhi = top_partner = top_share = np.nan
        if partners is not None:
            pp = partners[partners["cmdCode"].isin(codes)].groupby("partnerDesc")["primaryValue"].sum()
            if pp.sum() > 0:
                shares = pp / pp.sum()
                hhi = float((shares ** 2).sum())
                top_partner, top_share = shares.idxmax(), float(shares.max())

        rows.append(dict(group=g, wfp_items="; ".join(items), hs6_codes="; ".join(codes),
                         self_sufficiency=self_suff, self_sufficiency_basis=ss_basis,
                         import_bill_2024_usd=bill_2024, import_bill_2019_usd=bill_2019,
                         shelf_volatility_pct=vol, supplier_hhi=hhi, top_supplier=top_partner,
                         top_supplier_share=top_share))
    pd.DataFrame(rows).to_csv(OUT / "unido_screen.csv", index=False)

    if partners is not None:
        partners.to_csv(OUT / "imports_by_partner.csv", index=False)


def main() -> None:
    fx = build_fx()
    nat = build_prices(fx)
    build_world(nat)
    build_cpi()
    build_affordability()
    build_trade_and_screen(nat)
    for f in sorted(OUT.glob("*.csv")):
        n = sum(1 for _ in open(f, encoding="utf-8")) - 1
        print(f"{f.name:40s} {n:>7,} rows")


if __name__ == "__main__":
    main()
