import pandas as pd
import streamlit as st

from lib import charts, data, metrics

st.title("Price monitor", anchor=False)
st.markdown(
    "Three checks that point to **where shelf prices may not be following costs**. A flag is a reason to "
    "look closer, not proof of overcharging: transport, taxes, packaging or a poor harvest can all explain a gap."
)
st.caption("Built for consumer-protection teams deciding where to inspect first.")

tab_world, tab_region, tab_trend = st.tabs([":material/public: Shelf vs world price",
                                            ":material/map: Gaps between governorates",
                                            ":material/trending_up: Rising with a stable lira"])

# ------------------------------------------------------------------ 1. world vs shelf
with tab_world:
    wvs = data.world_vs_shelf()
    common = wvs.dropna(subset=["world_usd_per_kg", "shelf_usd_per_kg"])
    months = sorted(common["month"].unique())
    fmt = lambda m: f"{pd.Timestamp(m):%b %Y}"
    c1, c2, c3 = st.columns(3)
    start = c1.selectbox("From", months, index=months.index(pd.Timestamp("2024-03-01")), format_func=fmt, key="w_from")
    end = c2.selectbox("To", months, index=len(months) - 1, format_func=fmt, key="w_to")
    thr = c3.number_input("Flag if shelf beats world by (points)", 5, 100, 20, step=5, key="w_thr")
    flags = metrics.world_flags(wvs, pd.Timestamp(start), pd.Timestamp(end), thr)

    if flags.empty:
        st.info("No item has both a world and a shelf price in both months. Try a different range.")
    else:
        flags = flags.sort_values("gap_pp", ascending=False)
        flags["status"] = flags["flagged"].map({True: "Investigate", False: "Tracks world price"})
        st.dataframe(
            flags[["item", "status", "gap_pp", "world_change", "shelf_change", "benchmark"]],
            hide_index=True,
            column_config={
                "status": st.column_config.TextColumn("Status"),
                "item": "Item",
                "world_change": st.column_config.NumberColumn("World price", format="%+.0f%%"),
                "shelf_change": st.column_config.NumberColumn("Lebanese shelf", format="%+.0f%%"),
                "gap_pp": st.column_config.NumberColumn("Gap (points)", format="%+.0f",
                                                        help="Shelf change minus world change"),
                "benchmark": "World benchmark",
            },
        )
        n = int(flags["flagged"].sum())
        if n:
            st.warning(f"{n} item(s) flagged: shelf prices moved at least {thr} points more than world prices.",
                       icon=":material/flag:")
        item = st.selectbox("Show item", flags["item"].tolist(), key="w_item")
        g = wvs[(wvs["commodity"] == item) & (wvs["month"] >= start) & (wvs["month"] <= end)].copy()
        g0 = g[g["month"] == start].iloc[0]
        g["Lebanese shelf"] = g["shelf_usd_per_kg"] / g0["shelf_usd_per_kg"] * 100
        g["World price"] = g["world_usd_per_kg"] / g0["world_usd_per_kg"] * 100
        long = g.melt(id_vars="month", value_vars=["Lebanese shelf", "World price"], var_name="series",
                      value_name="index").dropna()
        st.altair_chart(charts.lines(long, "month", "index", "series",
                                     {"Lebanese shelf": charts.SLOTS[0], "World price": charts.SLOTS[1]},
                                     f"Index ({fmt(start)} = 100)"))
        note = flags.set_index("item").loc[item, "note"]
        st.caption(f"Both series in US dollars per kg. {note}")

# ------------------------------------------------------------------ 2. regional gaps
with tab_region:
    gov = data.governorate()
    months = sorted(gov["month"].unique())
    period = st.segmented_control("Period", ["Latest month", "Last 3 months", "Last 12 months"],
                                  default="Last 3 months", key="r_period")
    k = {"Latest month": 1, "Last 3 months": 3, "Last 12 months": 12}[period or "Last 3 months"]
    sel = months[-k:]
    gaps = metrics.regional_gaps(gov, sel)
    st.caption(f"Average price per governorate, {fmt(sel[0])} – {fmt(sel[-1])}. Bread excluded (regulated price).")
    gaps["unit"] = gaps["std_unit"].map(data.unit_label)
    st.dataframe(
        gaps[["item", "ratio", "most_expensive", "max_price", "cheapest", "min_price", "unit"]],
        hide_index=True,
        column_config={
            "item": "Item",
            "ratio": st.column_config.ProgressColumn("Most ÷ cheapest", format="×%.2f", min_value=1,
                                                     max_value=float(max(2.0, gaps["ratio"].max()))),
            "most_expensive": "Most expensive",
            "max_price": st.column_config.NumberColumn("US$", format="%.2f"),
            "cheapest": "Cheapest",
            "min_price": st.column_config.NumberColumn("US$ ", format="%.2f"),
            "unit": "Unit",
        },
    )
    item = st.selectbox("Show item", gaps["item"].tolist(), key="r_item")
    g = gov[gov["month"].isin(sel) & (gov["commodity"] == item)]
    by_gov = g.groupby("admin1")["price_usd_std"].mean().reset_index()
    unit = data.unit_label(g["std_unit"].iloc[0])
    st.altair_chart(charts.hbars(by_gov, "price_usd_std", "admin1", f"US$ {unit}", value_format=".2f"))

# ------------------------------------------------------------------ 3. rising with a stable lira
with tab_trend:
    nat = data.national()
    st.markdown("The lira has held at about **89,500 per dollar since 2023**, so prices in dollars should be "
                "roughly flat. Items still climbing in dollars are worth a closer look.")
    end = nat["month"].max()
    thr = st.slider("Flag if the 12-month average rose by more than", 0, 50, 15, format="%d%%", key="t_thr")
    rc = metrics.rolling_change(nat, end)
    rc["flag"] = rc["change_pct"] > thr
    st.caption(f"Average US-dollar price over the 12 months to {end:%b %Y} vs the 12 months before. "
               "Comparing yearly averages removes seasonal swings.")
    st.altair_chart(charts.hbars(rc, "change_pct", "item", "% change in average US$ price",
                                 color_field="origin_class", color_scale=charts.ORIGIN_SCALE, value_format="+.0f"))
    flagged = rc[rc["flag"]]
    if len(flagged):
        st.warning("Flagged: " + ", ".join(f"{r.item} ({r.change_pct:+.0f}%)" for r in flagged.itertuples()),
                   icon=":material/flag:")
    else:
        st.success("No item rose above the threshold.", icon=":material/check_circle:")
