# Lebanon food prices dashboard (prototype)

MSBA 325 project. Streamlit app with four pages:

| Page | Audience | What it shows |
|---|---|---|
| Overview | everyone | Food CPI vs other costs, US$ price changes by item, healthy-diet affordability |
| Price monitor | consumer protection | Flags: shelf vs world price, gaps between governorates, items rising while the lira is stable |
| Import dependence | UNIDO | Self-sufficiency, import bills, adjustable priority screen, supplier countries |
| About the data | everyone | Sources, cleaning steps, limits, downloads |

## Run locally

```bash
pip install -r requirements.txt
python pipeline/build_data.py      # only needed after raw data changes
streamlit run streamlit_app.py
```

Raw files live in `../datasets/lebanon food prices/`. The pipeline writes cleaned CSVs to `data/`
(the app only reads `data/`, so the raw folder is not needed for deployment). The same CSVs can be
loaded into Tableau Public.

## Deploy (public link, works on phones)

1. Create a GitHub repository and push this folder (including `data/`).
2. Go to <https://share.streamlit.io>, sign in with GitHub, choose **New app**, pick the repo and
   `streamlit_app.py`.
3. Share the resulting `*.streamlit.app` link with contacts and embed it in the blog post.
