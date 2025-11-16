"""Unit tests for pure reducers: compute_next_balances and compute_balances."""

from __future__ import annotations

from decimal import Decimal
from typing import cast

from hedix_wallet.domain.reducers import compute_balances, compute_next_balances
from hedix_wallet.domain.types import Asset, Balances, PositiveDecimal, Transaction


class TestReducers:
    def test_compute_next_balances_deposit_is_pure_and_correct(self) -> None:
        initial: Balances = {"BTC": Decimal("0"), "ETH": Decimal("0"), "USD": Decimal("0")}
        tx: Transaction = {
            "type": "DEPOSIT",
            "asset": cast(Asset, "BTC"),
            "amount": cast(PositiveDecimal, Decimal("1.5")),
        }

        result = compute_next_balances(initial, tx)

        # Original not mutated
        assert initial["BTC"] == Decimal("0")
        # Result updated
        assert result["BTC"] == Decimal("1.5")
        # Other assets unchanged
        assert result["ETH"] == Decimal("0")
        assert result["USD"] == Decimal("0")

    def test_compute_next_balances_withdraw_success_is_pure_and_correct(self) -> None:
        initial: Balances = {"BTC": Decimal("2.0"), "ETH": Decimal("0"), "USD": Decimal("0")}
        tx: Transaction = {
            "type": "WITHDRAW",
            "asset": cast(Asset, "BTC"),
            "amount": cast(PositiveDecimal, Decimal("0.5")),
        }

        result = compute_next_balances(initial, tx)

        # Original not mutated
        assert initial["BTC"] == Decimal("2.0")
        # Result updated
        assert result["BTC"] == Decimal("1.5")

    def test_compute_next_balances_withdraw_insufficient_keeps_balances(self) -> None:
        initial: Balances = {"BTC": Decimal("0.4"), "ETH": Decimal("0"), "USD": Decimal("0")}
        tx: Transaction = {
            "type": "WITHDRAW",
            "asset": cast(Asset, "BTC"),
            "amount": cast(PositiveDecimal, Decimal("0.5")),
        }

        result = compute_next_balances(initial, tx)

        # No change due to insufficient funds
        assert result["BTC"] == Decimal("0.4")
        # Still pure (original unchanged)
        assert initial["BTC"] == Decimal("0.4")

    def test_compute_balances_folds_sequence(self) -> None:
        initial: Balances = {"BTC": Decimal("0"), "ETH": Decimal("0"), "USD": Decimal("0")}
        txs: list[Transaction] = [
            {
                "type": "DEPOSIT",
                "asset": cast(Asset, "BTC"),
                "amount": cast(PositiveDecimal, Decimal("1.5")),
            },
            {
                "type": "DEPOSIT",
                "asset": cast(Asset, "USD"),
                "amount": cast(PositiveDecimal, Decimal("1000")),
            },
            {
                "type": "WITHDRAW",
                "asset": cast(Asset, "USD"),
                "amount": cast(PositiveDecimal, Decimal("300")),
            },
            {
                "type": "WITHDRAW",
                "asset": cast(Asset, "BTC"),
                "amount": cast(PositiveDecimal, Decimal("2.0")),
            },  # ignored
            {
                "type": "DEPOSIT",
                "asset": cast(Asset, "ETH"),
                "amount": cast(PositiveDecimal, Decimal("5.0")),
            },
            {
                "type": "WITHDRAW",
                "asset": cast(Asset, "BTC"),
                "amount": cast(PositiveDecimal, Decimal("0.5")),
            },
        ]

        result = compute_balances(initial, txs)

        assert result["BTC"] == Decimal("1.0")
        assert result["ETH"] == Decimal("5.0")
        assert result["USD"] == Decimal("700")
