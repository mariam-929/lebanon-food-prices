import altair as alt
import pandas as pd
import streamlit as st

from lib import charts, data, metrics

st.title("Import dependence", anchor=False)
st.markdown(
    "Lebanon's cheapest sources of nutrition, such as pulses and wheat, are also the foods it imports most. "
    "This page ranks staples by how exposed Lebanon is to importing them, to help choose **which value chains "
    "deserve a local-production feasibility study**."
)
st.caption("Built for industrial-development planners. It screens priorities; it does not show that local "
           "production would be cheaper (public production-cost data stops in 2019).")

screen = data.unido_screen()

with st.container(border=True):
    st.subheader("How much of each staple Lebanon grows itself", anchor=False)
    st.caption("Production ÷ (production + imports − exports), 2022-24 average. Grey bars are assumed ~0% "
               "because FAOSTAT records no domestic production.")
    ss = screen.dropna(subset=["self_sufficiency"]).copy()
    ss["basis"] = ss["self_sufficiency_basis"].str.startswith("Assumed").map({True: "Assumed", False: "Measured"})
    ss_order = ss.sort_values("self_sufficiency")["group"].tolist()
    chart = alt.Chart(ss).mark_bar(cornerRadiusEnd=4, height={"band": 0.7}).encode(
        x=alt.X("self_sufficiency:Q", title="Share produced in Lebanon", axis=alt.Axis(format=".0%"),
                scale=alt.Scale(domain=[0, 1])),
        y=alt.Y("group:N", sort=ss_order, title=None, axis=alt.Axis(labelOverlap=False)),
        color=alt.Color("basis:N", scale=alt.Scale(domain=["Measured", "Assumed"], range=[charts.SLOTS[0], charts.MUTED]),
                        legend=alt.Legend(orient="top", title=None)),
        tooltip=[alt.Tooltip("group:N", title="Staple"), alt.Tooltip("self_sufficiency:Q", format=".0%"),
                 alt.Tooltip("self_sufficiency_basis:N", title="Basis")],
    )
    ss["label"] = ss.apply(lambda r: f"{r.self_sufficiency:.0%}" + (" (assumed)" if r.basis == "Assumed" else ""), axis=1)
    text = alt.Chart(ss).mark_text(align="left", dx=4, color=charts.MUTED).encode(
        x="self_sufficiency:Q", y=alt.Y("group:N", sort=ss_order), text="label:N")
    st.altair_chart(charts._base(alt.layer(chart, text), 30 * len(ss)))

with st.container(border=True):
    st.subheader("What Lebanon spends importing them", anchor=False)
    st.caption("Import value in US$ million, UN Comtrade (Lebanon's own customs reports).")
    bills = screen.melt(id_vars="group", value_vars=["import_bill_2019_usd", "import_bill_2024_usd"],
                        var_name="year", value_name="usd")
    bills["year"] = bills["year"].map({"import_bill_2019_usd": "2019", "import_bill_2024_usd": "2024"})
    bills["usd_m"] = bills["usd"] / 1e6
    order = screen.sort_values("import_bill_2024_usd", ascending=False)["group"].tolist()
    dots = alt.Chart(bills).encode(y=alt.Y("group:N", sort=order, title=None, axis=alt.Axis(labelOverlap=False)))
    rule = dots.mark_rule(color=charts.MUTED, strokeWidth=2).encode(x="min(usd_m):Q", x2="max(usd_m):Q")
    pts = dots.mark_circle(size=110, opacity=1).encode(
        x=alt.X("usd_m:Q", title="US$ million"),
        color=alt.Color("year:N", scale=alt.Scale(domain=["2019", "2024"], range=[charts.SLOTS[1], charts.SLOTS[0]]),
                        legend=alt.Legend(orient="top", title=None)),
        tooltip=["group:N", "year:N", alt.Tooltip("usd_m:Q", format=",.1f", title="US$ million")],
    )
    st.altair_chart(charts._base(alt.layer(rule, pts), 30 * len(order)))

with st.container(border=True):
    st.subheader("Priority screen", anchor=False)
    st.caption("Adjust how much each factor matters. Each factor is scaled 0–1 across staples; the score is the "
               "weighted average. Staples missing a factor are scored on the factors they have.")
    with st.container(horizontal=True):
        w = {
            "import_dependence": st.slider("Import dependence", 0, 5, 3, key="w_dep",
                                           help="1 − share produced locally"),
            "import_bill": st.slider("Import bill", 0, 5, 2, key="w_bill", help="2024 import value (log scale)"),
            "volatility": st.slider("Price volatility", 0, 5, 1, key="w_vol",
                                    help="Month-to-month swings in the US$ shelf price since Jan 2023"),
            "concentration": st.slider("Supplier concentration", 0, 5, 2, key="w_hhi",
                                       help="Herfindahl index of import origins, 2022-24: high = few suppliers"),
        }
    if sum(w.values()) == 0:
        st.info("Set at least one weight above zero.")
    else:
        scored = metrics.priority_scores(screen, w)
        scored["grown_pct"] = scored["self_sufficiency"] * 100
        scored["imports_m"] = scored["import_bill_2024_usd"] / 1e6
        scored["top_share_pct"] = scored["top_supplier_share"] * 100
        st.dataframe(
            scored[["group", "score", "grown_pct", "imports_m", "top_supplier", "top_share_pct", "missing_factors"]],
            hide_index=True,
            column_config={
                "group": "Staple",
                "score": st.column_config.ProgressColumn("Priority score", format="%.0f", min_value=0, max_value=100),
                "grown_pct": st.column_config.NumberColumn("Grown locally", format="%.0f%%"),
                "imports_m": st.column_config.NumberColumn("Imports 2024", format="$%.0fM"),
                "top_supplier": "Main supplier",
                "top_share_pct": st.column_config.NumberColumn("Main supplier share", format="%.0f%%"),
                "missing_factors": "Not scored on",
            },
        )
        top = scored.head(3)["group"].tolist()
        st.markdown(f"With these weights, the top candidates for a feasibility study are **{', '.join(top)}**.")

partners = data.partners()
if partners is not None:
    with st.container(border=True):
        st.subheader("Where imports come from", anchor=False)
        groups = screen.dropna(subset=["top_supplier"])["group"].tolist()
        g = st.selectbox("Staple", groups, key="p_group")
        codes = screen.set_index("group").loc[g, "hs6_codes"].split("; ")
        p = partners[partners["cmdCode"].astype(str).str.zfill(6).isin(codes)]
        share = (p.groupby("partnerDesc")["primaryValue"].sum() / p["primaryValue"].sum()).sort_values(ascending=False)
        top = share.head(6)
        if len(share) > 6:
            top["Other"] = share.iloc[6:].sum()
        df = top.rename("share").reset_index().rename(columns={"partnerDesc": "country", "index": "country"})
        st.caption("Share of import value, 2022-24 combined (UN Comtrade).")
        st.altair_chart(charts.hbars(df, "share", "country", "Share of imports", value_format=".0%", sort="-x"))
