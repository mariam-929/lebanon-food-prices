# Lebanon food prices dashboard

**Why are staples so expensive in Lebanon, and what can be done?**

An interactive dashboard that turns public price, trade and production data into **concrete flags and
priorities** for the people who can act on food prices in Lebanon. Built for the MSBA 325
*Data Visualization and Communication* course at the American University of Beirut (Fall 2026-27).

> **Status:** working prototype, being shown to stakeholders for feedback.
> **Live app:** *link added after deployment on share.streamlit.io*

---

## 1. Purpose

Since the 2019 financial crisis, food has become the fastest-rising cost of living in Lebanon:

- Food prices are **about 300 times** their December 2019 level, against about 76 times for all
  consumer prices (CAS consumer price index, to Aug 2026).
- **46% of people can't afford a healthy diet** (2025), up from 0.1% in 2019 (FAO).
- Lebanon grows only a small share of its cheapest staples: about **14% of its lentils, 22% of its
  wheat and 23% of its chickpeas** (FAOSTAT + UN Comtrade, 2022-24).

Everyone in Lebanon knows food got expensive; that alone is not news. This app goes one step further
and asks two questions that someone can **act on**:

1. **Short term — are shelf prices following costs?** Where do Lebanese shelf prices rise faster than
   world prices, differ sharply between governorates, or keep climbing even though the lira has been
   stable since 2023? Those are the places worth investigating first.
2. **Long term — which imports should Lebanon replace?** Which staples is Lebanon most exposed to
   importing, by dependence, cost, price swings and reliance on a few supplier countries? Those are the
   value chains worth a local-production feasibility study.

One story, two actions: **monitor prices now, reduce import exposure over time.**

---

## 2. Who it's for

| Audience | Page they use | Decisions it supports | What it can't tell them |
|---|---|---|---|
| **Consumer-protection authorities** (primary audience for the price monitor) | Price monitor | Which items and governorates to inspect first; which items to watch month to month; what to tell consumers | Which shop is overcharging (no shop-level data), or *why* a gap exists |
| **Industrial-development and agro-food planners**, e.g. agencies supporting local production (primary audience for import dependence) | Import dependence | Which staples to shortlist for value-chain or feasibility studies; how exposed each staple is to a single supplier country | Whether producing locally would be cheaper (public production-cost data stops in 2019) |
| **The public, students and media** (secondary audience, reached through the course blog post and social media) | Overview | Understanding how food prices changed relative to other costs and the currency | Personal shopping advice (prices are governorate averages) |

Stakeholders were chosen because members of the team have professional contacts in these kinds of
organisations, so the dashboard can be shown to real users and their feedback recorded. No organisation
has endorsed this work, and contacts are not named here without their permission.

---

## 3. What the app is for — and what it is not

**It is for:**
- Spotting **where to look**: a monitoring tool that ranks items and regions by how unusual their price
  movement is.
- Comparing **Lebanese shelf prices with world prices, regions and the exchange rate** in one place,
  which no single public source does.
- **Screening** staples for import substitution, with weights the user can adjust.

**It is not:**
- **Proof of overcharging.** A flag is a reason to look closer. Transport, taxes, packaging, a poor
  harvest or product differences can all explain a gap.
- **A feasibility study.** The import-dependence ranking says which staples deserve one, not which
  would succeed.
- **Political commentary.** It describes prices and trade; it does not assign blame to governments,
  importers or retailers.

---

## 4. Key findings so far (data to Aug 2026)

- **Food outpaced everything else:** ×304 since Dec 2019 vs ×76 for all prices; rent rose far less.
- **The currency doesn't explain it all:** even measured in US dollars, many foods cost several times
  more than in 2021, especially locally grown and formerly subsidised items.
- **Rice is flagged:** from Mar 2024 to Aug 2026 the world rice price fell 23% while the Lebanese shelf
  price rose 16%. Sugar is flagged in some windows (Mar 2024 → Mar 2026: world −31%, shelf −7%);
  sunflower oil is *not* flagged — its shelf price followed the world price.
- **Regional gaps:** in 2024 the same item cost up to 1.7 times as much in one governorate as in another
  (cabbage ×1.7, salt ×1.7, carrots ×1.6).
- **Import exposure:** wheat products (US$184M of imports in 2024), sunflower oil (US$140M) and sugar
  (US$129M) are the largest bills. 55% of wheat imports come from Ukraine, 58% of lentils from Canada and
  65% of tea from Sri Lanka.

All figures are reproducible from `raw data/` with `pipeline/build_data.py`.

---

## 5. The pages, and how each check works

### Overview
- **Headline figures:** food CPI multiple since Dec 2019, the parallel exchange rate, the share who
  can't afford a healthy diet, and local self-sufficiency in lentils, chickpeas and wheat.
- **Food vs other costs:** CPI categories rebased to Dec 2019 = 1 (log scale, so ×10 and ×100 are evenly spaced).
- **Price change in US dollars by item:** coloured by whether the food is mostly imported, locally
  processed / mixed, or mostly local.
- **Affordability:** FAO's share of people unable to afford a healthy diet, 2017-2025.

### Price monitor (consumer protection)
| Check | How it is calculated | Flag rule (adjustable) |
|---|---|---|
| **Shelf vs world price** | % change in the Lebanese shelf price vs the matching World Bank world price, both in US$ per kg, between two chosen months | Shelf change exceeds world change by ≥ 20 points |
| **Gaps between governorates** | Average US$ price in each of the 8 governorates over the latest 1, 3 or 12 months; most expensive ÷ cheapest | Shown as a ranked ratio |
| **Rising with a stable lira** | Average US$ price over the last 12 months vs the 12 months before. Yearly averages remove seasonal swings (cabbage is ~45% cheaper in summer) | Rise above 15% |

Bread is excluded from all flags because its price is set by the government.

### Import dependence (industrial development)
- **Self-sufficiency:** production ÷ (production + imports − exports), 2022-24 average. Rice, sugar,
  milk powder and tea are assumed ~0% (no domestic production recorded) and shown in grey.
- **Import bills:** 2019 vs 2024, in US$ million.
- **Priority screen:** four factors, each scaled 0-1 across staples, combined with user-set weights:
  import dependence · import bill · shelf-price volatility (since Jan 2023) · supplier concentration
  (Herfindahl index of import origins, 2022-24). Staples missing a factor are scored on the rest.
- **Supplier countries:** share of import value by country, 2022-24.

### About the data
Sources, cleaning steps, limits, and downloads of the cleaned tables.

---

## 6. How each dataset is used

| Dataset (in `raw data/`) | Used for | Page |
|---|---|---|
| WFP food prices for Lebanon | Monthly shelf prices by governorate — the core of every price chart and flag | Overview, Price monitor, Import dependence (volatility) |
| WFP markets | Governorate of each market | Price monitor |
| World Bank real-time prices (currency) | Parallel exchange rate before May 2020, to convert LBP to US$ | All price charts |
| CAS consumer price index | Food vs other cost categories since 2007 | Overview |
| FAO cost & affordability of a healthy diet | Share of people unable to afford a healthy diet | Overview |
| World Bank Pink Sheet | World prices for rice, sugar, sunflower oil, tea, wheat | Price monitor (shelf vs world) |
| UN Comtrade (all partners) | Import and export volumes and values by food | Import dependence (bills, self-sufficiency) |
| UN Comtrade (by partner) | Supplier countries and concentration | Import dependence |
| FAOSTAT production | Domestic production volumes | Import dependence (self-sufficiency) |
| FAOSTAT producer prices | Kept for reference only — real values stop in 2019 | – |
| WFP global extract (Lebanon + neighbours) | Kept for comparing Lebanon with Jordan, Syria, Egypt, Iraq, Türkiye, Palestine | Planned |
| World Bank real-time prices (energy) | Kept for fuel analysis | Planned |

Full file-by-file documentation, links and licences: [`raw data/README.md`](raw%20data/README.md).

---

## 7. How the raw data is cleaned

`pipeline/build_data.py` makes these changes:

1. **US-dollar prices are recomputed.** WFP's own `usdprice` column uses the official exchange rate
   (about 1,505 LBP until 2022) while the market rate passed 29,000. Every price is converted at the
   monthly parallel-market rate (WFP's observed rate from May 2020, World Bank estimates before).
2. **Regions are harmonised.** WFP moved from 27 district markets to 8 governorates in 2025. All years
   are expressed as governorate medians so the series line up.
3. **Pack sizes are normalised** to per kg, per litre, per egg or per head.
4. **Each food is classed** as mostly imported, locally processed / mixed, or mostly local, using
   production (FAOSTAT) and trade (UN Comtrade) data — per food type, not per product on the shelf.
5. **Bread is excluded from price flags** (government-set price).
6. **World benchmarks** are matched to shelf items and converted to US$ per kg (sunflower oil at 0.92 kg/L).
7. **CPI** is reshaped from CAS's wide bilingual layout into one row per category per month.
8. **Self-sufficiency** = production ÷ (production + imports − exports).

---

## 8. Design choices

- **Diagnostic wording:** "flag", "investigate", "worth a closer look" — never "overcharging".
- **Economic, not political framing**, in line with the course rule against sensitive topics.
- **Mobile-friendly:** single-column layout on phones, horizontal bar charts so labels stay readable,
  wrapping legends.
- **One axis per chart:** series on different scales are indexed to a common base instead of dual axes.
- **Colour follows the entity:** "mostly imported" is always blue, "mostly local" always green, across
  every chart; colours come from a colour-blind-validated palette.
- **Gaps are shown, not hidden:** missing CPI months appear as breaks; assumed values are greyed and labelled.
- **Adjustable thresholds and weights,** so users can test whether a finding depends on one setting.

---

## 9. Limits

- Prices are monthly governorate averages; individual shops are not covered.
- World benchmarks are close but not identical products (e.g. Thai rice vs Egyptian rice on the shelf).
- Public data on local production costs stops in 2019, so import dependence ranks priorities rather
  than comparing costs.
- Many recent FAOSTAT production values are FAO estimates.
- UN Comtrade has no 2025 data yet; CAS has not published CPI for April-June 2026.

---

## 10. Project context and next steps

This is a course project. Its main deliverable is **impact**: showing the dashboard to the people who
could use it and recording their feedback. The plan:

1. Share the live app with consumer-protection and industrial-development contacts and ask:
   *Which of these would you use? Would these flags change where you inspect? Are these the right
   factors for choosing value chains? What's missing?*
2. Publish a blog post with the embedded app on the AUB data-visualization site and share it on social media.
3. Iterate on the feedback.

Possible additions: nutrition per dollar (USDA FoodData Central), minimum-wage affordability, the
Lebanon-vs-neighbours comparison, fuel prices, a Tableau Public version of the price monitor, and any
data stakeholders are willing to share.

---

## Repository layout

```
├── streamlit_app.py        app entry point (navigation)
├── app_pages/              one file per page
├── lib/                    shared code: data loaders, chart builders, flag/score logic
├── pipeline/build_data.py  turns raw data into the cleaned tables
├── raw data/               original source files (see raw data/README.md)
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

## Deploy

1. Sign in at <https://share.streamlit.io> with GitHub.
2. **Create app** → repository `mariam-929/lebanon-food-prices`, branch `main`, file `streamlit_app.py`.
3. Every push to `main` updates the live app.

## Sources and licences

All data is public. Details, links and coverage: [`raw data/README.md`](raw%20data/README.md).

- WFP food prices for Lebanon, via the Humanitarian Data Exchange (CC BY-IGO)
- Central Administration of Statistics, Lebanon: consumer price index
- FAO / FAOSTAT: production, producer prices, cost and affordability of a healthy diet (CC BY 4.0)
- World Bank: Commodity Price Data (Pink Sheet) and Real-Time Prices (CC BY 4.0)
- UN Comtrade: Lebanon's food imports and exports

If you reuse this work, please credit the original sources above.
