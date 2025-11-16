"""Main entry point for the wallet application."""

from decimal import Decimal

from hedix_wallet.wallet import (
    Transaction,
    format_balances,
    make_wallet,
)

DELIMITER = "-" * 60


def get_example_transactions() -> list[Transaction]:
    """Get the example transactions from the problm pdf, simulates a json."""
    return [
        {"type": "DEPOSIT", "asset": "BTC", "amount": Decimal("1.5")},
        {"type": "DEPOSIT", "asset": "USD", "amount": Decimal("1000")},
        {"type": "WITHDRAW", "asset": "USD", "amount": Decimal("300")},
        {"type": "WITHDRAW", "asset": "BTC", "amount": Decimal("2.0")},  # Should fail
        {"type": "DEPOSIT", "asset": "ETH", "amount": Decimal("5.0")},
        {"type": "WITHDRAW", "asset": "BTC", "amount": Decimal("0.5")},
    ]


def main() -> None:
    """Run the wallet application with the example transactions in pdf."""
    print("=" * 60)
    print("Hedix Crypto Wallet")
    print("=" * 60)
    print()

    # Initialize wallet
    deposit, withdraw, snapshot, _ = make_wallet()

    # Get transactions (in a real app, these could come from CLI args, file, API, etc.)
    transactions = get_example_transactions()

    print("Initial State: BTC: 0, ETH: 0, USD: 0")
    print()
    print("Processing transactions:")
    print(DELIMITER)

    # Process transactions and display each step
    for i, tx in enumerate(transactions, 1):
        match tx["type"]:
            case "DEPOSIT":
                deposit(tx["asset"], tx["amount"])
                status = "DONE"
            case "WITHDRAW":
                ok = withdraw(tx["asset"], tx["amount"])
                status = "DONE" if ok else "FAILED (insufficient funds)"
            case _:
                # this is defensive, should never happen
                status = "FAILED (invalid type)"

        balances = snapshot()
        print(
            f"{i}. {tx['type']} {tx['asset']} {tx['amount']}: "
            f"{format_balances(balances)} {status}"
        )

    print(DELIMITER)
    print()

    final_balances = snapshot()
    print(f"Expected Output: {format_balances(final_balances)}")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
