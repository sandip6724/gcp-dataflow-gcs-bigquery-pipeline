import pytest

from src.transformations import parse_employee_row


def test_parse_valid_employee_row():
    row = '1,"Robert","Wilson","HR","HR Specialist",95161,2021-03-08,Germany'
    result = parse_employee_row(row)

    assert result == {
        "EmployeeID": 1,
        "FirstName": "Robert",
        "LastName": "Wilson",
        "Department": "HR",
        "Position": "HR Specialist",
        "Salary": 95161,
        "JoiningDate": "2021-03-08",
        "Country": "Germany",
    }


def test_parse_quoted_comma():
    row = '2,"Linda, Jr.","Johnson","Engineering","Data Scientist",52274,2010-09-26,UK'
    result = parse_employee_row(row)
    assert result["FirstName"] == "Linda, Jr."


@pytest.mark.parametrize(
    "row",
    [
        "1,Robert,Wilson,HR,HR Specialist,95161,not-a-date,Germany",
        "x,Robert,Wilson,HR,HR Specialist,95161,2021-03-08,Germany",
        "1,Robert,Wilson,HR,HR Specialist,-1,2021-03-08,Germany",
        "1,Robert,Wilson,HR",
        "0,Robert,Wilson,HR,HR Specialist,95161,2021-03-08,Germany",
        "1,,Wilson,HR,HR Specialist,95161,2021-03-08,Germany",
    ],
)
def test_invalid_employee_rows_are_rejected(row):
    with pytest.raises(ValueError):
        parse_employee_row(row)
