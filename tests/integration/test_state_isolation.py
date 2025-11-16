"""Integration tests to verify proper state isolation using the functional wallet."""

from decimal import Decimal

from hedix_wallet.wallet import make_wallet


class TestStateIsolation:
    def test_each_wallet_instance_has_isolated_state(self) -> None:
        _, _, snapshot1, process1 = make_wallet()
        _, _, snapshot2, process2 = make_wallet()

        process1([{"type": "DEPOSIT", "asset": "BTC", "amount": Decimal("10.0")}])
        process2([{"type": "DEPOSIT", "asset": "ETH", "amount": Decimal("5.0")}])

        assert snapshot1()["BTC"] == Decimal("10.0")
        assert snapshot1()["ETH"] == Decimal("0")

        assert snapshot2()["BTC"] == Decimal("0")
        assert snapshot2()["ETH"] == Decimal("5.0")

    def test_state_persists_within_same_wallet(self) -> None:
        _, _, snapshot, process = make_wallet()

        process([{"type": "DEPOSIT", "asset": "BTC", "amount": Decimal("5.0")}])
        assert snapshot()["BTC"] == Decimal("5.0")

        process([{"type": "DEPOSIT", "asset": "BTC", "amount": Decimal("3.0")}])
        assert snapshot()["BTC"] == Decimal("8.0")

    def test_each_test_method_starts_with_clean_state(self) -> None:
        _, _, snapshot, _ = make_wallet()
        # Should start with zero balance
        assert snapshot()["BTC"] == Decimal("0")
        assert snapshot()["ETH"] == Decimal("0")
        assert snapshot()["USD"] == Decimal("0")

    def test_another_test_also_has_clean_state(self) -> None:
        _, _, snapshot, process = make_wallet()
        process([{"type": "DEPOSIT", "asset": "USD", "amount": Decimal("100")}])
        balances = snapshot()
        assert balances["BTC"] == Decimal("0")
        assert balances["ETH"] == Decimal("0")
        assert balances["USD"] == Decimal("100")

    def test_snapshot_returns_copy(self) -> None:
        _, _, snapshot, process = make_wallet()
        process([{"type": "DEPOSIT", "asset": "BTC", "amount": Decimal("10.0")}])
        balances = snapshot()
        balances["BTC"] = Decimal("999.0")
        # Internal state unchanged
        assert snapshot()["BTC"] == Decimal("10.0")
