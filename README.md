# 🚀 Hedix Wallet

A small crypto wallet that processes BTC/ETH/USD transactions in order.
Deposits always succeed; withdrawals succeed only with sufficient funds.
Amounts use Decimal.

## Quick start

Prereqs: Python 3.11+, UV

```bash
uv venv && source .venv/bin/activate # create & activate venv with UV
uv pip install -e ".[dev]"           # install
uv run wallet                        # run
```

Docker:
```bash
docker build -t hedix-wallet .
docker run --rm hedix-wallet
```

## Tests
- How to run:
  - All tests: `uv run pytest`
  - Unit only: `uv run pytest tests/unit/`
  - Integration only: `uv run pytest tests/integration/`
- Unit suites:
  - `tests/unit/test_wallet.py` (closure API), `test_transaction.py` (ops), `test_use_case.py` (orchestration),
    `test_cli_adapter.py` (parse/format), `test_reducers.py` (pure reducers).
- Integration suites:
  - `tests/integration/test_example_scenario.py` (spec example),
    `test_edge_cases.py` (edge cases), `test_state_isolation.py` (state isolation).
- Approach:
  - Prefer pure function tests for determinism; stateful behavior tested via the closure and the use case.

## Public API (facade)
- `make_wallet()` → `(deposit, withdraw, snapshot, process)`:
  - `deposit(asset, amount)` → None
  - `withdraw(asset, amount)` → bool
  - `snapshot()` → Balances
  - `process(transactions)` → Balances (batch)
- `parse_transaction(str)` → Transaction
- `format_balances(balances)` → str

## Architecture (hexagonal focus)
- Ports (inward-facing interfaces):
  - `WalletPort` (Protocol) defines the application’s needs: `deposit`, `withdraw`, `snapshot`.
  - `use_cases.process_transactions` depends only on this port (not on concrete implementations).
- Adapters (outer layer):
  - Input/driving adapter: `main.py` (console runner) feeds transactions into the use case.
  - I/O helpers: `adapters/cli.py` parse/format external representations.
  - Domain-side adapter: `wallet_core.make_wallet` provides a concrete `WalletPort` (via closures).
- Flow and boundaries:
  - External input → adapter (parse) → use case (port) → domain implementation → adapter (format/output).
  - Dependencies point inward; swapping adapters (e.g., HTTP, DB) requires no changes to the use case.
- Facade:
  - `wallet.py` offers a stable import surface, re-exporting the API and composing the pieces.

For a deeper dive, see the full architecture document: [ARCH.md](ARCH.md)

## Functional paradigm
- Core logic is pure: reducers (`compute_next_balances`, `compute_balances`) return new states without mutating inputs.
- State lives in a closure: `wallet_core.make_wallet` provides `deposit/withdraw/snapshot` that close over private `balances`.
- Side effects at the edges: parsing/printing/CLI; application use case orchestrates pure functions via a typed `WalletPort`.
- Benefits: easy testing, predictable behavior, safe composition, and clear boundaries between pure and impure code.

```