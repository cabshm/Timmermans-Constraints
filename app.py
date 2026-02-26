import pandas as pd
import streamlit as st
from datetime import date

APP_TITLE = "Timmerman Constraint Finder"
VERSION = "Vcc1.2"
DATA_FILE = "timmerman_constraints_vcc.csv"
DISCLAIMER = (
    "Disclaimer: This tool is provided for reference and convenience only. "
    "It does not replace clinical judgment, institutional policies, or peer review. "
    "Users are responsible for verifying constraints against the source material and the patient's clinical context."
)

st.set_page_config(page_title=APP_TITLE, layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    df["Contouring instructions"] = df["Contouring instructions"].fillna("Not given")
    df["Tissue"] = df["Tissue"].astype(str).str.strip()
    df["Type"] = df["Type"].astype(str).str.strip()
    return df

df = load_data()

st.title(APP_TITLE)

col1, col2 = st.columns([3,2])
with col1:
    st.caption(f"Version: **{VERSION}**  •  Date: **{date.today().isoformat()}**")
with col2:
    st.caption(DISCLAIMER)

st.divider()

fractions = sorted(df["Fractions"].dropna().unique().tolist())
fraction = st.selectbox("How many fractions?", options=fractions, index=fractions.index(3) if 3 in fractions else 0)

# Correct logic: always include parallel organs
df_serial = df[(df["Fractions"] == fraction) & (df["Type"].str.lower() == "serial")]
df_parallel = df[df["Type"].str.lower() == "parallel"]
df_fx = pd.concat([df_serial, df_parallel], ignore_index=True)

# Radio filter AFTER merge
type_filter = st.radio("Show", options=["All", "Serial only", "Parallel only"], horizontal=True)
if type_filter == "Serial only":
    df_fx = df_fx[df_fx["Type"].str.lower() == "serial"]
elif type_filter == "Parallel only":
    df_fx = df_fx[df_fx["Type"].str.lower() == "parallel"]

# Remove footnotes and non-organ entries
df_fx = df_fx[
    ~df_fx["Tissue"].str.contains("Abbreviations", case=False, na=False) &
    ~df_fx["Tissue"].str.startswith("*", na=False)
]
df_fx = df_fx[df_fx["Tissue"].str.strip() != ""]

oars = sorted(df_fx["Tissue"].dropna().unique().tolist())
oar = st.selectbox("Select OAR / Structure", options=oars)

df_oar = df_fx[df_fx["Tissue"] == oar].copy()
if "Occ" in df_oar.columns:
    df_oar = df_oar.sort_values(by=["Occ"])

show_cols = ["Type","Contouring instructions","Volume","Volume max (Gy)","Max point dose (Gy)","Endpoint"]
for c in show_cols:
    if c not in df_oar.columns:
        df_oar[c] = ""

st.subheader("Constraints")
st.dataframe(df_oar[show_cols].reset_index(drop=True), use_container_width=True, hide_index=True)
