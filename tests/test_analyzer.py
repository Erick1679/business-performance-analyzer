import pytest
from datetime import date

from src.analyzer import (
    BusinessRecord,
    InvalidBusinessDataError,
    calculate_average_transaction,
    calculate_profit,
    calculate_profit_margin,
    get_currency_name,
    get_lowest_transaction_by_profit,
    get_top_transaction_by_profit,
    load_records_from_csv,
    rank_transactions_by_profit,
    summarize_by_currency,
    summarize_records,
)
from src.calendar import (
    analyze_daily_performance,
    build_daily_calendar,
    calculate_daily_profit_margin,
    generate_calendar,
    get_active_daily_performance,
)

def test_calculate_profit():
    assert calculate_profit(15000, 9000) == 6000


def test_calculate_profit_margin():
    assert calculate_profit_margin(15000, 6000) == 40


def test_profit_margin_with_zero_sales():
    assert calculate_profit_margin(0, 0) == 0


def test_get_currency_name_usd():
    assert get_currency_name("USD") == "US Dollar"


def test_get_currency_name_lowercase():
    assert get_currency_name("usd") == "US Dollar"


def test_get_currency_name_invalid_code():
    assert get_currency_name("ZZZ") is None


def test_business_record():
    record = BusinessRecord(
        date="2026-10-01",
        description="Consulting Project",
        sales=15000,
        expenses=9000,
        currency="USD",
    )

    assert record.date == "2026-10-01"
    assert record.description == "Consulting Project"
    assert record.sales == 15000
    assert record.expenses == 9000
    assert record.currency == "USD"
    assert record.profit == 6000
    assert record.profit_margin == 40


def test_summarize_records():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting Project",
            sales=15000,
            expenses=9000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-02",
            description="Data Analysis",
            sales=10000,
            expenses=6000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-03",
            description="Training",
            sales=5000,
            expenses=4000,
            currency="USD",
        ),
    ]

    summary = summarize_records(records)

    assert summary["total_sales"] == 30000
    assert summary["total_expenses"] == 19000
    assert summary["total_profit"] == 11000
    assert summary["profit_margin"] == (11000 / 30000) * 100


def test_calculate_average_transaction():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting Project",
            sales=15000,
            expenses=9000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-02",
            description="Data Analysis",
            sales=10000,
            expenses=6000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-03",
            description="Training",
            sales=5000,
            expenses=4000,
            currency="USD",
        ),
    ]

    averages = calculate_average_transaction(records)

    assert averages["average_sales"] == 10000
    assert averages["average_expenses"] == (19000 / 3)
    assert averages["average_profit"] == (11000 / 3)


def test_calculate_average_transaction_with_empty_records():
    averages = calculate_average_transaction([])

    assert averages["average_sales"] == 0
    assert averages["average_expenses"] == 0
    assert averages["average_profit"] == 0


def test_load_records_from_csv():
    records = load_records_from_csv("data/raw/business_data.csv")

    assert len(records) == 5

    assert records[0].date == "2026-10-01"
    assert records[0].description == "Consulting Project"
    assert records[0].sales == 15000
    assert records[0].expenses == 9000
    assert records[0].currency == "USD"

    assert records[4].date == "2026-10-05"
    assert records[4].description == "Business Consulting"
    assert records[4].sales == 12000
    assert records[4].expenses == 7000
    assert records[4].currency == "EUR"


def test_summarize_by_currency():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting Project",
            sales=15000,
            expenses=9000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-02",
            description="Data Analysis",
            sales=10000,
            expenses=6000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-05",
            description="Business Consulting",
            sales=12000,
            expenses=7000,
            currency="EUR",
        ),
    ]

    summaries = summarize_by_currency(records)

    assert summaries["USD"]["total_sales"] == 25000
    assert summaries["USD"]["total_expenses"] == 15000
    assert summaries["USD"]["total_profit"] == 10000

    assert summaries["EUR"]["total_sales"] == 12000
    assert summaries["EUR"]["total_expenses"] == 7000
    assert summaries["EUR"]["total_profit"] == 5000


def test_csv_missing_required_column(tmp_path):
    csv_file = tmp_path / "missing_column.csv"

    csv_file.write_text(
        "date,description,sales,expenses\n"
        "2026-10-01,Consulting Project,15000,9000\n",
        encoding="utf-8",
    )

    with pytest.raises(
        InvalidBusinessDataError,
        match="missing required columns: currency",
    ):
        load_records_from_csv(csv_file)


def test_csv_invalid_numeric_value(tmp_path):
    csv_file = tmp_path / "invalid_number.csv"

    csv_file.write_text(
        "date,description,sales,expenses,currency\n"
        "2026-10-01,Consulting Project,not-a-number,9000,USD\n",
        encoding="utf-8",
    )

    with pytest.raises(
        InvalidBusinessDataError,
        match="Invalid sales or expenses value on row 2",
    ):
        load_records_from_csv(csv_file)


def test_csv_unsupported_currency(tmp_path):
    csv_file = tmp_path / "invalid_currency.csv"

    csv_file.write_text(
        "date,description,sales,expenses,currency\n"
        "2026-10-01,Consulting Project,15000,9000,ZZZ\n",
        encoding="utf-8",
    )

    with pytest.raises(
        InvalidBusinessDataError,
        match="Unsupported currency 'ZZZ' on row 2",
    ):
        load_records_from_csv(csv_file)


def test_csv_blank_numeric_value(tmp_path):
    csv_file = tmp_path / "blank_value.csv"

    csv_file.write_text(
        "date,description,sales,expenses,currency\n"
        "2026-10-01,Consulting Project,15000,,USD\n",
        encoding="utf-8",
    )

    with pytest.raises(
        InvalidBusinessDataError,
        match="Invalid sales or expenses value on row 2",
    ):
        load_records_from_csv(csv_file)


def test_csv_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_records_from_csv("data/raw/does_not_exist.csv")


def test_get_top_transaction_by_profit():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting Project",
            sales=15000,
            expenses=9000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-02",
            description="Data Analysis",
            sales=10000,
            expenses=6000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-03",
            description="Training",
            sales=5000,
            expenses=4000,
            currency="USD",
        ),
    ]

    top_transaction = get_top_transaction_by_profit(records)

    assert top_transaction.description == "Consulting Project"
    assert top_transaction.profit == 6000
def test_get_lowest_transaction_by_profit():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting Project",
            sales=15000,
            expenses=9000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-02",
            description="Data Analysis",
            sales=10000,
            expenses=6000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-03",
            description="Training",
            sales=5000,
            expenses=4000,
            currency="USD",
        ),
    ]

    lowest_transaction = get_lowest_transaction_by_profit(records)

    assert lowest_transaction.description == "Training"
    assert lowest_transaction.profit == 1000
def test_rank_transactions_by_profit():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting Project",
            sales=15000,
            expenses=9000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-02",
            description="Data Analysis",
            sales=10000,
            expenses=6000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-03",
            description="Training",
            sales=5000,
            expenses=4000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-04",
            description="Executive Assistance",
            sales=8000,
            expenses=3500,
            currency="USD",
        ),
    ]

    ranked_transactions = rank_transactions_by_profit(records)

    assert ranked_transactions[0].description == "Consulting Project"
    assert ranked_transactions[0].profit == 6000

    assert ranked_transactions[1].description == "Executive Assistance"
    assert ranked_transactions[1].profit == 4500

    assert ranked_transactions[2].description == "Data Analysis"
    assert ranked_transactions[2].profit == 4000

    assert ranked_transactions[3].description == "Training"
    assert ranked_transactions[3].profit == 1000
def test_generate_calendar_for_non_leap_year():
    dates = generate_calendar(2026)

    assert dates[0].isoformat() == "2026-01-01"
    assert dates[-1].isoformat() == "2026-12-31"
    assert len(dates) == 365


def test_generate_calendar_for_leap_year():
    dates = generate_calendar(2028)

    assert dates[0].isoformat() == "2028-01-01"
    assert dates[-1].isoformat() == "2028-12-31"
    assert len(dates) == 366


def test_generate_calendar_includes_february_29_in_leap_year():
    dates = generate_calendar(2028)

    assert date(2028, 2, 29) in dates
def test_build_daily_calendar_includes_dates_without_transactions():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting Project",
            sales=15000,
            expenses=9000,
            currency="USD",
        )
    ]

    daily_data = build_daily_calendar(records, 2026)

    assert len(daily_data) == 365

    assert daily_data[date(2026, 1, 1)] == {
        "sales": 0,
        "expenses": 0,
        "profit": 0,
        "transaction_count": 0,
    }

    assert daily_data[date(2026, 10, 1)] == {
        "sales": 15000,
        "expenses": 9000,
        "profit": 6000,
        "transaction_count": 1,
    }


def test_build_daily_calendar_combines_multiple_transactions_on_same_date():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting Project",
            sales=15000,
            expenses=9000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-01",
            description="Data Analysis",
            sales=10000,
            expenses=6000,
            currency="USD",
        ),
    ]

    daily_data = build_daily_calendar(records, 2026)

    assert daily_data[date(2026, 10, 1)] == {
        "sales": 25000,
        "expenses": 15000,
        "profit": 10000,
        "transaction_count": 2,
    }
def test_analyze_daily_performance():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting Project",
            sales=15000,
            expenses=9000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-02",
            description="Data Analysis",
            sales=10000,
            expenses=6000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-03",
            description="Training",
            sales=5000,
            expenses=4000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-04",
            description="Executive Assistance",
            sales=8000,
            expenses=3500,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-05",
            description="Business Consulting",
            sales=12000,
            expenses=7000,
            currency="EUR",
        ),
    ]

    daily_data = build_daily_calendar(records, 2026)
    analysis = analyze_daily_performance(daily_data)

    assert analysis["total_sales"] == 50000
    assert analysis["total_expenses"] == 29500
    assert analysis["total_profit"] == 20500

    assert analysis["active_days"] == 5
    assert analysis["inactive_days"] == 360

    highest_date, highest_data = analysis["highest_profit_day"]
    assert highest_date == date(2026, 10, 1)
    assert highest_data["profit"] == 6000

    lowest_date, lowest_data = analysis["lowest_profit_day"]
    assert lowest_date == date(2026, 10, 3)
    assert lowest_data["profit"] == 1000


def test_analyze_daily_performance_with_no_transactions():
    daily_data = {
        date(2026, 1, 1): {
            "sales": 0,
            "expenses": 0,
            "profit": 0,
            "transaction_count": 0,
        },
        date(2026, 1, 2): {
            "sales": 0,
            "expenses": 0,
            "profit": 0,
            "transaction_count": 0,
        },
    }

    analysis = analyze_daily_performance(daily_data)

    assert analysis["total_sales"] == 0
    assert analysis["total_expenses"] == 0
    assert analysis["total_profit"] == 0

    assert analysis["active_days"] == 0
    assert analysis["inactive_days"] == 2

    assert analysis["highest_profit_day"] is None
    assert analysis["lowest_profit_day"] is None
def test_calculate_daily_profit_margin():
    day_data = {
        "sales": 10000,
        "expenses": 6000,
        "profit": 4000,
        "transaction_count": 1,
    }

    margin = calculate_daily_profit_margin(day_data)

    assert margin == 40


def test_get_active_daily_performance():
    daily_data = {
        date(2026, 10, 1): {
            "sales": 15000,
            "expenses": 9000,
            "profit": 6000,
            "transaction_count": 1,
        },
        date(2026, 10, 2): {
            "sales": 0,
            "expenses": 0,
            "profit": 0,
            "transaction_count": 0,
        },
        date(2026, 10, 3): {
            "sales": 5000,
            "expenses": 4000,
            "profit": 1000,
            "transaction_count": 1,
        },
    }

    active_days = get_active_daily_performance(daily_data)

    assert len(active_days) == 2

    assert active_days[0]["date"] == date(2026, 10, 1)
    assert active_days[0]["transaction_count"] == 1
    assert active_days[0]["sales"] == 15000
    assert active_days[0]["expenses"] == 9000
    assert active_days[0]["profit"] == 6000
    assert active_days[0]["profit_margin"] == 40

    assert active_days[1]["date"] == date(2026, 10, 3)
    assert active_days[1]["transaction_count"] == 1
    assert active_days[1]["sales"] == 5000
    assert active_days[1]["expenses"] == 4000
    assert active_days[1]["profit"] == 1000
    assert active_days[1]["profit_margin"] == 20
