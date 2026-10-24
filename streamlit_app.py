import streamlit as st

st.set_page_config(page_title="Lebanon food prices", page_icon=":material/shopping_basket:", layout="wide")

page = st.navigation(
    [
        st.Page("app_pages/overview.py", title="Overview", icon=":material/insights:", default=True),
        st.Page("app_pages/price_monitor.py", title="Price monitor", icon=":material/policy:"),
        st.Page("app_pages/import_dependence.py", title="Import dependence", icon=":material/local_shipping:"),
        st.Page("app_pages/about.py", title="About the data", icon=":material/info:"),
    ],
    position="top",
)
page.run()

st.caption("Prototype · MSBA 325, American University of Beirut · Sources: WFP, CAS, FAO, World Bank, UN Comtrade")
