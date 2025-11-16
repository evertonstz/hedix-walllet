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

Tests:
```bash
uv run pytest
uv run ruff check src/ tests/
uv run black src/ tests/
```

## Public API (facade)
- `make_wallet()` → `(deposit, withdraw, snapshot, process)`:
  - `deposit(asset, amount)` → None
  - `withdraw(asset, amount)` → bool
  - `snapshot()` → Balances
  - `process(transactions)` → Balances (batch)
- `parse_transaction(str)` → Transaction
- `format_balances(balances)` → str

## Architecture (functional hexagonal)
- Domain:
  - `wallet_core.make_wallet` (closure over state)
  - Pure reducers: `reducers.compute_next_balances`, `reducers.compute_balances`
  - Typed models: `types.py` (Asset, Transaction, Balances, PositiveDecimal)
- Application:
  - `use_cases.process_transactions` with a `WalletPort` Protocol
- Adapters:
  - `adapters/cli.py` (parse/format)
- Facade:
  - `wallet.py` re-exports and wires pieces into a tiny API

For a deeper dive, see the full architecture document: [ARCH.md](ARCH.md)

## Functional paradigm
- Core logic is pure: reducers (`compute_next_balances`, `compute_balances`) return new states without mutating inputs.
- State lives in a closure: `wallet_core.make_wallet` provides `deposit/withdraw/snapshot` that close over private `balances`.
- Side effects at the edges: parsing/printing/CLI; application use case orchestrates pure functions via a typed `WalletPort`.
- Benefits: easy testing, predictable behavior, safe composition, and clear boundaries between pure and impure code.

```