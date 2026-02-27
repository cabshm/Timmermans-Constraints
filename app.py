import io
import pandas as pd
import streamlit as st
from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table as RLTable, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

APP_TITLE = "Timmerman Constraint Finder"
VERSION = "Vcc1.4"
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
    df["Fractions"] = pd.to_numeric(df["Fractions"], errors="coerce").astype("Int64")
    df["Type"] = df["Type"].astype(str).str.strip()
    df["Tissue"] = df["Tissue"].astype(str).str.strip()
    df["Contouring instructions"] = df["Contouring instructions"].fillna("Not given")
    # Remove footnotes / abbreviations
    df = df[~df["Tissue"].str.startswith("*", na=False)]
    df = df[~df["Tissue"].str.contains("Abbreviations", case=False, na=False)]
    df = df[df["Tissue"].str.strip() != ""]
    return df

def style_by_type(df_show: pd.DataFrame):
    def _row_style(row):
        t = str(row.get("Type","")).lower()
        if t == "serial":
            return ["background-color: #F3F7FF"] * len(row)  # very light blue
        if t == "parallel":
            return ["background-color: #F3FFF6"] * len(row)  # very light green
        return [""] * len(row)
    return df_show.style.apply(_row_style, axis=1)

def build_pdf(fraction: int, oar: str, df_oar: pd.DataFrame) -> bytes:
    buff = io.BytesIO()
    doc = SimpleDocTemplate(buff, pagesize=letter, topMargin=36, bottomMargin=36, leftMargin=36, rightMargin=36)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(f"<b>{APP_TITLE}</b>", styles["Title"]))
    story.append(Paragraph(f"Version: {VERSION} &nbsp;&nbsp; Date: {date.today().isoformat()}", styles["Normal"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"<b>Fractions:</b> {fraction}", styles["Normal"]))
    story.append(Paragraph(f"<b>OAR / Structure:</b> {oar}", styles["Normal"]))
    story.append(Spacer(1, 12))

    cols = ["Type","Contouring instructions","Volume","Volume max (Gy)","Max point dose (Gy)","Endpoint"]
    for c in cols:
        if c not in df_oar.columns:
            df_oar[c] = ""

    table_data = [cols] + df_oar[cols].fillna("").astype(str).values.tolist()

    t = RLTable(table_data, repeatRows=1, hAlign="LEFT")
    ts = TableStyle([
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 10),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#305496")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.5, colors.lightgrey),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("FONTSIZE", (0,1), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.HexColor("#F7F7F7")]),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ])
    t.setStyle(ts)
    story.append(t)
    story.append(Spacer(1, 12))
    story.append(Paragraph(DISCLAIMER, styles["Normal"]))

    doc.build(story)
    return buff.getvalue()

df = load_data()

st.title(APP_TITLE)

col1, col2 = st.columns([3,2])
with col1:
    st.caption(f"Version: **{VERSION}**  •  Date: **{date.today().isoformat()}**")
with col2:
    st.caption(DISCLAIMER)

st.divider()

fractions = sorted([int(x) for x in df["Fractions"].dropna().unique().tolist()])
fraction = st.selectbox("How many fractions?", options=fractions, index=fractions.index(3) if 3 in fractions else 0)

df_fx = df[df["Fractions"] == fraction].copy()

type_filter = st.radio("Show", options=["All", "Serial only", "Parallel only"], horizontal=True)
if type_filter == "Serial only":
    df_fx = df_fx[df_fx["Type"].str.lower() == "serial"]
elif type_filter == "Parallel only":
    df_fx = df_fx[df_fx["Type"].str.lower() == "parallel"]

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
df_show = df_oar[show_cols].reset_index(drop=True)
st.dataframe(style_by_type(df_show), use_container_width=True, hide_index=True)

pdf_bytes = build_pdf(fraction, oar, df_oar.copy())
st.download_button(
    label="Export selected constraints to PDF",
    data=pdf_bytes,
    file_name=f"Timmerman_{fraction}fx_{oar.replace(' ','_')}.pdf",
    mime="application/pdf",
)
