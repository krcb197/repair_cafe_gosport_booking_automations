"""
script to generate all the dates for the Repair Cafe Gosport Events, within a date range
"""
import argparse
import datetime

from py_rcg_booking_automation import event_dates

def parse_date(value: str) -> datetime.date:
    """
    Parse a command line date in DD-MM-YYYY format.
    """
    try:
        return datetime.date.strptime(value, "%d-%m-%Y")
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date '{value}'. Use DD-MM-YYYY."
        ) from exc

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Repair Cafe Gosport event dates within a date range."
    )
    parser.add_argument(
        "--start-date",
        required=True,
        type=parse_date,
        help="Start date in DD-MM-YYYY format.",
    )
    parser.add_argument(
        "--end-date",
        required=True,
        type=parse_date,
        help="End date in DD-MM-YYYY format.",
    )

    args = parser.parse_args()
    if args.end_date < args.start_date:
        parser.error("--end-date must be on or after --start-date")

    return args


if __name__ == '__main__':
    cli_args = parse_args()
    for event_date in event_dates(
        start_date=cli_args.start_date,
        end_date=cli_args.end_date,
    ):
        print(f'{event_date:%d/%m/%Y}')
