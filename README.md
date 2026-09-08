# KACHING!

**Before an AI can touch money, it must carry proof.**

This directory is the executable Binance Agent OS Track A submission. It combines
the preserved EvidenceBound/TradeGate core with a deterministic financial-action
compiler, current Binance exchange-contract checks, signed Ed25519 authorization
leases and a local enforcement-verification lab.

The public product is KACHING! The `tradegate` Python package and this directory
retain their existing names for compatibility.

## Run

Requires Python 3.11+ in an activated virtual environment, Node 22.12+ (or Node 24)
and npm. From this directory:

```bash
python -m pip install -e .
cd ui
npm ci --ignore-scripts
npm run build
cd ..
python -m tradegate.web
```

Open **http://127.0.0.1:8890** and select **Run judge demo**. Seven scenes call
the real local compiler and verifiers, ending in Enforcement Lab. Offline fixtures
are the default. Enable explicit read-only Binance observations with an existing
securely configured CLI account:

```bash
python -m tradegate.web --live
```

## Capability is not authorization

```text
Untrusted proposal → evidence + exchange contract → deterministic policy
                                           ↓
                                  ALLOW / REVIEW / BLOCK
                                           ↓ ALLOW only
                              Ed25519 Authorization Lease
                                           ↓
                                  local PEP verification
                                           ↓
                                   VALID / REJECTED
```

BLOCK and REVIEW authorize zero and issue no lease. A 100.00 USDT REVIEW fixture
has a 24.37 USDT safe envelope; applying that envelope creates a new draft that
must be compiled again. ALLOW can issue a 30-second `kaching.authorization.v1`
lease signed by a local Ed25519 key.

The Enforcement Lab accepts the exact signed action and demonstrates seven
rejections: amount escalation, resource mutation, audience mutation, signature
forgery, policy drift, expiry and replay in consuming mode. Replay state is
bounded and in-memory; preview checks do not consume or check replay history.
The PEP has no execution function.

SHA-256 protects decision-receipt integrity against the retained original.
Ed25519 authenticates the separate authorization lease. Public responses contain
neither private signing material nor Binance credentials or account balances.

## Verify

```bash
python -m unittest discover -s tests -v
python demo_attack_suite.py
python -m compileall -q tradegate tests
npm test --prefix ui
npm run build --prefix ui
cd ..
python -m unittest discover -s tests -v
python scripts/release_safety_audit.py
git diff --check
```

The integrated baseline is 77 KACHING! tests, 8 UI tests and 50 root tests:
135 total. The separate six Attest PoC tests are outside that total. Consult
[VERIFICATION.md](../docs/VERIFICATION.md) for the final build's measured results,
browser QA, screenshots, video and CI status.

[Product overview and screenshots](../README.md) ·
[Architecture](../ARCHITECTURE.md) · [Security](../SECURITY.md) ·
[Demo](../DEMO.md) · [96-second script](DEMO_SCRIPT.md) · [Submission](SUBMISSION.md)
