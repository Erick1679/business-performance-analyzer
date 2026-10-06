import csv
import pycountry
from dataclasses import dataclass

from src.calendar import (
    analyze_daily_performance,
    build_daily_calendar,
    get_active_daily_performance,
    summarize_monthly_performance,
)


class InvalidBusinessDataError(ValueError):
    """Raised when business data is invalid."""


@dataclass
class BusinessRecord:
    """Represent a single business performance record."""

    date: str
    description: str
    sales: float
    expenses: float
    currency: str

    @property
    def profit(self):
        """Calculate profit."""
        return self.sales - self.expenses

    @property
    def profit_margin(self):
        """Calculate profit margin as a percentage."""
        if self.sales == 0:
            return 0

        return (self.profit / self.sales) * 100


def calculate_profit(sales, expenses):
    """Calculate profit from sales and expenses."""
    return sales - expenses


def calculate_profit_margin(sales, profit):
    """Calculate profit margin as a percentage."""
    if sales == 0:
        return 0

    return (profit / sales) * 100


def get_currency_name(currency_code):
    """Return the currency name for an ISO 4217 currency code."""
    currency = pycountry.currencies.get(
        alpha_3=currency_code.upper()
    )

    if currency is None:
        return None

    return currency.name


def summarize_records(records):
    """Calculate overall business performance from multiple records."""
    total_sales = sum(record.sales for record in records)
    total_expenses = sum(record.expenses for record in records)
    total_profit = total_sales - total_expenses

    if total_sales == 0:
        profit_margin = 0
    else:
        profit_margin = (total_profit / total_sales) * 100

    return {
        "total_sales": total_sales,
        "total_expenses": total_expenses,
        "total_profit": total_profit,
        "profit_margin": profit_margin,
    }


def calculate_average_transaction(records):
    """Calculate average sales, expenses, and profit per transaction."""
    if not records:
        return {
            "average_sales": 0,
            "average_expenses": 0,
            "average_profit": 0,
        }

    transaction_count = len(records)

    total_sales = sum(record.sales for record in records)
    total_expenses = sum(record.expenses for record in records)
    total_profit = sum(record.profit for record in records)

    return {
        "average_sales": total_sales / transaction_count,
        "average_expenses": total_expenses / transaction_count,
        "average_profit": total_profit / transaction_count,
    }


def get_top_transaction_by_profit(records):
    """Return the transaction with the highest profit."""
    if not records:
        return None

    return max(records, key=lambda record: record.profit)


def get_lowest_transaction_by_profit(records):
    """Return the transaction with the lowest profit."""
    if not records:
        return None

    return min(records, key=lambda record: record.profit)


def rank_transactions_by_profit(records):
    """Return transactions ranked from highest to lowest profit."""
    return sorted(
        records,
        key=lambda record: record.profit,
        reverse=True,
    )


def load_records_from_csv(file_path):
    """Load and validate business records from a CSV file."""
    records = []

    required_columns = {
        "date",
        "description",
        "sales",
        "expenses",
        "currency",
    }

    with open(
        file_path,
        mode="r",
        newline="",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise InvalidBusinessDataError(
                "CSV file does not contain a header row."
            )

        missing_columns = required_columns - set(reader.fieldnames)

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise InvalidBusinessDataError(
                f"CSV file is missing required columns: {missing}"
            )

        for row_number, row in enumerate(reader, start=2):
            date = row["date"].strip()
            description = row["description"].strip()

            if not date:
                raise InvalidBusinessDataError(
                    f"Missing date on row {row_number}."
                )

            if not description:
                raise InvalidBusinessDataError(
                    f"Missing description on row {row_number}."
                )

            try:
                sales = float(row["sales"])
                expenses = float(row["expenses"])
            except (TypeError, ValueError):
                raise InvalidBusinessDataError(
                    f"Invalid sales or expenses value on row {row_number}."
                )

            currency = row["currency"].strip().upper()

            if not currency:
                raise InvalidBusinessDataError(
                    f"Missing currency on row {row_number}."
                )

            if get_currency_name(currency) is None:
                raise InvalidBusinessDataError(
                    f"Unsupported currency '{currency}' on row {row_number}."
                )

            record = BusinessRecord(
                date=date,
                description=description,
                sales=sales,
                expenses=expenses,
                currency=currency,
            )

            records.append(record)

    return records


def summarize_by_currency(records):
    """Summarize business performance separately for each currency."""
    summaries = {}

    currencies = {record.currency for record in records}

    for currency in currencies:
        currency_records = [
            record
            for record in records
            if record.currency == currency
        ]

        summaries[currency] = summarize_records(currency_records)

    return summaries


def display_monthly_performance(records):
    """Display calendar-based monthly performance separately by currency."""
    currencies = sorted({record.currency for record in records})

    print("\nMonthly Calendar Performance")
    print("============================")

    for currency in currencies:
        currency_records = [
            record
            for record in records
            if record.currency == currency
        ]

        daily_data = build_daily_calendar(currency_records)

        monthly_data = summarize_monthly_performance(
            daily_data,
            year=None,
        )

        currency_name = get_currency_name(currency)

        print(f"\nCurrency: {currency} - {currency_name}")

        print(
            "\nMonth      Transactions   Active Days"
            "       Sales       Expenses       Profit       Margin"
        )

        print("-" * 90)

        for month, month_data in sorted(monthly_data.items()):
            print(
                f"{month} "
                f"{month_data['transaction_count']:>12} "
                f"{month_data['active_days']:>13} "
                f"{currency} {month_data['sales']:>10,.2f} "
                f"{currency} {month_data['expenses']:>10,.2f} "
                f"{currency} {month_data['profit']:>10,.2f} "
                f"{month_data['profit_margin']:>9.2f}%"
            )


def display_daily_performance(records):
    """Display calendar-based daily performance separately by currency."""
    currencies = sorted({record.currency for record in records})

    print("\nDaily Calendar Performance")
    print("==========================")

    for currency in currencies:
        currency_records = [
            record
            for record in records
            if record.currency == currency
        ]

        daily_data = build_daily_calendar(currency_records)
        analysis = analyze_daily_performance(daily_data)

        active_daily_performance = get_active_daily_performance(
            daily_data
        )

        currency_name = get_currency_name(currency)

        print(f"\nCurrency: {currency} - {currency_name}")
        print(f"Active Days: {analysis['active_days']}")
        print(f"Inactive Days: {analysis['inactive_days']}")

        highest_profit_day = analysis["highest_profit_day"]
        lowest_profit_day = analysis["lowest_profit_day"]

        if highest_profit_day is not None:
            highest_date, highest_data = highest_profit_day

            print(
                f"Highest Profit Day: "
                f"{highest_date} - "
                f"{currency} {highest_data['profit']:,.2f}"
            )

        if lowest_profit_day is not None:
            lowest_date, lowest_data = lowest_profit_day

            print(
                f"Lowest Profit Day: "
                f"{lowest_date} - "
                f"{currency} {lowest_data['profit']:,.2f}"
            )

        print("\nDaily Performance:")

        print(
            "Date       Transactions       Sales"
            "       Expenses       Profit       Margin"
        )

        print("-" * 78)

        for day in active_daily_performance:
            print(
                f"{day['date']} "
                f"{day['transaction_count']:>12} "
                f"{currency} {day['sales']:>10,.2f} "
                f"{currency} {day['expenses']:>10,.2f} "
                f"{currency} {day['profit']:>10,.2f} "
                f"{day['profit_margin']:>9.2f}%"
            )


def display_csv_report(file_path):
    """Display a business performance report from a CSV file."""
    records = load_records_from_csv(file_path)
    summaries = summarize_by_currency(records)

    print("\nBusiness Performance Report")
    print("===========================")

    for currency in sorted(summaries):
        currency_name = get_currency_name(currency)
        summary = summaries[currency]

        currency_records = [
            record
            for record in records
            if record.currency == currency
        ]

        averages = calculate_average_transaction(
            currency_records
        )

        top_transaction = get_top_transaction_by_profit(
            currency_records
        )

        lowest_transaction = get_lowest_transaction_by_profit(
            currency_records
        )

        ranked_transactions = rank_transactions_by_profit(
            currency_records
        )

        print(f"\nCurrency: {currency} - {currency_name}")
        print(
            f"Sales: "
            f"{currency} {summary['total_sales']:,.2f}"
        )
        print(
            f"Expenses: "
            f"{currency} {summary['total_expenses']:,.2f}"
        )
        print(
            f"Profit: "
            f"{currency} {summary['total_profit']:,.2f}"
        )
        print(
            f"Profit Margin: "
            f"{summary['profit_margin']:.2f}%"
        )

        print(
            f"Average Sales: "
            f"{currency} {averages['average_sales']:,.2f}"
        )
        print(
            f"Average Expenses: "
            f"{currency} {averages['average_expenses']:,.2f}"
        )
        print(
            f"Average Profit: "
            f"{currency} {averages['average_profit']:,.2f}"
        )

        print(
            f"Top Transaction: "
            f"{top_transaction.description}"
        )
        print(
            f"Top Transaction Profit: "
            f"{currency} {top_transaction.profit:,.2f}"
        )
        print(
            f"Top Transaction Margin: "
            f"{top_transaction.profit_margin:.2f}%"
        )

        print(
            f"Lowest Transaction: "
            f"{lowest_transaction.description}"
        )
        print(
            f"Lowest Transaction Profit: "
            f"{currency} {lowest_transaction.profit:,.2f}"
        )
        print(
            f"Lowest Transaction Margin: "
            f"{lowest_transaction.profit_margin:.2f}%"
        )

        print("\nTransaction Ranking:")

        for rank, transaction in enumerate(
            ranked_transactions,
            start=1,
        ):
            print(
                f"{rank}. {transaction.description} - "
                f"{currency} {transaction.profit:,.2f} profit "
                f"({transaction.profit_margin:.2f}% margin)"
            )

    display_monthly_performance(records)
    display_daily_performance(records)


def main():
    """Run the business performance analyzer."""
    file_path = "data/raw/business_data.csv"

    try:
        display_csv_report(file_path)

    except FileNotFoundError:
        print(f"Error: CSV file not found: {file_path}")
        raise SystemExit(1)

    except InvalidBusinessDataError as error:
        print(f"Error: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
