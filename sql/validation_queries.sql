-- Replace project_id and dataset_id before running.
-- Basic row-count and duplicate checks after a successful pipeline run.

SELECT COUNT(*) AS total_rows
FROM `project_id.dataset_id.employee_data`;

SELECT EmployeeID, COUNT(*) AS row_count
FROM `project_id.dataset_id.employee_data`
GROUP BY EmployeeID
HAVING COUNT(*) > 1
ORDER BY row_count DESC;

SELECT
  COUNTIF(EmployeeID IS NULL) AS null_employee_ids,
  COUNTIF(JoiningDate IS NULL) AS null_joining_dates,
  COUNTIF(Salary < 0) AS negative_salaries
FROM `project_id.dataset_id.employee_data`;
