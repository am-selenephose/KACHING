# EvidenceBound TradeGate — 110-second demo

## 0:00–0:12 — Hook

**Voice:** "AI agents can propose trades. Proposal is not authorization. EvidenceBound TradeGate is the deterministic gate between an AI action and money."

**Screen:** architecture line from README.

## 0:12–0:30 — Real Binance state

Run/show the already verified flow against BNBUSDT.

**Voice:** "TradeGate reads live Binance market data and authenticated account state. Credentials stay inside Binance CLI; TradeGate never stores them."

Show only: symbol, market source, account-authenticated=true. Do not show balances, API keys, UID, or profile files.

## 0:30–0:52 — Governor decision

Show the genuine result:

```text
verdict: BLOCK
reasons: CASH_BUFFER_BREACH, NO_SAFE_NOTIONAL
requested_quote_notional: 10
approved_quote_notional: 0
```

**Voice:** "This is a production-account integration proof. The governor refused the proposed buy because its deterministic cash policy could not approve a safe notional. No trade was placed."

## 0:52–1:15 — Evidence receipt

Show the evidence SHA only:

`9434dc11e04a64a90721abdb866241169d89589030358ae7ef90ba3b48d816f2`

**Voice:** "The intent, observations, policy result, reasons and metrics are bound into a canonical SHA-256 receipt."

Show `ORIGINAL_VERIFIED=True`.

## 1:15–1:32 — Tamper test

Change the protected verdict in a copy of the packet.

Show `TAMPERED_VERIFIED=False`.

**Voice:** "Change the decision after the fact and verification fails."

## 1:32–1:48 — Execution boundary

**Voice:** "If TradeGate returns BLOCK, it refuses even Binance order-test. If a future intent is ALLOW or REVIEW-approved, only Binance's non-executing order-test validation is available. There is no live-order placement path in this build."

## 1:48–1:50 — Close

**Voice:** "AI proposes. TradeGate decides what is allowed to touch money."
