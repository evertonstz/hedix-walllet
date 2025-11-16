"""Integration tests for edge cases and complex scenarios."""

from decimal import Decimal

from hedix_wallet.wallet import Transaction, make_wallet


class TestEdgeCases:
    """Integration tests for edge cases."""

    def test_multiple_failed_withdrawals_dont_affect_balance(self) -> None:
        _, _, _, process = make_wallet()
        transactions: list[Transaction] = [
            {"type": "DEPOSIT", "asset": "BTC", "amount": Decimal("1.0")},
            {"type": "WITHDRAW", "asset": "BTC", "amount": Decimal("2.0")},  # Fail
            {"type": "WITHDRAW", "asset": "BTC", "amount": Decimal("1.5")},  # Fail
            {"type": "WITHDRAW", "asset": "BTC", "amount": Decimal("1.1")},  # Fail
            {"type": "WITHDRAW", "asset": "BTC", "amount": Decimal("0.5")},  # Success
        ]
        result = process(transactions)
        assert result["BTC"] == Decimal("0.5")

    def test_withdraw_exact_balance_leaves_zero(self) -> None:
        _, _, _, process = make_wallet()
        transactions: list[Transaction] = [
            {"type": "DEPOSIT", "asset": "ETH", "amount": Decimal("10.0")},
            {"type": "WITHDRAW", "asset": "ETH", "amount": Decimal("10.0")},
        ]
        result = process(transactions)
        assert result["ETH"] == Decimal("0")

    def test_precision_with_small_amounts(self) -> None:
        _, _, _, process = make_wallet()
        transactions: list[Transaction] = [
            {"type": "DEPOSIT", "asset": "BTC", "amount": Decimal("0.00000001")},
            {"type": "DEPOSIT", "asset": "BTC", "amount": Decimal("0.00000001")},
            {"type": "WITHDRAW", "asset": "BTC", "amount": Decimal("0.00000001")},
        ]
        result = process(transactions)
        assert result["BTC"] == Decimal("0.00000001")

    def test_large_number_of_transactions(self) -> None:
        _, _, _, process = make_wallet()
        transactions: list[Transaction] = [
            {"type": "DEPOSIT", "asset": "USD", "amount": Decimal("1")} for _ in range(1000)
        ]
        result = process(transactions)
        assert result["USD"] == Decimal("1000")

    def test_interleaved_operations_on_multiple_assets(self) -> None:
        _, _, _, process = make_wallet()
        transactions: list[Transaction] = [
            {"type": "DEPOSIT", "asset": "BTC", "amount": Decimal("10")},
            {"type": "DEPOSIT", "asset": "ETH", "amount": Decimal("20")},
            {"type": "DEPOSIT", "asset": "USD", "amount": Decimal("1000")},
            {"type": "WITHDRAW", "asset": "BTC", "amount": Decimal("3")},
            {"type": "WITHDRAW", "asset": "ETH", "amount": Decimal("5")},
            {"type": "WITHDRAW", "asset": "USD", "amount": Decimal("200")},
            {"type": "DEPOSIT", "asset": "BTC", "amount": Decimal("1")},
            {"type": "WITHDRAW", "asset": "ETH", "amount": Decimal("20")},  # Fail - only 15 left
            {"type": "WITHDRAW", "asset": "BTC", "amount": Decimal("8")},
        ]
        result = process(transactions)
        assert result["BTC"] == Decimal("0")  # 10 + 1 - 3 - 8
        assert result["ETH"] == Decimal("15")  # 20 - 5 (failed withdrawal ignored)
        assert result["USD"] == Decimal("800")  # 1000 - 200

    def test_alternating_deposits_and_withdrawals(self) -> None:
        _, _, _, process = make_wallet()
        transactions: list[Transaction] = [
            {"type": "DEPOSIT", "asset": "USD", "amount": Decimal("100")},
            {"type": "WITHDRAW", "asset": "USD", "amount": Decimal("50")},
            {"type": "DEPOSIT", "asset": "USD", "amount": Decimal("100")},
            {"type": "WITHDRAW", "asset": "USD", "amount": Decimal("50")},
            {"type": "DEPOSIT", "asset": "USD", "amount": Decimal("100")},
            {"type": "WITHDRAW", "asset": "USD", "amount": Decimal("50")},
        ]
        result = process(transactions)
        assert result["USD"] == Decimal("150")
