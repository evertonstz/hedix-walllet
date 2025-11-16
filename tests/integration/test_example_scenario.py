"""Integration test for the example scenario from the problem statement."""

from decimal import Decimal

from hedix_wallet.wallet import Transaction, make_wallet


class TestExampleScenario:
    """Integration test for the complete example scenario."""

    def test_example_scenario_from_problem_statement(self) -> None:
        """Test the exact example scenario provided in the problem statement."""
        # Setup
        _, _, _, process = make_wallet()

        # Define transactions
        transactions: list[Transaction] = [
            {"type": "DEPOSIT", "asset": "BTC", "amount": Decimal("1.5")},
            {"type": "DEPOSIT", "asset": "USD", "amount": Decimal("1000")},
            {"type": "WITHDRAW", "asset": "USD", "amount": Decimal("300")},
            {"type": "WITHDRAW", "asset": "BTC", "amount": Decimal("2.0")},  # Should fail
            {"type": "DEPOSIT", "asset": "ETH", "amount": Decimal("5.0")},
            {"type": "WITHDRAW", "asset": "BTC", "amount": Decimal("0.5")},
        ]

        # Execute
        result = process(transactions)

        # Assert final balances match expected output
        assert result["BTC"] == Decimal("1.0")
        assert result["ETH"] == Decimal("5.0")
        assert result["USD"] == Decimal("700.0")

    def test_step_by_step_execution(self) -> None:
        """Test that transactions are processed in sequence with accumulated state."""
        _, _, _, process = make_wallet()

        # Step 1: DEPOSIT BTC 1.5
        result = process([{"type": "DEPOSIT", "asset": "BTC", "amount": Decimal("1.5")}])
        assert result["BTC"] == Decimal("1.5")
        assert result["ETH"] == Decimal("0")
        assert result["USD"] == Decimal("0")

        # Step 2: DEPOSIT USD 1000 (state carries over from step 1)
        result = process([{"type": "DEPOSIT", "asset": "USD", "amount": Decimal("1000")}])
        assert result["BTC"] == Decimal("1.5")
        assert result["USD"] == Decimal("1000")

        # Step 3: WITHDRAW USD 300 (state carries over)
        result = process([{"type": "WITHDRAW", "asset": "USD", "amount": Decimal("300")}])
        assert result["USD"] == Decimal("700")

        # Step 4: WITHDRAW BTC 2.0 (should fail - insufficient funds)
        result = process([{"type": "WITHDRAW", "asset": "BTC", "amount": Decimal("2.0")}])
        assert result["BTC"] == Decimal("1.5")  # Unchanged

        # Step 5: DEPOSIT ETH 5.0 (state carries over)
        result = process([{"type": "DEPOSIT", "asset": "ETH", "amount": Decimal("5.0")}])
        assert result["ETH"] == Decimal("5.0")

        # Step 6: WITHDRAW BTC 0.5 (state carries over)
        result = process([{"type": "WITHDRAW", "asset": "BTC", "amount": Decimal("0.5")}])
        assert result["BTC"] == Decimal("1.0")

        # Final verification: all accumulated state is correct
        assert result["BTC"] == Decimal("1.0")
        assert result["ETH"] == Decimal("5.0")
        assert result["USD"] == Decimal("700.0")
