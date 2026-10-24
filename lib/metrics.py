"""Flag and score computations, kept free of Streamlit so they can be tested and reused."""
import numpy as np
import pandas as pd


def world_flags(wvs: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp, threshold_pp: float) -> pd.DataFrame:
    """% change of world vs shelf USD/kg between two months. Flag when the shelf moved
    `threshold_pp` points more (up) than the world benchmark."""
    rows = []
    for item, g in wvs.groupby("commodity"):
        g = g.set_index("month")
        if start not in g.index or end not in g.index:
            continue
        w0, w1 = g.loc[start, "world_usd_per_kg"], g.loc[end, "world_usd_per_kg"]
        s0, s1 = g.loc[start, "shelf_usd_per_kg"], g.loc[end, "shelf_usd_per_kg"]
        if pd.isna([w0, w1, s0, s1]).any():
            continue
        wc, sc = (w1 / w0 - 1) * 100, (s1 / s0 - 1) * 100
        rows.append(dict(item=item, benchmark=g["benchmark"].iloc[0], world_change=wc, shelf_change=sc,
                         gap_pp=sc - wc, shelf_end=s1, world_end=w1, flagged=(sc - wc) >= threshold_pp,
                         note=g["note"].iloc[0] if isinstance(g["note"].iloc[0], str) else ""))
    return pd.DataFrame(rows)


def regional_gaps(gov: pd.DataFrame, months: list[pd.Timestamp]) -> pd.DataFrame:
    """Most vs least expensive governorate per item, using the average over `months`."""
    sub = gov[gov["month"].isin(months) & ~gov["regulated_price"]]
    avg = sub.groupby(["commodity", "origin_class", "std_unit", "admin1"])["price_usd_std"].mean().reset_index()
    rows = []
    for (item, origin, unit), g in avg.groupby(["commodity", "origin_class", "std_unit"]):
        if g["admin1"].nunique() < 4:
            continue
        hi, lo = g.loc[g["price_usd_std"].idxmax()], g.loc[g["price_usd_std"].idxmin()]
        rows.append(dict(item=item, origin_class=origin, std_unit=unit, ratio=hi.price_usd_std / lo.price_usd_std,
                         most_expensive=hi.admin1, max_price=hi.price_usd_std,
                         cheapest=lo.admin1, min_price=lo.price_usd_std, n_governorates=g["admin1"].nunique()))
    return pd.DataFrame(rows).sort_values("ratio", ascending=False)


def rolling_change(nat: pd.DataFrame, end: pd.Timestamp) -> pd.DataFrame:
    """Average USD price over the 12 months to `end` vs the 12 months before. Comparing 12-month
    averages removes seasonal swings (e.g. cabbage is ~45% cheaper in summer)."""
    cur = pd.date_range(end - pd.DateOffset(months=11), end, freq="MS")
    prev = pd.date_range(end - pd.DateOffset(months=23), end - pd.DateOffset(months=12), freq="MS")
    d = nat[~nat["regulated_price"]]
    a = d[d["month"].isin(cur)].groupby("commodity")["price_usd_std"].agg(["mean", "count"])
    b = d[d["month"].isin(prev)].groupby("commodity")["price_usd_std"].agg(["mean", "count"])
    t = a.join(b, lsuffix="_cur", rsuffix="_prev").dropna()
    t = t[(t["count_cur"] >= 9) & (t["count_prev"] >= 9)]  # need most months in both windows
    t["change_pct"] = (t["mean_cur"] / t["mean_prev"] - 1) * 100
    meta = d.drop_duplicates("commodity").set_index("commodity")[["origin_class", "std_unit"]]
    return t.join(meta).reset_index().rename(columns={"commodity": "item"}).sort_values("change_pct", ascending=False)


FACTORS = {
    "import_dependence": "Import dependence",
    "import_bill": "Import bill (2024)",
    "volatility": "Shelf-price volatility",
    "concentration": "Supplier concentration",
}


def priority_scores(screen: pd.DataFrame, weights: dict[str, float]) -> pd.DataFrame:
    """Weighted 0-100 screening score. Each factor min-max scaled across groups; missing factors are
    left out of that group's weighted average (and reported)."""
    s = screen.copy()
    raw = pd.DataFrame({
        "import_dependence": 1 - s["self_sufficiency"].clip(0, 1),
        "import_bill": np.log10(s["import_bill_2024_usd"].clip(lower=1)),
        "volatility": s["shelf_volatility_pct"],
        "concentration": s["supplier_hhi"],
    })
    scaled = (raw - raw.min()) / (raw.max() - raw.min()).replace(0, np.nan)
    w = pd.Series(weights, dtype=float)
    present = scaled.notna()
    weighted = (scaled.fillna(0) * w).sum(axis=1)
    denom = (present * w).sum(axis=1).replace(0, np.nan)
    s["score"] = weighted / denom * 100
    s["missing_factors"] = present.apply(lambda r: ", ".join(FACTORS[k] for k, ok in r.items() if not ok and w[k] > 0), axis=1)
    for k in FACTORS:
        s[f"scaled_{k}"] = scaled[k]
    return s.sort_values("score", ascending=False)
