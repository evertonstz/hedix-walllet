## Architecture Overview (Functional + Hexagonal)

This project uses a lightweight, fully functional take on Hexagonal Architecture (Ports & Adapters) to keep the code small, testable, and easy to extend.

### Goals
- **Simplicity**: Small functional surface area, no classes
- **Isolation**: Pure domain separated from I/O and formatting
- **Extensibility**: Add features by composing small functions

### Layers
- **Domain (`src/hedix_wallet/domain/`)**
  - `types.py`: Core types using `TypedDict` and `Literal` (e.g., `Asset`, `Transaction`)
  - `wallet_core.py`: Stateful closure (`make_wallet`) returning `deposit`, `withdraw`, `snapshot`
- **Application (`src/hedix_wallet/application/`)**
  - `ports.py`: Functional “port” (`WalletPort`) bundling `deposit`, `withdraw`, `snapshot`
  - `use_cases.py`: `process_transactions(transactions, port)` orchestrates domain calls
- **Adapters (`src/hedix_wallet/adapters/`)**
  - `cli.py`: CLI helpers: `parse_transaction(line)`, `format_balances(balances)`
- **Facade (`src/hedix_wallet/wallet.py`)**
  - Public entry to the functional API: `make_wallet`, `parse_transaction`, `format_balances`
  - Composes domain + application + adapters to keep external API tiny
- **Entry Point**
  - `src/hedix_wallet/main.py`: Example runner that uses the facade

### Pure Core (Reducers)
To keep the domain easy to reason about and test, we expose two pure reducers:

- `domain/reducers.py`
  - `compute_next_balances(balances, tx) -> Balances` applies a single transaction
  - `compute_balances(initial, txs) -> Balances` folds a list of transactions

The closure returned by `wallet_core.make_wallet()` delegates to these reducers, giving us a thin stateful layer over a pure, deterministic core.

### Data Flow
```
User Input → adapters/cli.parse_transaction → application/use_cases.process_transactions
           → domain/wallet_core (deposit/withdraw/snapshot) → adapters/cli.format_balances
```

### Why Functional?
- **Clear state boundaries**: State lives in a closure returned by `make_wallet()`
- **Testability**: Easy to unit test functions; no mocking frameworks needed
- **No inheritance/DI overhead**: Hexagonal separation with simple functions and typed ports

### Extension Points
- **New assets**: Update validation/order in `adapters/cli.parse_asset` and `format_balances`
- **New transaction types**: Extend the `Transaction['type']` union and branch in `use_cases.process_transactions`
- **New adapters**: Add a new module (e.g., `http.py`) that converts external inputs to `Transaction` and calls the use case

With reducers in place, reuse is simple—batch processors can call the pure `compute_balances`, while interactive flows can use the closure for incremental state.

### Testing
- **Unit tests**: Focus on `wallet_core` behavior, parsing/formatting, and the use case
- **Integration tests**: End-to-end scenarios built from the public facade API

### Public API (Facade)
- `make_wallet()` → `(deposit, withdraw, snapshot, process_transactions)`
- `parse_transaction(line)` → `Transaction`
- `format_balances(balances)` → `str`

This keeps consumers simple while the internals remain cleanly separated by concerns. 
