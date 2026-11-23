
from datetime import datetime, timedelta, timezone
from time import monotonic

import requests

from trading212 import Trading212Client
from agent import summarize_portfolio


PERIODS = {
    "1": ("1 month", 30),
    "2": ("3 months", 90),
    "3": ("6 months", 180),
    "4": ("12 months", 365),
    "5": ("All time", None),
}

# Trading 212 account summary limit: 1 request / 5 seconds.
MIN_REFRESH_INTERVAL = 5


def select_period():
    print("\n=== SELECT TIME PERIOD ===")

    for key, (label, _) in PERIODS.items():
        if key == "5":
            print(f"{key}. {label}")
        else:
            print(f"{key}. Last {label}")

    choice = input("\nChoose [default 2]: ").strip() or "2"

    if choice not in PERIODS:
        print("Invalid selection. Using 3 months.")
        choice = "2"

    return choice


def build_instrument_lookup(instruments):
    return {
        instrument["ticker"]: instrument["name"]
        for instrument in instruments
        if instrument.get("ticker")
        and instrument.get("name")
    }


def fetch_portfolio(client, previous=None, full=False):
    """Fetch fresh data without discarding the previous snapshot."""

    print("\nRefreshing Trading 212 data...")

    account = client.get_account()
    positions = client.get_positions()

    if full or previous is None:
        print("Loading transaction history...")
        transactions = client.get_transactions()

        print("Loading instrument metadata...")
        instruments = client.get_instruments()
        names = build_instrument_lookup(instruments)
    else:
        transactions = previous["transactions"]
        names = previous["names"]

    snapshot = {
        "account": account,
        "positions": positions,
        "transactions": transactions,
        "names": names,
        "updated": datetime.now(timezone.utc),
    }

    print("Refresh successful.")
    return snapshot


def display_portfolio(client, snapshot, period_choice):
    label, days = PERIODS[period_choice]

    if days is None:
        transactions = snapshot["transactions"]
    else:
        start_date = (
            datetime.now(timezone.utc) - timedelta(days=days)
        )
        transactions = client.filter_transactions(
            snapshot["transactions"],
            start_date
        )

    print(f"\nSelected period: {label}")
    print(
        "Last updated: "
        + snapshot["updated"].astimezone().strftime(
            "%d %b %Y, %H:%M:%S"
        )
    )

    summarize_portfolio(
        snapshot["account"],
        snapshot["positions"],
        transactions,
        snapshot["names"]
    )


def main():
    client = Trading212Client()

    try:
        snapshot = fetch_portfolio(client, full=True)
        last_refresh = monotonic()
        period_choice = "2"

        while True:
            display_portfolio(client, snapshot, period_choice)

            print("\n=== PORTFOLIO MENU ===")
            print("1. Change time period")
            print("2. Refresh portfolio data")
            print("3. Exit")

            choice = input("\nChoose: ").strip()

            if choice == "1":
                period_choice = select_period()

            elif choice == "2":
                elapsed = monotonic() - last_refresh

                if elapsed < MIN_REFRESH_INTERVAL:
                    remaining = MIN_REFRESH_INTERVAL - elapsed
                    print(
                        f"Please wait {remaining:.1f} seconds "
                        "before refreshing."
                    )
                    continue

                try:
                    snapshot = fetch_portfolio(
                        client,
                        previous=snapshot
                    )
                    last_refresh = monotonic()

                except requests.RequestException as error:
                    print(f"Refresh failed: {error}")
                    print("Keeping previous portfolio data.")
                    last_refresh = monotonic()

            elif choice == "3":
                print("\nGoodbye!")
                break

            else:
                print("Invalid choice. Please try again.")

    finally:
        client.close()


if __name__ == "__main__":
    main()
