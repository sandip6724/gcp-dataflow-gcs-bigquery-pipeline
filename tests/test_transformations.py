import pytest

from src.transformations import parse_employee_row

def test_parse_valid_employee_row():
    row = "1,Robert,Wilson,HR,HR Specialist,95161,2021-03-08,Germany"
    result = parse_employee_row(row)

    assert result["EmployeeID"] == 1
    assert result["Salary"] == 95161
    assert result["JoiningDate"] == "2021-03-08"
    assert result["Country"] == "Germany"

@pytest.mark.parametrize("row", [
    "1,Robert,Wilson,HR,HR Specialist,95161,not-a-date,Germany",
    "x,Robert,Wilson,HR,HR Specialist,95161,2021-03-08,Germany",
    "1,Robert,Wilson,HR,HR Specialist,-1,2021-03-08,Germany",
    "1,Robert,Wilson,HR",
])
def test_invalid_employee_rows_are_rejected(row):
    with pytest.raises((ValueError, Exception)):
        parse_employee_row(row)
