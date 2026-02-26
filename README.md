# Timmerman Constraint Finder (Streamlit)

This repo hosts a simple public Streamlit web app that lets users select:
- Fractions
- OAR / Structure

…and view the associated constraints.

## Files
- `app.py` — Streamlit app
- `timmerman_constraints.csv` — data extracted from the Excel backend `_Data`
- `requirements.txt` — Python dependencies

## Deploy (Streamlit Community Cloud)
1. Push this folder to a GitHub repo.
2. Go to Streamlit Community Cloud and click **New app**.
3. Select your repo and set the main file to `app.py`.
4. Deploy.

## Update data
Replace `timmerman_constraints.csv` and redeploy (or push a commit).
