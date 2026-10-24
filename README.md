# Lebanon food prices dashboard

**Why are staples so expensive in Lebanon, and what can be done?**

An interactive dashboard built for the MSBA 325 *Data Visualization and Communication* course at the
American University of Beirut (Fall 2026-27). It combines public data from WFP, the Central
Administration of Statistics (CAS), FAO, the World Bank and UN Comtrade to support two kinds of action:

- **Short term, price monitoring:** flag items whose shelf prices don't follow costs, so
  consumer-protection teams know where to look first.
- **Long term, import substitution:** rank the staples Lebanon depends on importing, to help choose
  which value chains deserve a local-production feasibility study.

> **Status:** working prototype, shared with stakeholders for feedback.
> Live app: *link added after deployment on share.streamlit.io*

---

## What's in the app

| Page | For | What it shows |
|---|---|---|
| **Overview** | everyone | Food prices vs other costs since 2019, which foods rose most in US dollars, share of people who can't afford a healthy diet |
| **Price monitor** | consumer protection | Three flags: shelf vs world price · gaps between governorates · items still rising while the lira is stable |
| **Import dependence** | industrial-development planners | Share of each staple grown locally, import bills, an adjustable priority score, supplier countries |
| **About the data** | everyone | Sources, cleaning steps, limits, downloads of the cleaned tables |

**A flag is a reason to look closer, not proof of overcharging.** Transport, taxes, packaging or a poor
harvest can all explain a gap.

---

## Repository layout

```
├── streamlit_app.py        app entry point (navigation)
├── app_pages/              one file per page
├── lib/                    shared code: data loaders, chart builders, flag/score logic
├── pipeline/build_data.py  turns raw data into the cleaned tables
├── raw data/               original source files, unmodified (see raw data/README.md)
├── data/                   cleaned tables the app reads (also usable in Tableau)
├── requirements.txt
└── .streamlit/config.toml  theme
```

## Run it locally

```bash
pip install -r requirements.txt
python pipeline/build_data.py      # rebuilds data/ from raw data/ (optional - data/ is committed)
streamlit run streamlit_app.py
```

## How the raw data is cleaned

`pipeline/build_data.py` makes these changes. Each one is explained in the app's *About the data* page.

1. **US-dollar prices are recomputed.** WFP's own `usdprice` column uses the official exchange rate
   (about 1,505 LBP until 2022) while the market rate passed 29,000. Every price is converted at the
   monthly parallel-market rate instead.
2. **Regions are harmonised.** WFP moved from 27 district markets to 8 governorates in 2025. All years
   are expressed as governorate medians so the series line up.
3. **Pack sizes are normalised** to per kg, per litre, per egg or per head.
4. **Each food is classed as mostly imported, locally processed / mixed, or mostly local**, using
   production (FAOSTAT) and trade (UN Comtrade) data. This is per food type, not per product on the shelf.
5. **Bread is excluded from price flags** because its price is set by the government.
6. **World benchmarks** (World Bank) are matched to shelf items and converted to US$ per kg.
7. **CPI** is reshaped from CAS's wide bilingual layout into one row per category per month.
8. **Self-sufficiency** = production ÷ (production + imports − exports).

## Limits

- Prices are monthly governorate averages; individual shops are not covered.
- World benchmarks are close but not identical products (e.g. Thai rice vs Egyptian rice on the shelf).
- Public data on local production costs stops in 2019, so the import-dependence page ranks priorities
  rather than comparing production costs.
- UN Comtrade has no 2025 data yet; CAS has not published CPI for April-June 2026.

## Deploy

1. Sign in at <https://share.streamlit.io> with GitHub.
2. **Create app** → repository `mariam-929/lebanon-food-prices`, branch `main`, file `streamlit_app.py`.
3. Every push to `main` updates the live app.

## Sources and licences

All data is public. Full details, links and coverage are in [`raw data/README.md`](raw%20data/README.md).

- WFP food prices for Lebanon, via the Humanitarian Data Exchange (CC BY-IGO)
- Central Administration of Statistics, Lebanon: consumer price index
- FAO / FAOSTAT: production, producer prices, cost and affordability of a healthy diet (CC BY 4.0)
- World Bank: Commodity Price Data (Pink Sheet) and Real-Time Prices (CC BY 4.0)
- UN Comtrade: Lebanon's food imports and exports

If you reuse this work, please credit the original sources above.
