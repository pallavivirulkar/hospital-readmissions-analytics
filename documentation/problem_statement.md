# Business Problem Statement — Hospital Readmissions & Patient Flow Analytics

## Background
CityCare Hospitals (fictional hospital network, used for this analysis) is
subject to CMS's Hospital Readmissions Reduction Program (HRRP), which
penalizes hospitals up to 3% of Medicare reimbursement when their 30-day
readmission rates exceed the CMS-expected rate for specific conditions.

## Problem Statement
Hospital leadership does not have a clear, data-driven view of:
- Which diagnosis categories and patient segments are driving 30-day
  readmissions
- How their readmission performance compares to CMS-expected benchmarks
- What the estimated financial exposure from HRRP penalties is
- Whether patient flow factors (e.g., length of stay) relate to readmission risk

## Objective
Build an end-to-end analytics solution (Python → SQL → Power BI) that
identifies readmission drivers, quantifies financial risk, and enables
leadership to simulate the impact of readmission-reduction initiatives.

## Key Stakeholders
- Hospital Operations / Quality Improvement team (primary audience)
- Finance team (penalty exposure, cost impact)
- Care Management team (patient flow, discharge planning)

## Key KPIs
- 30-Day Readmission Rate
- Excess Readmission Ratio (actual vs. CMS-expected)
- Average Length of Stay (LOS)
- Estimated Penalty Exposure ($)

## Scope
- Encounter-level data for diabetes-related hospital admissions
- Readmission detection within a 30-day window of prior discharge
- Analysis at patient, diagnosis, and hospital-region level

## Out of Scope
- Real-time/live data integration (this is a historical/batch analysis)
- Clinical treatment recommendations (this is an operational/financial
  analytics project, not a clinical decision tool)

## Success Criteria
A working Power BI dashboard that lets a hospital manager identify top
readmission drivers, see estimated financial exposure, and simulate the
impact of a target readmission-reduction percentage.