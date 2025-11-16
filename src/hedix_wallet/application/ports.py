"""Application ports (functional) connecting use-cases to the domain."""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol

from hedix_wallet.domain.types import Asset, Balances


class WalletPort(Protocol):
    def deposit(self, asset: Asset, amount: Decimal) -> None: ...
    def withdraw(self, asset: Asset, amount: Decimal) -> bool: ...
    def snapshot(self) -> Balances: ...
