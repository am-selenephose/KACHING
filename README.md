# KACHING!

**Before an AI can touch money, it must carry proof.**

This directory is the executable Binance Agent OS Track A submission. It combines
the preserved EvidenceBound/TradeGate core with a deterministic financial-action
compiler, current Binance exchange-contract checks, signed Ed25519 authorization
leases and a local enforcement-verification lab.

```bash
cd ui
npm ci --ignore-scripts
npm run build
cd ..
python -m tradegate.web
```

Open **http://127.0.0.1:8890** and run **Judge Mode**. Offline fixtures are the
default. Enable explicit read-only Binance observations with:

```bash
python -m tradegate.web --live
```

KACHING separates capability from authorization:

```text
Untrusted proposal → evidence + exchange contract → deterministic PDP
                                           ↓
                                  ALLOW / REVIEW / BLOCK
                                           ↓ ALLOW only
                              signed authorization lease
                                           ↓
                                  local PEP verification
```

BLOCK and REVIEW authorize zero and issue no lease. ALLOW can issue a 30-second
`kaching.authorization.v1` lease signed by a local Ed25519 key. The Enforcement
Lab accepts the exact signed action and rejects amount/resource/audience mutation,
signature forgery, policy drift, expiry and replay. The PEP contains no execution
function.

Verify locally:

```bash
python -m unittest discover -s tests -v
python demo_attack_suite.py
python -m compileall -q tradegate tests
npm test --prefix ui
npm run build --prefix ui
```

For a private live receipt, choose a new output path every run:

```bash
python -m tradegate.cli --symbol BNBUSDT --side BUY --quote 10 --human \
  --evidence-out private-evidence-recording.json
```

The command above does not request order-test. Do not display private evidence,
Binance profiles, API Management, UID, balances or credentials in a public demo.

[Product overview](../README.md) · [Architecture](../ARCHITECTURE.md) ·
[Security](../SECURITY.md) · [Demo](../DEMO.md) · [Submission](SUBMISSION.md)
