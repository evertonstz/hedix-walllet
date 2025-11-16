"""Unit tests for parsing and formatting helpers."""

from decimal import Decimal

import pytest

from hedix_wallet.wallet import format_balances, parse_transaction


class TestParsingAndFormatting:
    """Test suite for parse_transaction and format_balances."""

    def test_parse_deposit_transaction(self) -> None:
        tx = parse_transaction("DEPOSIT BTC 1.5")
        assert tx["type"] == "DEPOSIT"
        assert tx["asset"] == "BTC"
        assert tx["amount"] == Decimal("1.5")

    def test_parse_withdraw_transaction(self) -> None:
        tx = parse_transaction("WITHDRAW USD 300")
        assert tx["type"] == "WITHDRAW"
        assert tx["asset"] == "USD"
        assert tx["amount"] == Decimal("300")

    def test_parse_transaction_case_insensitive(self) -> None:
        tx = parse_transaction("deposit eth 2.5")
        assert tx["type"] == "DEPOSIT"
        assert tx["asset"] == "ETH"
        assert tx["amount"] == Decimal("2.5")

    def test_parse_transaction_with_extra_whitespace(self) -> None:
        tx = parse_transaction("  DEPOSIT   BTC   1.0  ")
        assert tx["type"] == "DEPOSIT"
        assert tx["asset"] == "BTC"
        assert tx["amount"] == Decimal("1.0")

    def test_parse_transaction_invalid_format_raises_error(self) -> None:
        with pytest.raises(ValueError, match="Invalid transaction format"):
            parse_transaction("DEPOSIT BTC")

    def test_parse_transaction_invalid_type_raises_error(self) -> None:
        with pytest.raises(ValueError, match="Invalid transaction type"):
            parse_transaction("TRANSFER BTC 1.0")

    def test_parse_transaction_invalid_asset_raises_error(self) -> None:
        with pytest.raises(ValueError, match="Invalid asset"):
            parse_transaction("DEPOSIT XRP 100")

    def test_parse_transaction_invalid_amount_raises_error(self) -> None:
        with pytest.raises(ValueError, match="Invalid amount"):
            parse_transaction("DEPOSIT BTC abc")

    def test_format_balances(self) -> None:
        balances = {"BTC": Decimal("1.0"), "ETH": Decimal("5.0"), "USD": Decimal("700.0")}
        formatted = format_balances(balances)
        assert "BTC: 1.0" in formatted
        assert "ETH: 5.0" in formatted
        assert "USD: 700.0" in formatted

    def test_format_balances_with_zeros(self) -> None:
        balances = {"BTC": Decimal("0"), "ETH": Decimal("0"), "USD": Decimal("100.0")}
        formatted = format_balances(balances)
        assert "BTC: 0" in formatted
        assert "ETH: 0" in formatted
        assert "USD: 100.0" in formatted
