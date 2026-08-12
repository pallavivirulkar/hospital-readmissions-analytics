-- Phase 6: Validate readmitted_flag using CASE WHEN
SELECT
  COUNT(*) AS mismatch_count
FROM (
  SELECT
    readmitted,
    CAST(readmitted_flag AS INTEGER) AS python_flag,
    CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END AS sql_flag
  FROM encounters
)
WHERE python_flag != sql_flag;
