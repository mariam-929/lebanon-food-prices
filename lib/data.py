"""Cached loaders for the cleaned tables in ../data (built by pipeline/build_data.py)."""
from pathlib import Path

import pandas as pd
import streamlit as st

DATA = Path(__file__).resolve().parents[1] / "data"


@st.cache_data(ttl="1d", max_entries=32)
def load(name: str, dates: tuple[str, ...] = ("month",)) -> pd.DataFrame:
    df = pd.read_csv(DATA / f"{name}.csv")
    for c in dates:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c])
    return df


def national() -> pd.DataFrame:
    return load("prices_national_monthly")


def governorate() -> pd.DataFrame:
    return load("prices_governorate_monthly")


def world_vs_shelf() -> pd.DataFrame:
    return load("world_vs_shelf_monthly")


def cpi() -> pd.DataFrame:
    return load("cpi_monthly")


def fx() -> pd.DataFrame:
    return load("fx_monthly")


def items() -> pd.DataFrame:
    return load("items", dates=("first_month", "last_month"))


def affordability() -> pd.DataFrame:
    return load("affordability_yearly", dates=())


def unido_screen() -> pd.DataFrame:
    return load("unido_screen", dates=())


def partners() -> pd.DataFrame | None:
    return load("imports_by_partner", dates=()) if (DATA / "imports_by_partner.csv").exists() else None


def unit_label(std_unit: str) -> str:
    return {"kg": "per kg", "litre": "per litre", "egg": "per egg", "head": "per head"}.get(std_unit, std_unit)
