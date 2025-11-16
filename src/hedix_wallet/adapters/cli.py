"""CLI adapter helpers (parsing/formatting) - pure functions."""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import cast

from hedix_wallet.domain.types import Asset, PositiveDecimal, Transaction, TransactionType


def parse_asset(value: str) -> Asset:
    upper = value.strip().upper()
    if upper not in ("BTC", "ETH", "USD"):
        raise ValueError(f"Invalid asset: '{value}'. Supported: BTC, ETH, USD")
    return upper


def parse_transaction(line: str) -> Transaction:
    parts = line.strip().split()
    if len(parts) != 3:
        raise ValueError("Invalid transaction format. Expected: 'TYPE ASSET AMOUNT'")

    type_str, asset_str, amount_str = parts
    type_upper: TransactionType = type_str.upper()

    if type_upper not in ("DEPOSIT", "WITHDRAW"):
        raise ValueError("Invalid transaction type. Expected: DEPOSIT or WITHDRAW")

    asset = parse_asset(asset_str)
    try:
        amount = Decimal(amount_str)
    except (ValueError, ArithmeticError):
        raise ValueError(f"Invalid amount: '{amount_str}'. Must be a valid number.")

    if amount <= 0:
        raise ValueError("Transaction amount must be positive")

    positive_amount = cast(PositiveDecimal, amount)
    return {"type": type_upper, "asset": asset, "amount": positive_amount}


def format_balances(balances: Mapping[Asset, Decimal]) -> str:
    ordered_assets: list[Asset] = ["BTC", "ETH", "USD"]
    parts = [f"{asset}: {balances.get(asset, Decimal('0'))}" for asset in ordered_assets]
    return ", ".join(parts)
