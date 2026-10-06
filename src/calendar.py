from datetime import date, timedelta


def generate_calendar(year=None):
    """Generate every date for a calendar year."""
    if year is None:
        year = date.today().year

    start_date = date(year, 1, 1)
    end_date = date(year + 1, 1, 1)

    calendar_dates = []
    current_date = start_date

    while current_date < end_date:
        calendar_dates.append(current_date)
        current_date += timedelta(days=1)

    return calendar_dates


def build_daily_calendar(records, year=None):
    """Combine the full calendar with business transaction data."""
    calendar_dates = generate_calendar(year)

    target_year = year or date.today().year

    daily_data = {
        current_date: {
            "sales": 0,
            "expenses": 0,
            "profit": 0,
            "transaction_count": 0,
        }
        for current_date in calendar_dates
    }

    for record in records:
        record_date = date.fromisoformat(record.date)

        if record_date.year != target_year:
            continue

        daily_data[record_date]["sales"] += record.sales
        daily_data[record_date]["expenses"] += record.expenses
        daily_data[record_date]["profit"] += record.profit
        daily_data[record_date]["transaction_count"] += 1

    return daily_data


def calculate_daily_profit_margin(day_data):
    """Calculate profit margin for a single day."""
    if day_data["sales"] == 0:
        return 0

    return (day_data["profit"] / day_data["sales"]) * 100


def get_active_daily_performance(daily_data):
    """Return active business days with calculated profit margins."""
    active_days = []

    for current_date, day_data in daily_data.items():
        if day_data["transaction_count"] == 0:
            continue

        daily_performance = {
            "date": current_date,
            "transaction_count": day_data["transaction_count"],
            "sales": day_data["sales"],
            "expenses": day_data["expenses"],
            "profit": day_data["profit"],
            "profit_margin": calculate_daily_profit_margin(
                day_data
            ),
        }

        active_days.append(daily_performance)

    return sorted(
        active_days,
        key=lambda day: day["date"],
    )


def analyze_daily_performance(daily_data):
    """Analyze business performance across the calendar year."""
    total_sales = sum(
        day["sales"]
        for day in daily_data.values()
    )

    total_expenses = sum(
        day["expenses"]
        for day in daily_data.values()
    )

    total_profit = sum(
        day["profit"]
        for day in daily_data.values()
    )

    active_days = sum(
        1
        for day in daily_data.values()
        if day["transaction_count"] > 0
    )

    inactive_days = sum(
        1
        for day in daily_data.values()
        if day["transaction_count"] == 0
    )

    active_day_data = {
        current_date: day
        for current_date, day in daily_data.items()
        if day["transaction_count"] > 0
    }

    if active_day_data:
        highest_profit_day = max(
            active_day_data.items(),
            key=lambda item: item[1]["profit"],
        )

        lowest_profit_day = min(
            active_day_data.items(),
            key=lambda item: item[1]["profit"],
        )
    else:
        highest_profit_day = None
        lowest_profit_day = None

    return {
        "total_sales": total_sales,
        "total_expenses": total_expenses,
        "total_profit": total_profit,
        "active_days": active_days,
        "inactive_days": inactive_days,
        "highest_profit_day": highest_profit_day,
        "lowest_profit_day": lowest_profit_day,
    }
def get_daily_performance(daily_data, target_date):
    """Return performance data for a specific date."""
    return daily_data.get(target_date)
def get_performance_between_dates(
    daily_data,
    start_date,
    end_date,
):
    """Return daily performance within an inclusive date range."""
    return {
        current_date: day_data
        for current_date, day_data in daily_data.items()
        if start_date <= current_date <= end_date
    }
def summarize_monthly_performance(daily_data, year=None):
    """Summarize business performance for each month."""
    monthly_data = {}

    for current_date, day_data in daily_data.items():
        if year is not None and current_date.year != year:
            continue

        month_key = current_date.strftime("%Y-%m")

        if month_key not in monthly_data:
            monthly_data[month_key] = {
                "sales": 0,
                "expenses": 0,
                "profit": 0,
                "transaction_count": 0,
                "active_days": 0,
            }

        monthly_data[month_key]["sales"] += day_data["sales"]
        monthly_data[month_key]["expenses"] += day_data["expenses"]
        monthly_data[month_key]["profit"] += day_data["profit"]
        monthly_data[month_key]["transaction_count"] += (
            day_data["transaction_count"]
        )

        if day_data["transaction_count"] > 0:
            monthly_data[month_key]["active_days"] += 1

    for month_data in monthly_data.values():
        sales = month_data["sales"]

        if sales == 0:
            month_data["profit_margin"] = 0
        else:
            month_data["profit_margin"] = (
                month_data["profit"] / sales
            ) * 100

    return monthly_data
