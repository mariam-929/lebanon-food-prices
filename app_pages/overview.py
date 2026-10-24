import pandas as pd
import streamlit as st

from lib import charts, data

st.title("Why are staples so expensive in Lebanon?", anchor=False)
st.markdown(
    "Since the 2019 crisis, food has become the fastest-rising cost in Lebanon. This dashboard tracks "
    "**where shelf prices drift away from costs** (for price monitoring) and **which staples Lebanon "
    "depends on importing** (for local-production planning)."
)

cpi = data.cpi()
piv = cpi.pivot_table(index="month", columns="division", values="index_dec2013_100")
base, last = pd.Timestamp("2019-12-01"), piv.index.max()
food_x = piv.loc[last, "Food and non-alcoholic beverages"] / piv.loc[base, "Food and non-alcoholic beverages"]
all_x = piv.loc[last, "Consumer price index"] / piv.loc[base, "Consumer price index"]
fx = data.fx().set_index("month")["lbp_per_usd"]
fx_x = fx.iloc[-1] / fx.loc[base]
aff = data.affordability().set_index("year")
ss = data.unido_screen().set_index("group")["self_sufficiency"]

with st.container(horizontal=True):
    st.metric("Food prices since Dec 2019", f"×{food_x:,.0f}", f"vs ×{all_x:,.0f} for all prices",
              delta_color="off", delta_arrow="off", border=True,
              help=f"CAS consumer price index, Dec 2019 to {last:%b %Y}")
    st.metric("Lira per US dollar", f"{fx.iloc[-1]:,.0f}", f"×{fx_x:,.0f} since Dec 2019", delta_color="off",
              delta_arrow="off", border=True, help="Parallel-market rate (WFP / World Bank)")
    st.metric("Can't afford a healthy diet", f"{aff.loc[aff.index.max(), 'pct_unable_to_afford']:.0f}%",
              f"was {aff.loc[2019, 'pct_unable_to_afford']:.1f}% in 2019", delta_color="off", delta_arrow="off",
              border=True, help=f"FAO, {aff.index.max()} · {aff.loc[aff.index.max(), 'million_unable_to_afford']:.1f} million people")
    st.metric("Lentils grown in Lebanon", f"{ss['Lentils']:.0%}",
              f"chickpeas {ss['Chickpeas']:.0%} · wheat {ss['Wheat products']:.0%}", delta_color="off",
              delta_arrow="off", border=True, help="Share of consumption produced locally, 2022-24 (FAOSTAT + UN Comtrade)")

with st.container(border=True):
    st.subheader("Food rose four times faster than everything else", anchor=False)
    st.caption("Consumer price index, multiple of its December 2019 level (log scale). Gaps are months CAS did not publish (Apr-May 2020 for some categories, Apr-Jun 2026).")
    others = [d for d in piv.columns if d not in ("Food and non-alcoholic beverages", "Consumer price index")]
    extra = st.pills("Compare with", ["Transportation", "Health", "Actual rent", "Water,electricity,gas and other fuels",
                                      "Education", "Communication"], selection_mode="multi",
                     default=["Transportation", "Actual rent"], key="cpi_extra")
    shown = ["Food and non-alcoholic beverages", "Consumer price index"] + list(extra)
    colors = {d: charts.SLOTS[i] for i, d in enumerate(
        ["Food and non-alcoholic beverages", "Consumer price index", "Transportation", "Health", "Actual rent",
         "Water,electricity,gas and other fuels", "Education", "Communication"])}
    rebased = (piv.loc[piv.index >= "2019-12-01", shown] / piv.loc[base, shown]).reset_index().melt(
        id_vars="month", var_name="division", value_name="multiple")
    rebased["division"] = rebased["division"].replace({"Consumer price index": "All prices (CPI)",
                                                       "Food and non-alcoholic beverages": "Food"})
    colors = {{"Consumer price index": "All prices (CPI)", "Food and non-alcoholic beverages": "Food"}.get(k, k): v
              for k, v in colors.items() if k in shown}
    st.altair_chart(charts.lines(rebased, "month", "multiple", "division", colors, "× Dec 2019 level", log=True,
                                 y_format=",.0f"))

with st.container(border=True):
    st.subheader("Even in dollars, some foods got far more expensive", anchor=False)
    st.caption("Change in shelf price in US dollars (parallel-market rate). Locally grown and formerly subsidised "
               "items rose most, so the currency collapse alone doesn't explain it.")
    nat = data.national()
    months = sorted(nat["month"].unique())
    c1, c2 = st.columns(2)
    start = c1.selectbox("From", months, index=months.index(pd.Timestamp("2021-03-01")),
                         format_func=lambda m: f"{pd.Timestamp(m):%b %Y}", key="ov_from")
    end = c2.selectbox("To", months, index=len(months) - 1, format_func=lambda m: f"{pd.Timestamp(m):%b %Y}",
                       key="ov_to")
    a = nat[nat["month"] == start].set_index("commodity")
    b = nat[nat["month"] == end].set_index("commodity")
    chg = (b["price_usd_std"] / a["price_usd_std"]).dropna().rename("multiple").reset_index()
    chg = chg.merge(b[["origin_class"]].reset_index(), on="commodity")
    if chg.empty:
        st.info("No items were priced in both months. Pick a different range.")
    else:
        st.altair_chart(charts.hbars(chg, "multiple", "commodity", "× price in US dollars", color_field="origin_class",
                                     color_scale=charts.ORIGIN_SCALE, value_format=".1f"))

with st.container(border=True):
    st.subheader("Almost half the population can't afford a healthy diet", anchor=False)
    st.caption("Share of people unable to afford a healthy diet (FAO, State of Food Security report 2026)")
    st.altair_chart(charts.vbars(data.affordability(), "year", "pct_unable_to_afford", "% of population",
                                 y_format=".0f"))
