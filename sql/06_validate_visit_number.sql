-- Phase 6: Validate visit_number using ROW_NUMBER() window function
-- Compares Python-generated visit_number (Phase 5) against SQL-derived value
SELECT
  COUNT(*) AS mismatch_count
FROM (
  SELECT
    patient_nbr,
    encounter_id,
    CAST(visit_number AS INTEGER) AS python_visit_number,
    ROW_NUMBER() OVER (
      PARTITION BY patient_nbr
      ORDER BY CAST(encounter_id AS INTEGER)
    ) AS sql_visit_number
  FROM encounters
)
WHERE python_visit_number != sql_visit_number;
