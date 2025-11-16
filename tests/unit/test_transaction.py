"""Unit tests for operations using the functional wallet API."""

from decimal import Decimal

from hedix_wallet.wallet import make_wallet


class TestOperations:
    def test_multiple_deposits_accumulate(self) -> None:
        deposit, _, snapshot, _ = make_wallet()
        deposit("BTC", Decimal("1.0"))
        deposit("BTC", Decimal("0.5"))
        deposit("ETH", Decimal("2.0"))
        balances = snapshot()
        assert balances["BTC"] == Decimal("1.5")
        assert balances["ETH"] == Decimal("2.0")

    def test_successful_withdraw_after_deposit(self) -> None:
        deposit, withdraw, snapshot, _ = make_wallet()
        deposit("USD", Decimal("1000"))
        ok = withdraw("USD", Decimal("300"))
        assert ok is True
        assert snapshot()["USD"] == Decimal("700")

    def test_failed_withdraw_leaves_balance_unchanged(self) -> None:
        deposit, withdraw, snapshot, _ = make_wallet()
        deposit("BTC", Decimal("1.0"))
        ok = withdraw("BTC", Decimal("2.0"))
        assert ok is False
        assert snapshot()["BTC"] == Decimal("1.0")

    def test_withdraw_execute_with_exact_balance_succeeds(self) -> None:
        deposit, withdraw, snapshot, _ = make_wallet()
        deposit("ETH", Decimal("5.0"))
        ok = withdraw("ETH", Decimal("5.0"))
        assert ok is True
        assert snapshot()["ETH"] == Decimal("0")

    def test_withdraw_does_not_affect_other_assets(self) -> None:
        deposit, withdraw, snapshot, _ = make_wallet()
        deposit("BTC", Decimal("2.0"))
        deposit("ETH", Decimal("3.0"))
        deposit("USD", Decimal("100.0"))
        withdraw("BTC", Decimal("1.0"))
        balances = snapshot()
        assert balances["BTC"] == Decimal("1.0")
        assert balances["ETH"] == Decimal("3.0")
        assert balances["USD"] == Decimal("100.0")
