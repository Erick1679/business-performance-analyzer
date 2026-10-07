from datetime import date

import pytest

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
    summarize_by_description,
    summarize_by_service,
    summarize_records,
)

from src.calendar import (
    analyze_daily_performance,
    build_daily_calendar,
    calculate_daily_profit_margin,
    filter_records_by_date_range,
    generate_calendar,
    get_active_daily_performance,
    get_daily_performance,
    get_performance_between_dates,
    summarize_monthly_performance,
)


def test_calculate_profit():
    assert calculate_profit(10000, 6000) == 4000


def test_calculate_profit_margin():
    assert calculate_profit_margin(10000, 4000) == 40


def test_calculate_profit_margin_with_zero_sales():
    assert calculate_profit_margin(0, 0) == 0


def test_business_record_profit():
    record = BusinessRecord(
        date="2026-10-01",
        description="Consulting",
        sales=10000,
        expenses=6000,
        currency="USD",
    )

    assert record.profit == 4000


def test_business_record_profit_margin():
    record = BusinessRecord(
        date="2026-10-01",
        description="Consulting",
        sales=10000,
        expenses=6000,
        currency="USD",
    )

    assert record.profit_margin == 40


def test_business_record_zero_sales_margin():
    record = BusinessRecord(
        date="2026-10-01",
        description="Consulting",
        sales=0,
        expenses=0,
        currency="USD",
    )

    assert record.profit_margin == 0


def test_business_record_service_defaults_to_description():
    record = BusinessRecord(
        date="2026-10-01",
        description="Consulting",
        sales=10000,
        expenses=6000,
        currency="USD",
    )

    assert record.service == "Consulting"


def test_business_record_id_defaults_to_zero():
    record = BusinessRecord(
        date="2026-10-01",
        description="Consulting",
        sales=10000,
        expenses=6000,
        currency="USD",
    )

    assert record.id == 0


def test_business_record_accepts_id_and_service():
    record = BusinessRecord(
        date="2026-10-01",
        description="Consulting Project",
        sales=10000,
        expenses=6000,
        currency="USD",
        id=25,
        service="Business Consulting",
    )

    assert record.id == 25
    assert record.service == "Business Consulting"


def test_summarize_records():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting",
            sales=10000,
            expenses=6000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-02",
            description="Training",
            sales=5000,
            expenses=3000,
            currency="USD",
        ),
    ]

    summary = summarize_records(records)

    assert summary["total_sales"] == 15000
    assert summary["total_expenses"] == 9000
    assert summary["total_profit"] == 6000
    assert summary["profit_margin"] == 40


def test_summarize_records_with_empty_records():
    summary = summarize_records([])

    assert summary["total_sales"] == 0
    assert summary["total_expenses"] == 0
    assert summary["total_profit"] == 0
    assert summary["profit_margin"] == 0


def test_calculate_average_transaction():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting",
            sales=10000,
            expenses=6000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-02",
            description="Training",
            sales=5000,
            expenses=3000,
            currency="USD",
        ),
    ]

    averages = calculate_average_transaction(records)

    assert averages["average_sales"] == 7500
    assert averages["average_expenses"] == 4500
    assert averages["average_profit"] == 3000


def test_calculate_average_transaction_with_empty_records():
    averages = calculate_average_transaction([])

    assert averages["average_sales"] == 0
    assert averages["average_expenses"] == 0
    assert averages["average_profit"] == 0


def test_get_top_transaction_by_profit():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting",
            sales=10000,
            expenses=6000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-02",
            description="Training",
            sales=6000,
            expenses=1000,
            currency="USD",
        ),
    ]

    top_transaction = get_top_transaction_by_profit(records)

    assert top_transaction.description == "Training"
    assert top_transaction.profit == 5000


def test_get_top_transaction_with_empty_records():
    assert get_top_transaction_by_profit([]) is None


def test_get_lowest_transaction_by_profit():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting",
            sales=10000,
            expenses=6000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-02",
            description="Training",
            sales=5000,
            expenses=4500,
            currency="USD",
        ),
    ]

    lowest_transaction = get_lowest_transaction_by_profit(records)

    assert lowest_transaction.description == "Training"
    assert lowest_transaction.profit == 500


def test_get_lowest_transaction_with_empty_records():
    assert get_lowest_transaction_by_profit([]) is None


def test_rank_transactions_by_profit():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting",
            sales=10000,
            expenses=6000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-02",
            description="Training",
            sales=6000,
            expenses=1000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-03",
            description="Support",
            sales=4000,
            expenses=3000,
            currency="USD",
        ),
    ]

    ranked = rank_transactions_by_profit(records)

    assert ranked[0].description == "Training"
    assert ranked[1].description == "Consulting"
    assert ranked[2].description == "Support"


def test_get_currency_name():
    assert get_currency_name("USD") == "US Dollar"
    assert get_currency_name("EUR") == "Euro"


def test_get_currency_name_invalid_currency():
    assert get_currency_name("ZZZ") is None


def test_summarize_by_currency():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting",
            sales=15000,
            expenses=9000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-02",
            description="Training",
            sales=5000,
            expenses=4000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-03",
            description="Consulting",
            sales=12000,
            expenses=7000,
            currency="EUR",
        ),
    ]

    summaries = summarize_by_currency(records)

    assert summaries["USD"]["total_sales"] == 20000
    assert summaries["USD"]["total_expenses"] == 13000
    assert summaries["USD"]["total_profit"] == 7000
    assert summaries["USD"]["profit_margin"] == 35

    assert summaries["EUR"]["total_sales"] == 12000
    assert summaries["EUR"]["total_expenses"] == 7000
    assert summaries["EUR"]["total_profit"] == 5000
    assert summaries["EUR"]["profit_margin"] == pytest.approx(
        41.6666666667
    )


def test_summarize_by_description():
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
            description="Consulting Project",
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
            date="2026-10-05",
            description="Business Consulting",
            sales=12000,
            expenses=7000,
            currency="EUR",
        ),
    ]

    summaries = summarize_by_description(records)

    assert summaries["Consulting Project"]["USD"]["transaction_count"] == 2
    assert summaries["Consulting Project"]["USD"]["total_sales"] == 25000
    assert summaries["Consulting Project"]["USD"]["total_expenses"] == 15000
    assert summaries["Consulting Project"]["USD"]["total_profit"] == 10000
    assert summaries["Consulting Project"]["USD"]["profit_margin"] == 40

    assert summaries["Training"]["USD"]["transaction_count"] == 1
    assert summaries["Training"]["USD"]["total_profit"] == 1000

    assert summaries["Business Consulting"]["EUR"]["transaction_count"] == 1
    assert summaries["Business Consulting"]["EUR"]["total_sales"] == 12000
    assert summaries["Business Consulting"]["EUR"]["total_profit"] == 5000


def test_summarize_by_description_with_multiple_transactions():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Data Analysis",
            sales=10000,
            expenses=6000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-02",
            description="Data Analysis",
            sales=8000,
            expenses=4000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-03",
            description="Data Analysis",
            sales=12000,
            expenses=9000,
            currency="USD",
        ),
    ]

    summaries = summarize_by_description(records)

    data_analysis = summaries["Data Analysis"]["USD"]

    assert data_analysis["transaction_count"] == 3
    assert data_analysis["total_sales"] == 30000
    assert data_analysis["total_expenses"] == 19000
    assert data_analysis["total_profit"] == 11000
    assert data_analysis["profit_margin"] == pytest.approx(
        36.6666666667
    )


def test_summarize_by_description_keeps_currencies_separate():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting",
            sales=10000,
            expenses=6000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-02",
            description="Consulting",
            sales=12000,
            expenses=7000,
            currency="EUR",
        ),
    ]

    summaries = summarize_by_description(records)

    assert summaries["Consulting"]["USD"]["transaction_count"] == 1
    assert summaries["Consulting"]["USD"]["total_sales"] == 10000
    assert summaries["Consulting"]["USD"]["total_profit"] == 4000

    assert summaries["Consulting"]["EUR"]["transaction_count"] == 1
    assert summaries["Consulting"]["EUR"]["total_sales"] == 12000
    assert summaries["Consulting"]["EUR"]["total_profit"] == 5000


def test_summarize_by_description_with_zero_sales():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Free Consultation",
            sales=0,
            expenses=500,
            currency="USD",
        )
    ]

    summaries = summarize_by_description(records)

    service = summaries["Free Consultation"]["USD"]

    assert service["transaction_count"] == 1
    assert service["total_sales"] == 0
    assert service["total_expenses"] == 500
    assert service["total_profit"] == -500
    assert service["profit_margin"] == 0


def test_summarize_by_description_with_empty_records():
    summaries = summarize_by_description([])

    assert summaries == {}


def test_summarize_by_service():
    records = [
        BusinessRecord(
            id=1,
            date="2026-10-01",
            service="Consulting",
            description="Consulting Project",
            sales=15000,
            expenses=9000,
            currency="USD",
        ),
        BusinessRecord(
            id=2,
            date="2026-10-02",
            service="Consulting",
            description="Consulting Project",
            sales=10000,
            expenses=6000,
            currency="USD",
        ),
        BusinessRecord(
            id=3,
            date="2026-10-03",
            service="Training",
            description="Training Session",
            sales=5000,
            expenses=4000,
            currency="USD",
        ),
    ]

    summaries = summarize_by_service(records)

    assert summaries["Consulting"]["USD"]["transaction_count"] == 2
    assert summaries["Consulting"]["USD"]["total_sales"] == 25000
    assert summaries["Consulting"]["USD"]["total_profit"] == 10000
    assert summaries["Consulting"]["USD"]["profit_margin"] == 40

    assert summaries["Training"]["USD"]["transaction_count"] == 1
    assert summaries["Training"]["USD"]["total_profit"] == 1000


def test_load_records_from_csv(tmp_path):
    csv_file = tmp_path / "business_data.csv"

    csv_file.write_text(
        "date,description,sales,expenses,currency\n"
        "2026-10-01,Consulting,10000,6000,USD\n"
        "2026-10-02,Training,5000,3000,USD\n",
        encoding="utf-8",
    )

    records = load_records_from_csv(csv_file)

    assert len(records) == 2
    assert records[0].id == 1
    assert records[0].service == "Consulting"
    assert records[0].description == "Consulting"
    assert records[0].sales == 10000
    assert records[0].expenses == 6000
    assert records[0].currency == "USD"

    assert records[1].id == 2
    assert records[1].service == "Training"


def test_load_records_from_csv_with_id_and_service(tmp_path):
    csv_file = tmp_path / "business_data.csv"

    csv_file.write_text(
        "id,date,service,description,sales,expenses,currency\n"
        "101,2026-10-01,Consulting,Consulting Project,15000,9000,USD\n"
        "102,2026-10-02,Training,Training Session,5000,4000,USD\n",
        encoding="utf-8",
    )

    records = load_records_from_csv(csv_file)

    assert len(records) == 2

    assert records[0].id == 101
    assert records[0].service == "Consulting"
    assert records[0].description == "Consulting Project"

    assert records[1].id == 102
    assert records[1].service == "Training"
    assert records[1].description == "Training Session"


def test_load_records_invalid_id(tmp_path):
    csv_file = tmp_path / "business_data.csv"

    csv_file.write_text(
        "id,date,service,description,sales,expenses,currency\n"
        "ABC,2026-10-01,Consulting,Consulting Project,10000,6000,USD\n",
        encoding="utf-8",
    )

    with pytest.raises(
        InvalidBusinessDataError,
        match="Invalid id",
    ):
        load_records_from_csv(csv_file)


def test_load_records_empty_service_defaults_to_description(tmp_path):
    csv_file = tmp_path / "business_data.csv"

    csv_file.write_text(
        "id,date,service,description,sales,expenses,currency\n"
        "1,2026-10-01,,Consulting Project,10000,6000,USD\n",
        encoding="utf-8",
    )

    records = load_records_from_csv(csv_file)

    assert records[0].service == "Consulting Project"


def test_load_records_missing_column(tmp_path):
    csv_file = tmp_path / "business_data.csv"

    csv_file.write_text(
        "date,description,sales,currency\n"
        "2026-10-01,Consulting,10000,USD\n",
        encoding="utf-8",
    )

    with pytest.raises(
        InvalidBusinessDataError,
        match="missing required columns",
    ):
        load_records_from_csv(csv_file)


def test_load_records_invalid_date(tmp_path):
    csv_file = tmp_path / "business_data.csv"

    csv_file.write_text(
        "date,description,sales,expenses,currency\n"
        "invalid-date,Consulting,10000,6000,USD\n",
        encoding="utf-8",
    )

    with pytest.raises(
        InvalidBusinessDataError,
        match="Invalid date",
    ):
        load_records_from_csv(csv_file)


def test_load_records_invalid_numbers(tmp_path):
    csv_file = tmp_path / "business_data.csv"

    csv_file.write_text(
        "date,description,sales,expenses,currency\n"
        "2026-10-01,Consulting,abc,6000,USD\n",
        encoding="utf-8",
    )

    with pytest.raises(
        InvalidBusinessDataError,
        match="Invalid sales or expenses",
    ):
        load_records_from_csv(csv_file)


def test_load_records_invalid_currency(tmp_path):
    csv_file = tmp_path / "business_data.csv"

    csv_file.write_text(
        "date,description,sales,expenses,currency\n"
        "2026-10-01,Consulting,10000,6000,INVALID\n",
        encoding="utf-8",
    )

    with pytest.raises(
        InvalidBusinessDataError,
        match="Unsupported currency",
    ):
        load_records_from_csv(csv_file)


def test_generate_calendar():
    calendar_dates = generate_calendar(2026)

    assert len(calendar_dates) == 365
    assert calendar_dates[0] == date(2026, 1, 1)
    assert calendar_dates[-1] == date(2026, 12, 31)


def test_generate_calendar_leap_year():
    calendar_dates = generate_calendar(2024)

    assert len(calendar_dates) == 366
    assert date(2024, 2, 29) in calendar_dates


def test_build_daily_calendar():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting",
            sales=10000,
            expenses=6000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-01",
            description="Training",
            sales=5000,
            expenses=3000,
            currency="USD",
        ),
    ]

    daily_data = build_daily_calendar(records, year=2026)

    assert daily_data[date(2026, 10, 1)]["sales"] == 15000
    assert daily_data[date(2026, 10, 1)]["expenses"] == 9000
    assert daily_data[date(2026, 10, 1)]["profit"] == 6000
    assert daily_data[date(2026, 10, 1)]["transaction_count"] == 2


def test_build_daily_calendar_keeps_inactive_days():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting",
            sales=10000,
            expenses=6000,
            currency="USD",
        )
    ]

    daily_data = build_daily_calendar(records, year=2026)

    inactive_day = daily_data[date(2026, 10, 2)]

    assert inactive_day["sales"] == 0
    assert inactive_day["expenses"] == 0
    assert inactive_day["profit"] == 0
    assert inactive_day["transaction_count"] == 0


def test_build_daily_calendar_ignores_other_years():
    records = [
        BusinessRecord(
            date="2025-10-01",
            description="Old Consulting",
            sales=10000,
            expenses=6000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-01",
            description="Consulting",
            sales=5000,
            expenses=3000,
            currency="USD",
        ),
    ]

    daily_data = build_daily_calendar(records, year=2026)

    assert daily_data[date(2026, 10, 1)]["sales"] == 5000


def test_calculate_daily_profit_margin():
    day_data = {
        "sales": 10000,
        "expenses": 6000,
        "profit": 4000,
        "transaction_count": 1,
    }

    assert calculate_daily_profit_margin(day_data) == 40


def test_calculate_daily_profit_margin_zero_sales():
    day_data = {
        "sales": 0,
        "expenses": 0,
        "profit": 0,
        "transaction_count": 0,
    }

    assert calculate_daily_profit_margin(day_data) == 0


def test_get_active_daily_performance():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting",
            sales=10000,
            expenses=6000,
            currency="USD",
        )
    ]

    daily_data = build_daily_calendar(records, year=2026)

    active_days = get_active_daily_performance(daily_data)

    assert len(active_days) == 1
    assert active_days[0]["date"] == date(2026, 10, 1)
    assert active_days[0]["profit"] == 4000
    assert active_days[0]["profit_margin"] == 40


def test_analyze_daily_performance():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting",
            sales=10000,
            expenses=6000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-02",
            description="Training",
            sales=5000,
            expenses=4500,
            currency="USD",
        ),
    ]

    daily_data = build_daily_calendar(records, year=2026)

    analysis = analyze_daily_performance(daily_data)

    assert analysis["total_sales"] == 15000
    assert analysis["total_expenses"] == 10500
    assert analysis["total_profit"] == 4500
    assert analysis["active_days"] == 2
    assert analysis["inactive_days"] == 363

    highest_date, highest_data = analysis["highest_profit_day"]
    lowest_date, lowest_data = analysis["lowest_profit_day"]

    assert highest_date == date(2026, 10, 1)
    assert highest_data["profit"] == 4000

    assert lowest_date == date(2026, 10, 2)
    assert lowest_data["profit"] == 500


def test_get_daily_performance():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting",
            sales=10000,
            expenses=6000,
            currency="USD",
        )
    ]

    daily_data = build_daily_calendar(records, year=2026)

    result = get_daily_performance(
        daily_data,
        date(2026, 10, 1),
    )

    assert result["sales"] == 10000
    assert result["profit"] == 4000


def test_get_performance_between_dates():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting",
            sales=10000,
            expenses=6000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-03",
            description="Training",
            sales=5000,
            expenses=3000,
            currency="USD",
        ),
    ]

    daily_data = build_daily_calendar(records, year=2026)

    result = get_performance_between_dates(
        daily_data,
        date(2026, 10, 1),
        date(2026, 10, 3),
    )

    assert len(result) == 3
    assert result[date(2026, 10, 1)]["profit"] == 4000
    assert result[date(2026, 10, 2)]["profit"] == 0
    assert result[date(2026, 10, 3)]["profit"] == 2000


def test_summarize_monthly_performance():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting",
            sales=10000,
            expenses=6000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-15",
            description="Training",
            sales=5000,
            expenses=3000,
            currency="USD",
        ),
    ]

    daily_data = build_daily_calendar(records, year=2026)

    monthly_data = summarize_monthly_performance(
        daily_data,
        year=2026,
    )

    october = monthly_data["2026-10"]

    assert october["sales"] == 15000
    assert october["expenses"] == 9000
    assert october["profit"] == 6000
    assert october["transaction_count"] == 2
    assert october["active_days"] == 2
    assert october["profit_margin"] == 40


def test_filter_records_by_date_range():
    records = [
        BusinessRecord(
            date="2026-10-01",
            description="Consulting",
            sales=10000,
            expenses=6000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-05",
            description="Training",
            sales=5000,
            expenses=3000,
            currency="USD",
        ),
        BusinessRecord(
            date="2026-10-10",
            description="Support",
            sales=4000,
            expenses=2000,
            currency="USD",
        ),
    ]

    filtered = filter_records_by_date_range(
        records,
        date(2026, 10, 1),
        date(2026, 10, 5),
    )

    assert len(filtered) == 2
    assert filtered[0].description == "Consulting"
    assert filtered[1].description == "Training"
