# Data Sources

## 1. Diabetes 130-US Hospitals for Years 1999-2008 (Primary dataset)
- Source: Kaggle (kaggle.com/datasets/brandao/diabetes), originally from the
  UCI Machine Learning Repository
- License: CC0 — Public Domain
- File: data/raw/diabetic_data.csv
- Description: ~101,766 real patient hospital encounters across 130 US
  hospitals (1999-2008), diabetes-related admissions. Used as the core
  dataset for cleaning, readmission detection, and feature engineering.
- Note on recency: This dataset predates 2026, but was chosen deliberately
  for its patient/encounter-level granularity (includes patient_nbr and
  encounter_id, required for readmission self-join logic). Real-time
  healthcare data at this granularity is rarely public due to HIPAA
  privacy restrictions.

## 2. CMS FFS 30-Day Medicare Readmission Rate (Validation benchmark)
- Source: Kaggle (kaggle.com/datasets/cms/cms-ffs-30-day-medicare-readmission-rate),
  published directly by the Centers for Medicare & Medicaid Services (CMS)
- File: data/raw/ffs-medicare-30-day-readmission-rate-puf.csv
- Description: Official CMS Public Use File with national-level 30-day
  all-cause readmission rates for Medicare fee-for-service beneficiaries.
  Used to validate our calculated readmission rate against a real-world
  benchmark.