# Hospital Readmissions & Patient Flow Analytics — Streamlit Dashboard

Interactive companion dashboard to the Tableau version. Same data, same calculated
fields (Readmission Rate, Estimated Financial Risk, Repeat Patient, High-Risk Patient),
built with Python instead of a BI tool.

## Run it on your Mac

Copy this whole `streamlit_project` folder into your project (e.g. next to `tableau/`),
then in Terminal:

```bash
cd streamlit_project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard.py
```

It will open automatically at `http://localhost:8501`. Press `Ctrl+C` in Terminal to stop it.

## Pages

1. **Executive Overview** — KPI cards + readmission rate by age + repeat-patient risk concentration
2. **Readmission Drivers** — by admission type, race, discharge disposition, prior inpatient stays
3. **Patient Flow** — repeat vs. first-time, high-risk vs. standard, visit-number distribution
4. **Financial Impact** — risk by admission type / discharge disposition / age group
5. **What-If Simulator** — interactive slider to model savings from reducing readmission rate in a target segment

## Data

Reads directly from `data/*.csv` (the same 5 star-schema exports used in the Tableau workbook:
`fact_encounters`, `dim_patient`, `dim_admission_type`, `dim_discharge_disposition`, `dim_admission_source`).
If you re-export from SQLite later, just overwrite these files — no code changes needed.

Cost assumption: $16,300 per 30-day all-cause adult readmission (HCUP/AHRQ, 2020).
