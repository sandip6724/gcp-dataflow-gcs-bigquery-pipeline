"""Pure transformations for the employee CSV batch pipeline."""
from __future__ import annotations

import csv
from datetime import datetime
from typing import Any

EXPECTED_COLUMNS = [
    "EmployeeID", "FirstName", "LastName", "Department",
    "Position", "Salary", "JoiningDate", "Country",
]

def parse_employee_row(line: str) -> dict[str, Any]:
    """Parse and validate one CSV data row (not the header)."""
    values = next(csv.reader([line], strict=True))
    if len(values) != len(EXPECTED_COLUMNS):
        raise ValueError(
            f"Expected {len(EXPECTED_COLUMNS)} columns, received {len(values)}"
        )

    employee_id = int(values[0])
    first_name, last_name, department, position = (
        value.strip() for value in values[1:5]
    )
    salary = int(values[5])
    joining_date = datetime.strptime(values[6].strip(), "%Y-%m-%d").date()
    country = values[7].strip()

    if employee_id <= 0:
        raise ValueError("EmployeeID must be a positive integer")
    if salary < 0:
        raise ValueError("Salary cannot be negative")
    if not first_name or not last_name:
        raise ValueError("FirstName and LastName are required")

    return {
        "EmployeeID": employee_id,
        "FirstName": first_name,
        "LastName": last_name,
        "Department": department,
        "Position": position,
        "Salary": salary,
        "JoiningDate": joining_date.isoformat(),
        "Country": country,
    }
