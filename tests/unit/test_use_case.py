"""Unit tests for processing sequences of transactions with the functional API."""

from decimal import Decimal

from hedix_wallet.wallet import Transaction, make_wallet


class TestProcessTransactions:
    def test_empty_transaction_list_returns_zero_balances(self) -> None:
        _, _, _, process = make_wallet()
        result = process([])
        assert result["BTC"] == Decimal("0")
        assert result["ETH"] == Decimal("0")
        assert result["USD"] == Decimal("0")

    def test_single_deposit_updates_balance(self) -> None:
        _, _, _, process = make_wallet()
        transactions: list[Transaction] = [
            {"type": "DEPOSIT", "asset": "BTC", "amount": Decimal("1.5")}
        ]
        result = process(transactions)
        assert result["BTC"] == Decimal("1.5")
        assert result["ETH"] == Decimal("0")
        assert result["USD"] == Decimal("0")

    def test_multiple_deposits_accumulate(self) -> None:
        _, _, _, process = make_wallet()
        transactions: list[Transaction] = [
            {"type": "DEPOSIT", "asset": "BTC", "amount": Decimal("1.0")},
            {"type": "DEPOSIT", "asset": "BTC", "amount": Decimal("0.5")},
            {"type": "DEPOSIT", "asset": "ETH", "amount": Decimal("2.0")},
        ]
        result = process(transactions)
        assert result["BTC"] == Decimal("1.5")
        assert result["ETH"] == Decimal("2.0")

    def test_successful_withdraw_after_deposit(self) -> None:
        _, _, _, process = make_wallet()
        transactions: list[Transaction] = [
            {"type": "DEPOSIT", "asset": "USD", "amount": Decimal("1000")},
            {"type": "WITHDRAW", "asset": "USD", "amount": Decimal("300")},
        ]
        result = process(transactions)
        assert result["USD"] == Decimal("700")

    def test_failed_withdraw_leaves_balance_unchanged(self) -> None:
        _, _, _, process = make_wallet()
        transactions: list[Transaction] = [
            {"type": "DEPOSIT", "asset": "BTC", "amount": Decimal("1.0")},
            {"type": "WITHDRAW", "asset": "BTC", "amount": Decimal("2.0")},
        ]
        result = process(transactions)
        assert result["BTC"] == Decimal("1.0")

    def test_transactions_processed_in_order(self) -> None:
        _, _, _, process = make_wallet()
        transactions: list[Transaction] = [
            {"type": "DEPOSIT", "asset": "BTC", "amount": Decimal("2.0")},
            {"type": "WITHDRAW", "asset": "BTC", "amount": Decimal("1.0")},
            {"type": "WITHDRAW", "asset": "BTC", "amount": Decimal("0.5")},
        ]
        result = process(transactions)
        assert result["BTC"] == Decimal("0.5")
