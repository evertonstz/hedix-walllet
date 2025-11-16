"""Domain types for the wallet (pure typing, no I/O or adapters)."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from decimal import Decimal
from typing import Literal, NewType, TypeAlias, TypedDict

# Supported assets
Asset: TypeAlias = Literal["BTC", "ETH", "USD"]

# Supported transaction types
TransactionType: TypeAlias = Literal["DEPOSIT", "WITHDRAW"]

# Marker type for amounts that have been validated to be positive
PositiveDecimal = NewType("PositiveDecimal", Decimal)


class Transaction(TypedDict):
    type: TransactionType
    asset: Asset
    amount: PositiveDecimal


class Balances(TypedDict):
    BTC: Decimal
    ETH: Decimal
    USD: Decimal


# Callable type alias for batch processing
ProcessFunc: TypeAlias = Callable[[Iterable[Transaction]], Balances]
