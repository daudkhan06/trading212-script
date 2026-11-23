
from collections import Counter
from decimal import Decimal, InvalidOperation


def money(value):
    """Convert a monetary value to Decimal."""
    if value is None:
        return Decimal("0")

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"Invalid monetary value: {value}")


def calculate_cash_flows(transactions, currency):
    """Calculate deposits and withdrawals."""

    deposits = Decimal("0")
    withdrawals = Decimal("0")
    unknown_types = Counter()

    for transaction in transactions:
        kind = str(transaction.get("type", "")).upper()
        amount = money(transaction.get("amount"))
        transaction_currency = transaction.get("currency")

        if transaction_currency != currency:
            raise ValueError(
                f"Currency mismatch: expected {currency}, "
                f"received {transaction_currency}"
            )

        if kind == "DEPOSIT":
            deposits += abs(amount)

        elif kind in ("WITHDRAW", "WITHDRAWAL"):
            withdrawals += abs(amount)

        elif kind not in ("FEE", "TRANSFER"):
            unknown_types[kind or "MISSING"] += 1

    return {
        "deposits": deposits,
        "withdrawals": withdrawals,
        "net_deposits": deposits - withdrawals,
        "unknown_types": unknown_types,
    }


def summarize_portfolio(
    account,
    positions,
    transactions,
    instrument_names=None
):
    """Display portfolio, cash flows and holdings."""

    instrument_names = instrument_names or {}

    currency = account.get("currency", "GBP")
    total_value = money(account.get("totalValue"))

    cash_flows = calculate_cash_flows(
        transactions,
        currency
    )

    deposits = cash_flows["deposits"]
    withdrawals = cash_flows["withdrawals"]
    net_deposits = cash_flows["net_deposits"]

    print("\n" + "=" * 50)
    print("             TRADING 212 PORTFOLIO")
    print("=" * 50)

    print(f"\nAccount Currency:  {currency}")
    print(f"Current Value:     {total_value:,.2f} {currency}")
    print(f"Total Positions:   {len(positions)}")

    print("\n" + "-" * 50)
    print("             PERIOD CASH FLOWS")
    print("-" * 50)

    print(f"Deposited:         {deposits:,.2f} {currency}")
    print(f"Withdrawn:         {withdrawals:,.2f} {currency}")
    print(f"Net Deposits:      {net_deposits:,.2f} {currency}")

    if cash_flows["unknown_types"]:
        print("\nOther transaction types:")
        for kind, count in cash_flows["unknown_types"].items():
            print(f"  {kind}: {count}")

    print("\n" + "-" * 50)
    print("                PERFORMANCE")
    print("-" * 50)

    print(f"Current Value:     {total_value:,.2f} {currency}")
    print("Period P/L:       Requires historical valuations")
    print("Period Return:    Requires historical valuations")

    print("\n" + "-" * 50)
    print("                  HOLDINGS")
    print("-" * 50)

    if not positions:
        print("\nNo open positions.")

    else:
        for position in positions:
            instrument = position.get("instrument") or {}

            ticker = (
                instrument.get("ticker")
                or position.get("ticker")
                or "Unknown"
            )

            company_name = (
                instrument_names.get(ticker)
                or instrument.get("name")
                or position.get("name")
                or ticker
            )

            quantity = position.get("quantity", "N/A")

            print(f"\n{company_name} ({ticker})")
            print(f"  Quantity: {quantity} shares")

            current_price = position.get("currentPrice")
            average_price = position.get("averagePrice")

            if current_price is not None:
                print(f"  Current Price: {current_price}")

            if average_price is not None:
                print(f"  Average Price: {average_price}")

    print("\n" + "=" * 50)
    print("               END OF SUMMARY")
    print("=" * 50 + "\n")
