"""Unit tests for the functional wallet closure."""

from decimal import Decimal

import pytest

from hedix_wallet.wallet import format_balances, make_wallet


class TestFunctionalWallet:
    def test_wallet_initializes_with_zero_balances(self) -> None:
        _, _, snapshot, _ = make_wallet()
        balances = snapshot()
        assert balances["BTC"] == Decimal("0")
        assert balances["ETH"] == Decimal("0")
        assert balances["USD"] == Decimal("0")

    def test_deposit_updates_balance(self) -> None:
        deposit, _, snapshot, _ = make_wallet()
        deposit("BTC", Decimal("5.5"))
        assert snapshot()["BTC"] == Decimal("5.5")

    def test_withdraw_updates_balance_when_sufficient(self) -> None:
        deposit, withdraw, snapshot, _ = make_wallet()
        deposit("ETH", Decimal("10.0"))
        ok = withdraw("ETH", Decimal("3.0"))
        assert ok is True
        assert snapshot()["ETH"] == Decimal("7.0")

    def test_withdraw_fails_when_insufficient(self) -> None:
        _, withdraw, snapshot, _ = make_wallet()
        ok = withdraw("USD", Decimal("1.0"))
        assert ok is False
        assert snapshot()["USD"] == Decimal("0")

    def test_deposit_negative_amount_raises(self) -> None:
        deposit, _, _, _ = make_wallet()
        with pytest.raises(ValueError, match="positive"):
            deposit("BTC", Decimal("-1"))

    def test_withdraw_negative_amount_raises(self) -> None:
        _, withdraw, _, _ = make_wallet()
        with pytest.raises(ValueError, match="positive"):
            withdraw("BTC", Decimal("-1"))

    def test_snapshot_returns_copy(self) -> None:
        deposit, _, snapshot, _ = make_wallet()
        deposit("BTC", Decimal("1.0"))
        balances = snapshot()
        balances["BTC"] = Decimal("999.0")
        # Original state unchanged
        assert snapshot()["BTC"] == Decimal("1.0")

    def test_format_balances(self) -> None:
        deposit, _, snapshot, _ = make_wallet()
        deposit("BTC", Decimal("1.5"))
        deposit("USD", Decimal("700"))
        deposit("ETH", Decimal("5.0"))
        formatted = format_balances(snapshot())
        assert "BTC: 1.5" in formatted
        assert "ETH: 5.0" in formatted
        assert "USD: 700" in formatted
