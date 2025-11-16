"""Application use-cases (functional orchestrators)."""

from __future__ import annotations

from collections.abc import Iterable

from hedix_wallet.application.ports import WalletPort
from hedix_wallet.domain.types import Balances, Transaction


def process_transactions(transactions: Iterable[Transaction], port: WalletPort) -> Balances:
    """Process a list of transactions against the provided wallet port."""
    for tx in transactions:
        tx_type = tx["type"]
        tx_asset = tx["asset"]
        tx_amount = tx["amount"]

        if tx_type == "DEPOSIT":
            port.deposit(tx_asset, tx_amount)
        elif tx_type == "WITHDRAW":
            port.withdraw(tx_asset, tx_amount)
        else:
            raise ValueError(f"Unknown transaction type: {tx_type}")

    return port.snapshot()
