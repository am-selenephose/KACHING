# EvidenceBound TradeGate

Fail-closed pre-trade authorization for Binance Agent OS.

**AI proposes. TradeGate decides what is allowed to touch money.**

TradeGate reads live Binance market state plus authenticated account state, applies a deterministic policy, and returns `ALLOW`, `REVIEW`, or `BLOCK`. Every decision is bound into a canonical SHA-256 evidence receipt. Missing authorization fails closed.

```text
AI intent -> Binance state -> deterministic governor -> evidence receipt
                                                   -> ALLOW / REVIEW / BLOCK
```

A real production-account integration test against BNBUSDT produced a genuine `BLOCK` for a proposed 10 USDT BUY because the account state could not satisfy the cash-buffer rule. The original receipt verified; changing the protected verdict caused verification to fail. No live order or funds movement occurred.

## Run

```bash
python -m pip install -e .
binance-cli profile view
tradegate --symbol BNBUSDT --side BUY --quote 10 --evidence-out live-proof.json
```

`live-proof.json` is deliberately gitignored because it can contain account-state values.

## Test

```bash
python -m unittest discover -s tests -v
python -m compileall -q tradegate tests
```

Six deterministic tests cover auth failure, cash-buffer rejection, ALLOW, REVIEW, depth rejection, and tamper detection.

## Execution boundary

This build contains no withdrawal, transfer, or live-order placement path. `--order-test` uses Binance's non-executing order-test endpoint and is refused when the governor returns `BLOCK`.

See `DEMO_SCRIPT.md` for the 110-second demo and `SUBMISSION.md` for the Track A posting checklist.
