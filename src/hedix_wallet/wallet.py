"""Wallet facade exposing a small functional API by composing hexagonal pieces."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from decimal import Decimal
from types import SimpleNamespace

from hedix_wallet.adapters.cli import format_balances, parse_transaction
from hedix_wallet.application.ports import WalletPort
from hedix_wallet.application.use_cases import process_transactions as _process_use_case
from hedix_wallet.domain.types import Asset, Balances, ProcessFunc, Transaction, TransactionType
from hedix_wallet.domain.wallet_core import (
    DepositFunc,
    SnapshotFunc,
    WithdrawFunc,
)
from hedix_wallet.domain.wallet_core import (
    make_wallet as _make_wallet_core,
)

__all__ = [
    # Facade API
    "make_wallet",
    # Re-exports to define the public API and avoid lint problemas
    "format_balances",
    "parse_transaction",
    "Asset",
    "Balances",
    "Transaction",
    "TransactionType",
    "ProcessFunc",
]


def make_wallet(
    initial_balances: Mapping[Asset, Decimal] | None = None,
) -> tuple[DepositFunc, WithdrawFunc, SnapshotFunc, ProcessFunc]:
    """Create a wallet and expose both interactive and batch APIs.

    This is a small facade over the domain core:
    - Interactive (step-by-step): use the returned `deposit`, `withdraw`, and `snapshot`
      functions. They close over the same internal wallet state (a closure).
    - Batch: use the returned `process` function to apply a whole list of
      transactions in order and get the final balances in one call.

    Args:
        initial_balances: Optional starting balances for BTC/ETH/USD (defaults to 0).

    Returns:
        A 4-tuple:
            - deposit(asset, amount): None
            - withdraw(asset, amount): bool  (False when insufficient funds)
            - snapshot(): Balances  (defensive copy of current state)
            - process(transactions): Balances  (applies all txs in order)

    Notes:
        - `process` is the “batch path” used when you already have a list of transactions
          (e.g., file/HTTP payload) and want a single final result.
        - `deposit`/`withdraw` are the “interactive path” for incremental updates
          against the same wallet state.
    """
    deposit, withdraw, snapshot = _make_wallet_core(initial_balances)

    def process(transactions: Iterable[Transaction]) -> Balances:
        port: WalletPort = SimpleNamespace(deposit=deposit, withdraw=withdraw, snapshot=snapshot)
        return _process_use_case(transactions, port)

    return deposit, withdraw, snapshot, process
