import streamlit as st

from lib import data

st.title("About the data", anchor=False)

st.subheader("Sources", anchor=False)
st.table({
    "Source": ["WFP food prices (HDX)", "CAS consumer price index", "World Bank Pink Sheet", "UN Comtrade",
               "FAOSTAT", "FAO cost & affordability of a healthy diet", "World Bank real-time prices"],
    "What it gives": ["Monthly retail prices, 8 governorates, Aug 2012 – Aug 2026",
                      "Official CPI by spending category, Dec 2007 – Aug 2026",
                      "Monthly world commodity prices to Sep 2026",
                      "Lebanon's food imports and exports by product and partner, 2015 – 2024",
                      "Domestic production volumes, 2015 – 2024",
                      "Share of people unable to afford a healthy diet, 2017 – 2025",
                      "Parallel-market exchange rate before May 2020"],
})

st.subheader("How the data was cleaned", anchor=False)
st.markdown(
    "- **US-dollar prices recomputed.** WFP's own dollar column uses the official rate (about 1,505 LBP until 2022) "
    "while the market rate reached 29,000+. Every price here is converted at the monthly parallel-market rate.\n"
    "- **Regions harmonised.** WFP switched from 27 district markets to 8 governorates in 2025. All years are "
    "shown as governorate medians so the series line up.\n"
    "- **Pack sizes normalised** to per kg, per litre, per egg or per head.\n"
    "- **Imported vs local** is assigned per food type from production and trade data, not per product on the shelf.\n"
    "- **Bread is excluded from price flags** because its price is set by the government."
)

st.subheader("Limits", anchor=False)
st.markdown(
    "- Flags show where prices diverge from costs; they cannot prove why. Taxes, transport, packaging and "
    "harvests all matter.\n"
    "- World benchmarks are close but not identical products (e.g. Thai rice vs Egyptian rice on the shelf).\n"
    "- No public data on local production costs after 2019, so the import-dependence page screens priorities "
    "rather than comparing costs.\n"
    "- Prices are monthly governorate averages; individual shops are not covered.\n"
    "- CPI for April – June 2026 has not been published as data."
)

st.subheader("Download the cleaned data", anchor=False)
with st.container(horizontal=True):
    for name, label in [("prices_governorate_monthly", "Prices by governorate"),
                        ("prices_national_monthly", "National prices"),
                        ("world_vs_shelf_monthly", "World vs shelf"),
                        ("cpi_monthly", "CPI"), ("unido_screen", "Import dependence")]:
        st.download_button(label, (data.DATA / f"{name}.csv").read_bytes(), file_name=f"{name}.csv",
                           mime="text/csv", icon=":material/download:")
