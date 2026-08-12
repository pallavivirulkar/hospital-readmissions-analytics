-- Phase 6: Validate total_encounters using COUNT(*) OVER (PARTITION BY...)
SELECT
  COUNT(*) AS mismatch_count
FROM (
  SELECT
    patient_nbr,
    CAST(total_encounters AS INTEGER) AS python_total_encounters,
    COUNT(*) OVER (PARTITION BY patient_nbr) AS sql_total_encounters
  FROM encounters
)
WHERE python_total_encounters != sql_total_encounters;
