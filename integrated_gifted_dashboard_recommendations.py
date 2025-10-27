
# integrated_gifted_dashboard_recommendations.py

"""
Gifted Identification Dashboard (Streamlit)

To run:
    pip install streamlit pandas numpy matplotlib
    streamlit run integrated_gifted_dashboard_recommendations.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from typing import Dict, Tuple, Optional


def _safe_rate(numer: pd.Series, denom: pd.Series) -> float:
    try:
        n = float(np.nansum(numer.astype(float)))
        d = float(np.nansum(denom.astype(float)))
        return n / d if d > 0 else np.nan
    except Exception:
        return np.nan


def selection_rate(df: pd.DataFrame, outcome_col: str) -> float:
    return _safe_rate(df[outcome_col], pd.Series(np.ones(len(df))))


def group_rates(df: pd.DataFrame, group_col: str, outcome_col: str) -> pd.DataFrame:
    g = (
        df.groupby(group_col, dropna=False)
        .apply(lambda x: selection_rate(x, outcome_col))
        .reset_index(name="rate")
    )
    totals = df[group_col].value_counts(dropna=False).rename("n").reset_index()
    totals.columns = [group_col, "n"]
    return g.merge(totals, on=group_col, how="left").sort_values("rate", ascending=False)


def disparity_table(df: pd.DataFrame, group_col: str, outcome_col: str, reference: Optional[str] = None) -> pd.DataFrame:
    rates = group_rates(df, group_col, outcome_col)
    overall = selection_rate(df, outcome_col)

    if reference is None and len(rates) > 0:
        reference = rates.iloc[0][group_col]

    try:
        ref_rate = float(rates.loc[rates[group_col] == reference, "rate"].values[0])
    except:
        ref_rate = overall

    rates["rate_diff_vs_overall"] = rates["rate"] - overall
    rates["risk_ratio_vs_overall"] = rates["rate"] / overall if overall and not np.isnan(overall) and overall > 0 else np.nan
    rates["rate_vs_ref"] = rates["rate"] / ref_rate if ref_rate and not np.isnan(ref_rate) and ref_rate > 0 else np.nan
    rates["reference_group"] = reference
    return rates


def pct(x: float) -> str:
    return "-" if np.isnan(x) else f"{x*100:0.1f}%"


def add_basic_recommendations(title: str):
    st.subheader(title)
    st.markdown(
        """
- Standardize referrals using universal screening.
- Use multiple measures (nonverbal tests, rating scales, portfolios).
- Monitor cut-scores for subgroup disparities.
- Review each pipeline step: referred -> tested -> qualified -> placed.
- Strengthen family outreach and communication.
- Re-audit each semester to track improvement.
        """
    )


# ---------------- UI ----------------

st.set_page_config(page_title="Gifted Identification Dashboard", layout="wide")

st.title("🎓 Gifted Identification Dashboard")
st.caption("Identify and address inequities in gifted & talented selection pipelines.")

with st.sidebar:
    st.header("Upload Data")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])

    st.header("Column Mapping")
    col_map_defaults: Dict[str, str] = {
        "school_year": "school_year",
        "grade": "grade",
        "gender": "gender",
        "race_ethnicity": "race_ethnicity",
        "ell": "ell",
        "iep": "iep",
        "frl": "frl",
        "referred": "referred",
        "tested": "tested",
        "qualified": "qualified",
        "placed": "placed",
    }

    col_map = {k: st.text_input(k, v) for k, v in col_map_defaults.items()}

    st.header("Analysis Settings")
    group_col = st.selectbox("Group by:", list(col_map.keys()))
    outcome_col = st.selectbox("Outcome:", ["referred", "tested", "qualified", "placed"])
    use_latest_year = st.checkbox("Filter to most recent school year", True)
    min_group_size = st.number_input("Min group size", min_value=1, value=10)


if uploaded is None:
    st.info("Upload a CSV to begin.")
    st.stop()

df = pd.read_csv(uploaded)

rename_dict = {col_map[k]: k for k in col_map if col_map[k] in df.columns and col_map[k] != k}
df.rename(columns=rename_dict, inplace=True)

required = ["school_year", "grade", "gender", "race_ethnicity", "referred", "tested", "qualified", "placed"]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error(f"Missing columns: {missing}")
    st.stop()

for c in ["referred", "tested", "qualified", "placed", "ell", "iep", "frl"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

if use_latest_year:
    try:
        df["_year"] = df["school_year"].astype(str).str.extract(r"(\d{4})").astype(float)
        df = df[df["_year"] == df["_year"].max()].drop(columns=["_year"])
    except:
        pass

col1, col2, col3 = st.columns(3)
col1.metric("Referral Rate", pct(selection_rate(df, "referred")))
col2.metric("Qualification Rate", pct(selection_rate(df, "qualified")))
col3.metric("Placement Rate", pct(selection_rate(df, "placed")))

st.markdown("---")

st.subheader(f"Disparities by {group_col} for {outcome_col}")
tbl = group_rates(df, group_col, outcome_col)
tbl = tbl[tbl["n"] >= min_group_size]

if len(tbl) == 0:
    st.warning("No groups meet minimum size.")
else:
    disp = disparity_table(df[df[group_col].isin(tbl[group_col])], group_col, outcome_col)
    st.dataframe(disp, use_container_width=True)

    fig, ax = plt.subplots()
    ax.bar(tbl[group_col].astype(str), tbl["rate"].values)
    ax.set_title(f"{outcome_col.capitalize()} Rate by {group_col}")
    ax.set_xlabel(group_col)
    ax.set_ylabel("Rate")
    plt.xticks(rotation=30, ha="right")
    st.pyplot(fig, clear_figure=True)

st.subheader("Pipeline Funnel")
funnel = pd.DataFrame({
    "Stage": ["Referred", "Tested", "Qualified", "Placed"],
    "Count": [
        int(np.nansum(df["referred"])),
        int(np.nansum(df["tested"])),
        int(np.nansum(df["qualified"])),
        int(np.nansum(df["placed"])),
    ],
})
fig2, ax2 = plt.subplots()
ax2.plot(funnel["Stage"], funnel["Count"], marker="o")
ax2.set_title("Pipeline Counts")
st.pyplot(fig2, clear_figure=True)

add_basic_recommendations("Suggested Actions")
