# Raw data

The original files behind the dashboard, as downloaded (exceptions are noted below).
`pipeline/build_data.py` reads only this folder and writes the cleaned tables to `../data/`.

**Don't edit these files.** If a file is opened in Excel and saved, Excel rewrites the dates; the
pipeline copes with that, but other tools may not.

## Files

### Food prices (core)

| File | Source | Coverage | Rows × cols | Notes |
|---|---|---|---|---|
| `wfp_food_prices_lbn.csv` | WFP via [Humanitarian Data Exchange](https://data.humdata.org/dataset/wfp-food-prices-for-lebanon) | Aug 2012 – Aug 2026, monthly | 40,702 × 16 | Retail prices for ~30 foods, 3 fuels and the parallel exchange rate. ⚠️ `usdprice` uses the official rate and is wrong for 2020-22; the pipeline recomputes it. 27 district markets until 2024, 8 governorates from 2025. Dates are `dd-mm-yy` because the file was once saved in Excel (values unchanged) |
| `wfp_markets_lbn.csv` | WFP via HDX | – | 27 × 7 | Market names, governorates and coordinates |
| `wfp_global_extract/wfp_food_prices_lbn_and_neighbours_2024_2026.csv` | WFP global price files via HDX | Jan 2024 – Oct 2026 | 146,678 × 17 | **Filtered extract**: only Lebanon, Jordan, Syria, Egypt, Iraq, Türkiye and Palestine, rows unchanged. The full global files (~155 MB) are too large for GitHub |

### Exchange rate and fuel

| File | Source | Coverage | Rows × cols | Notes |
|---|---|---|---|---|
| `real-time-currency-prices-for-lebanon.csv` | World Bank Real-Time Prices, via HDX | Jan 2012 – Aug 2026 | 4,928 × 75 | Parallel LBP/USD rate (use rows where `mkt_name` = "Market Average"). Only 18 columns contain data. Model-based estimates; used before WFP's observed rate starts in May 2020 |
| `real-time-energy-prices-for-lebanon.csv` | World Bank Real-Time Prices, via HDX | Jan 2012 – Aug 2026 | 4,928 × 55 | Diesel, gas and petrol estimates. Kept for fuel analysis; not used by the current app |

### Consumer prices and affordability

| File | Source | Coverage | Notes |
|---|---|---|---|
| `cas_cpi/CPI_2007-2026.xlsx` | [CAS Lebanon](https://www.cas.gov.lb/economic-statistics/cpi/) | Dec 2007 – Mar 2026, monthly | CPI by 18 spending categories (Dec 2013 = 100). Wide layout with English and Arabic headers. Some categories missing Apr-May 2020 |
| `cas_cpi/CPI_AUGUST2026.xlsx` | CAS Lebanon | Jul – Aug 2026 | Latest monthly release, incl. regional CPI and subclasses. Apr-Jun 2026 were only published as images |
| `cas_cpi/CPI-Metadata.pdf` | CAS Lebanon | – | CPI methodology |
| `lbn_faostat_cost_affordability_healthy_diet.csv` | [FAOSTAT](https://www.fao.org/faostat/) (SOFI 2026 release) | 2017 – 2025, yearly | Cost of a healthy diet and share of people who can't afford it. Dates are `dd-mm-yy` (saved in Excel once) |

### World prices

| File | Source | Coverage | Notes |
|---|---|---|---|
| `world_bank_commodity_prices/CMO-Historical-Data-Monthly.xlsx` | [World Bank Pink Sheet](https://www.worldbank.org/en/research/commodity-markets) | Jan 1960 – Sep 2026, monthly | World prices for rice, wheat, sugar, sunflower oil, tea, chicken and more (nominal US$) |

### Trade (UN Comtrade)

Downloaded from the [UN Comtrade](https://comtradeplus.un.org/) public API (`comtradeapi.un.org/public/v1/preview`),
reporter Lebanon (code 422), annual data, HS 2017 six-digit codes.

| File | Coverage | Rows × cols | Notes |
|---|---|---|---|
| `un_comtrade/comtrade_lbn_food_hs6_2015_2025_raw.csv` | 2015 – 2024 | 548 × 49 | Imports and exports (US$ value, net kg) for ~29 food codes, all partners combined. No 2025 data reported yet. Lebanon files wheat under HS 100119 |
| `un_comtrade/comtrade_lbn_imports_by_partner_2022_2024.csv` | 2022 – 2024 | 930 × 8 | Imports by supplier country for 19 staple codes |
| `un_comtrade/hs6_to_wfp_item_map.csv` | – | 29 × 3 | **Made for this project**: links each HS6 code to a WFP food item |

### Production (FAOSTAT)

Filtered to Lebanon from the FAOSTAT bulk downloads (`bulks-faostat.fao.org/production/`, Asia files).

| File | Coverage | Notes |
|---|---|---|
| `faostat/faostat_production_crops_livestock_lbn.csv` | 1961 – 2024 | Production volumes. Many recent values are FAO estimates (flag `E`/`I`) |
| `faostat/faostat_producer_prices_lbn.csv` | 1991 – 2025 | Farm-gate prices. ⚠️ Real values only to 2019; 2020-25 are model estimates (flag `E`) and are not used |
| `faostat/self_sufficiency_lbn_2015_2024.csv` | 2015 – 2024 | **Made for this project**: production ÷ (production + imports − exports) for 9 foods, from the two files above and Comtrade |

## Licences and credit

- WFP data on HDX: Creative Commons Attribution for Intergovernmental Organisations (CC BY-IGO)
- FAO / FAOSTAT and World Bank data: Creative Commons Attribution 4.0 (CC BY 4.0)
- CAS Lebanon and UN Comtrade: public official statistics; cite the source when reusing

Please credit the original publishers when reusing any of these files.
