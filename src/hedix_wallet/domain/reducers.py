"""Pure reducers for wallet balances."""

from __future__ import annotations

from collections.abc import Iterable

from hedix_wallet.domain.types import Balances, Transaction


def _clone(balances: Balances) -> Balances:
    return {
        "BTC": balances["BTC"],
        "ETH": balances["ETH"],
        "USD": balances["USD"],
    }


def compute_next_balances(balances: Balances, transaction: Transaction) -> Balances:
    """Return a new balances dict after applying a single transaction (pure)."""
    next_balances = _clone(balances)

    ttype = transaction["type"]
    asset = transaction["asset"]
    amount = transaction["amount"]

    if ttype == "DEPOSIT":
        next_balances[asset] = next_balances[asset] + amount
        return next_balances

    if ttype == "WITHDRAW":
        if next_balances[asset] >= amount:
            next_balances[asset] = next_balances[asset] - amount
        return next_balances

    raise ValueError(f"Unknown transaction type: {ttype}")


def compute_balances(initial_balances: Balances, transactions: Iterable[Transaction]) -> Balances:
    """Return balances after applying all transactions in order (pure)."""
    state = initial_balances
    for tx in transactions:
        state = compute_next_balances(state, tx)
    return state
