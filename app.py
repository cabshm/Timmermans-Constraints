import pandas as pd
import streamlit as st
from datetime import date

# ====== CONFIG ======
APP_TITLE = "Timmerman Constraint Finder"
VERSION = "Vcc1"
DATA_FILE = "timmerman_constraints.csv"
DISCLAIMER = (
    "Disclaimer: This tool is provided for reference and convenience only. "
    "It does not replace clinical judgment, institutional policies, or peer review. "
    "Users are responsible for verifying constraints against the source material and the patient's clinical context."
)

st.set_page_config(page_title=APP_TITLE, layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    # Normalize blanks
    df["Contouring instructions"] = df["Contouring instructions"].fillna("Not given")
    return df

df = load_data()

st.title(APP_TITLE)

col1, col2 = st.columns([3,2])
with col1:
    st.caption(f"Version: **{VERSION}**  •  Date: **{date.today().isoformat()}**")
with col2:
    st.caption(DISCLAIMER)

st.divider()

# Controls
fractions = sorted(df["Fractions"].dropna().unique().tolist())
fraction = st.selectbox("How many fractions?", options=fractions, index=fractions.index(3) if 3 in fractions else 0)

df_fx = df[df["Fractions"] == fraction].copy()

# OAR dropdown
oars = sorted(df_fx["Tissue"].dropna().unique().tolist())
oar = st.selectbox("Select OAR / Structure", options=oars)

df_oar = df_fx[df_fx["Tissue"] == oar].copy()

# Sort occurrences if present
if "Occ" in df_oar.columns:
    df_oar = df_oar.sort_values(by=["Occ"])
else:
    df_oar = df_oar.sort_values(by=["Type"])

# Display results in a table-like view (one row per constraint line)
show_cols = [
    "Type",
    "Contouring instructions",
    "Volume",
    "Volume max (Gy)",
    "Max point dose (Gy)",
    "Endpoint",
]
for c in show_cols:
    if c not in df_oar.columns:
        df_oar[c] = ""

st.subheader("Constraints")
st.dataframe(
    df_oar[show_cols].reset_index(drop=True),
    use_container_width=True,
    hide_index=True
)

with st.expander("Show raw rows (debug)"):
    st.dataframe(df_oar.reset_index(drop=True), use_container_width=True, hide_index=True)
