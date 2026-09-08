# KACHING! demo

Show the boundary: an untrusted proposal becomes either zero authority or an
exact-action Ed25519 authorization lease. The Enforcement Lab verifies KACHING!
authority and never executes a financial action.

## Launch

From the repository root, after creating and activating a Python 3.11+ virtual
environment:

```bash
python -m pip install -e .
cd ui
npm ci --ignore-scripts
npm run build
cd ..
python -m tradegate.web
```

Open **http://127.0.0.1:8890**. Offline fixtures are the default. Use
`python -m tradegate.web --live` only with an existing securely configured Binance
CLI account when a new read-only observation is needed. The browser has no
order-test, live order, transfer, withdrawal or credential-management route.

## Seven-scene Judge Mode

Select **Run judge demo**. Each result comes from the local server's compiler or
verifier. The stage animation explains the pipeline; it is not a timing trace of
network or compiler execution.

1. An untrusted financial proposal enters the command deck.
2. Policy returns BLOCK, zero authorized and no lease.
3. Changing a protected receipt is rejected against its retained original.
4. A natural-language override cannot alter deterministic policy.
5. Five policy attacks are contained by real compiler/verifier checks.
6. A labeled ALLOW fixture issues a short-lived Ed25519 authorization lease.
7. The exact action verifies VALID and seven authorization bypasses are rejected.

Judge Mode finishes at the Enforcement Lab. Its deterministic fixtures are not
current Binance state. The separate live mode acquires authenticated account
observation, public market state and current `exchangeInfo` contract data.

## Recording

Use the [canonical 98-second shot list and voiceover](DEMO_SCRIPT.md).
Record the final production build at **1440×900 or 1920×1080**, after browser and
responsive checks. Keep the mode/source label visible and preserve the real
server-returned verdicts and rejection reasons.

The sequence is: KACHING! thesis → untrusted intent → deterministic compiler →
BLOCK → REVIEW envelope → ALLOW lease → exact enforcement → seven bypasses →
final KACHING! thesis. The final cut uses clearly labeled local fixtures. Its
package path is [docs/demo/KACHING-98s.mp4](docs/demo/KACHING-98s.mp4).

For the Binance evidence shot, use a current read-only result or an existing,
sanitized capture labeled **RECORDED LIVE EVIDENCE** with its actual observation
timestamp. An offline-only recording must say so. Do not manufacture a live shot
from fixture data or record private evidence files. A dated written verification
record can be shown as a record, but must not be presented as browser footage of
that live observation.

Compile the ALLOW fixture immediately before showing its 30-second lease and
validating the exact action. If it expires between takes, recompile and record the
new real lease. The seven-bypass arena uses its own deterministic fixture and
tests expiry with an injected verifier clock; it does not wait for live authority
to expire or change system time.

## Required screenshots

| Asset | Required visible evidence |
|---|---|
| [01-command-deck.png](docs/screenshots/01-command-deck.png) | KACHING!, untrusted proposal, seven-stage compiler, receipt. |
| [02-block.png](docs/screenshots/02-block.png) | BLOCK, determining rules, zero authorized, no lease. |
| [03-review-safe-envelope.png](docs/screenshots/03-review-safe-envelope.png) | Fixture label, 100.00 USDT requested, 24.37 USDT maximum admissible, zero authorized. |
| [04-authorization-lease.png](docs/screenshots/04-authorization-lease.png) | ALLOW fixture, Ed25519, ceiling, countdown, audience, issuer fingerprint. |
| [05-enforcement-valid.png](docs/screenshots/05-enforcement-valid.png) | Exact signed action and server result VALID. |
| [06-seven-bypasses.png](docs/screenshots/06-seven-bypasses.png) | Baseline VALID and 7/7 bypasses rejected with deterministic reasons. |
| [07-receipt-tamper.png](docs/screenshots/07-receipt-tamper.png) | Modified protected receipt rejected; original authorization unchanged. |

The [verification record](docs/VERIFICATION.md) records which captures and video
actually exist, their build provenance and measured video duration. Asset links
and a recording script alone do not establish completion.

## Optional technical proof

From the standalone repository root:

```bash
python demo_attack_suite.py
```

This exercises both adversarial layers and reports their actual results:

```text
5 / 5 POLICY ATTACKS CONTAINED
BASELINE — VALID
7 / 7 AUTHORIZATION BYPASSES REJECTED
```

The [full regression commands](README.md#verify-it-yourself) cover the standalone
77 Python and 8 UI tests, compileall, production build and the public release audit.
No financial transaction or order-test is required for the recording.

## Claim boundary

The SHA-256 decision receipt is checked against the locally retained original.
The separate Ed25519 lease authenticates the KACHING! issuer and signed claims.
Never call the receipt checksum a signature.

Call the evaluation API **AuthZEN-inspired** and the signed object a **KACHING!
Authorization Lease**. Consuming verification demonstrates replay rejection with
a bounded process-local cache; non-consuming previews do not check replay history.
The system does not control independent software holding Binance credentials.
No exchange acceptance, certification, endorsement or profit is implied.
