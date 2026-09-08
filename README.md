# KACHING!

## Before an AI can touch money, it must carry proof.

KACHING! is a proof-carrying financial authorization kernel for AI agents built
with Binance Agent OS.

Trading agents answer: **“What should I do?”**

KACHING! answers: **“Is this exact action authorized?”**

```text
ANY AGENT
   ↓
UNTRUSTED FINANCIAL INTENT
   ↓
KACHING!
   ├─ Binance state
   ├─ exchange contract
   ├─ deterministic policy
   ├─ safe-action envelope
   └─ ALLOW / REVIEW / BLOCK
           ↓
      ALLOW ONLY
           ↓
 Ed25519 Authorization Lease
           ↓
 Enforcement Boundary
           ↓
    VALID / REJECTED
```

**Capability is not authorization.** Credentials and tool access do not make an
agent proposal valid. REVIEW and BLOCK authorize zero. Only ALLOW can issue a
short-lived, signed authorization lease.

`docs/screenshots/command-deck.png` — capture pending

The approved final interface direction is prismatic emerald glass: a dark optical environment illuminated by emerald authority with restrained holographic refraction. Final visual polish is in progress; authorization semantics are frozen. The
[typography record](docs/TYPOGRAPHY.md) records the current legal font assets and
the required RICHY reference direction.

## What makes KACHING! different

Trading, signal, news and portfolio agents can all be proposers. KACHING! sits
beneath them as an authorization boundary.

An ALLOW lease binds the exact origin, action, symbol/resource, requested amount,
intended tool audience, policy hash, evidence commitment, issuer identity and time
window. The local verifier checks the Ed25519 signature and the proposed action
before any financial execution capability is involved.

The deterministic authorization-bypass gauntlet demonstrates seven rejection
classes: amount escalation, resource mutation, audience/tool mutation, signature
forgery, policy drift, expired authority and consumed-lease replay.

The exact signed action passes verification within its validity window and current
policy. Consuming verification rejects a second consumption of the same nonce;
non-consuming previews do not consume authority or check replay history.

## Three outcomes, one authority boundary

| Decision | Demonstration | Authority issued |
|---|---|---|
| BLOCK | A determining policy rule prevents the action. | 0 USDT; no lease. |
| REVIEW | The fixture requests 100.00 USDT; the safe envelope is 24.37 USDT. | 0 USDT; no lease. A revised draft requires recompilation. |
| ALLOW | The fixture requests 10.00 USDT and passes policy. | A 30-second Ed25519 lease for that exact action. No live trade. |

The seven visible compiler stages are **Normalize → Observe → Verify Evidence →
Compile Policy → Safe Envelope → Authorize → Attest**. Natural-language messages
remain untrusted metadata and cannot alter policy.

## Binance evidence

Authenticated account observation uses Binance CLI. Public market observations
can fall back to Binance Spot REST. Before live authorization, KACHING! also reads
current `exchangeInfo` rules: symbol status, MARKET-order support,
quote-order-quantity support and applicable notional bounds. Missing, stale or
malformed exchange state fails closed.

The [dated live proof](docs/VERIFICATION.md) records a September 8, 2026 BLOCK for
a 10 USDT BNB buy with `CASH_BUFFER_BREACH` and `NO_SAFE_NOTIONAL`; no order,
transfer or withdrawal was executed. This historical observation is not a claim
about current Binance account state. Live public receipts omit private balances
and exact balance-derived safe envelopes.

## Run KACHING!

Requirements: Python 3.11+, Node 22.12+ (or Node 24), npm. From the repository root,
install the Python package and its Ed25519 dependency in a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
cd ui
npm ci --ignore-scripts
npm run build
cd ..
python -m tradegate.web
```

Open **http://127.0.0.1:8890** and select **Run judge demo**. Its seven scenes use
actual local compiler, signature and verifier calls with clearly labeled fixtures.
Offline fixtures are the default. With an existing securely configured Binance
CLI account, explicit read-only Binance observations can be enabled with:

```bash
python -m tradegate.web --live
```

The browser has no order, transfer, withdrawal or credential-management route.
The server binds to `127.0.0.1`.

## Verify it yourself

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s tests -v
python demo_attack_suite.py
python -m compileall -q tradegate tests
npm test --prefix ui
npm run build --prefix ui
cd ..
python scripts/release_safety_audit.py
git diff --check
```

The standalone authorization-kernel baseline is **85 product tests: 77 Python + 8 UI**, with 5/5 policy attacks contained and 7/7 authorization bypasses rejected. EvidenceBound's separate provenance-runtime tests are intentionally not part of this repository.
Use the [verification record](docs/VERIFICATION.md) for the final build's exact
test counts, browser evidence, responsive checks and release status. Local passes
do not establish GitHub Actions success; CI requires an actual completed run.

## Demo assets

The [96-second recording script](DEMO_SCRIPT.md) distinguishes
deterministic fixtures from live reads and dated recorded evidence. The release
record identifies the captured video, its measured duration and verified build.

| View | Screenshot |
|---|---|
| Command deck | `docs/screenshots/command-deck.png` — capture pending |
| BLOCK | `docs/screenshots/block-state.png` — capture pending |
| REVIEW | `docs/screenshots/safe-envelope-review.png` — capture pending |
| ALLOW | `docs/screenshots/authorization-lease.png` — capture pending |
| Enforcement Lab | `docs/screenshots/enforcement-valid.png` — capture pending |
| Authorization gauntlet | `docs/screenshots/authorization-gauntlet.png` — capture pending |
| Receipt integrity | `docs/screenshots/tamper-failure.png` — capture pending |

## Cryptographic boundary

Public decision receipts carry SHA-256 integrity identifiers checked against the
local retained original. **Authorization leases are different:** they are signed
with a local Ed25519 issuer key and can be independently verified with the trusted
public key. The private key is generated outside the repository, kept
owner-readable (`0600`) and never returned to the browser.

Replay protection is bounded, local, in-memory and applied in consuming mode; it
does not survive restart or cover distributed verifiers. An external program that
independently holds Binance credentials can bypass this application; KACHING!
cannot revoke credentials it does not control. The lease is KACHING! authorization
evidence, not a Binance-native token, Binance endorsement, formal AuthZEN
conformance or a guarantee of profitability/exchange acceptance. There is **no
live execution path** in the browser or authorization verifier.

[Architecture](ARCHITECTURE.md) · [Security boundary](SECURITY.md) ·
[Demo](DEMO.md) · [Verification](docs/VERIFICATION.md) ·
[Track A submission](SUBMISSION.md)

The public submission source is the standalone `am-selenephos/KACHING` repository. Existing `tradegate` import paths and versioned evidence identifiers remain stable for compatibility.
