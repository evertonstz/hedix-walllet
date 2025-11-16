"""Core functional wallet implementation (stateful closure, pure domain)."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from decimal import Decimal
from typing import cast

from .reducers import compute_next_balances
from .types import Asset, Balances, PositiveDecimal, Transaction

# Function type aliases for the wallet API
DepositFunc = Callable[[Asset, Decimal], None]
WithdrawFunc = Callable[[Asset, Decimal], bool]
SnapshotFunc = Callable[[], Balances]


def make_wallet(
    initial_balances: Mapping[Asset, Decimal] | None = None,
) -> tuple[DepositFunc, WithdrawFunc, SnapshotFunc]:
    """Create a wallet using a clojure to encapsulate state.

    Args:
        initial_balances: Optional initial balances. Missing assets default to 0.

    Returns:
        (deposit, withdraw, snapshot)
    """
    balances: Balances = {
        "BTC": Decimal("0"),
        "ETH": Decimal("0"),
        "USD": Decimal("0"),
    }
    if initial_balances:
        for asset in ("BTC", "ETH", "USD"):
            if asset in initial_balances:
                amount = initial_balances[asset]
                if amount < 0:
                    raise ValueError(f"Balance cannot be negative: {asset}={amount}")
                balances[asset] = Decimal(amount)

    def deposit(asset: Asset, amount: Decimal) -> None:
        nonlocal balances
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        tx: Transaction = {
            "type": "DEPOSIT",
            "asset": asset,
            "amount": cast(PositiveDecimal, amount),
        }
        balances = compute_next_balances(balances, tx)

    def withdraw(asset: Asset, amount: Decimal) -> bool:
        nonlocal balances
        if amount <= 0:
            raise ValueError("Withdraw amount must be positive")
        tx: Transaction = {
            "type": "WITHDRAW",
            "asset": asset,
            "amount": cast(PositiveDecimal, amount),
        }
        next_balances = compute_next_balances(balances, tx)
        success = next_balances[asset] != balances[asset]
        balances = next_balances
        return success

    def snapshot() -> Balances:
        # Defensive copy
        return {
            "BTC": balances["BTC"],
            "ETH": balances["ETH"],
            "USD": balances["USD"],
        }

    return deposit, withdraw, snapshot
