# KACHING! verification record — September 8, 2026

## Current GitHub and branding check

The integrated authorization kernel is on `hackathon/binance-agent-os-tradegate`.
The public repository has been renamed to **am-selenephos/KACHING** at the owner's
request; the product display name is **KACHING!**. The main landing README and
About description now direct visitors to the KACHING! branch.

Fresh local regression after the branding changes: **50 root + 77 authorization
+ 8 UI = 85 passed, 0 failed, 0 skipped**. Compileall, typecheck, production
build, public audit, 5/5 policy attacks and 7/7 authorization bypasses passed.
Authorization-kernel semantics were not changed by this branding pass.

The current production stylesheet still imports `midnight.css`. The final
metallic-gold / black RICHY-like / holographic treatment remains pending. No final
screenshots or video are present in tracked source. The browser plugin still
returns `ERR_BLOCKED_BY_CLIENT` for the loopback preview, so this pass does not
claim a new rendered QA result.

One GitHub Actions dispatch recheck returned HTTP 422:
**“Actions has been disabled for this user.”** Cloud CI remains unverified.

The evidence below records the earlier integrated-kernel verification; it does
not certify the remaining visual release.

## Authorization-kernel local regression

Fresh verification on the isolated `design/kaching-authorization-kernel` worktree:

| Check | Passed | Failed | Skipped |
|---|---:|---:|---:|
| EvidenceBound runtime / release-safety tests | 50 | 0 | 0 |
| KACHING compiler, exchange, authorization, service, HTTP and legacy TradeGate tests | 77 | 0 | 0 |
| KACHING UI unit tests | 8 | 0 | 0 |
| **Total test cases** | **85** | **0** | **0** |

Additional executable gates:

- Python `compileall`: PASS.
- TypeScript typecheck + Vite production build: PASS.
- Public repository safety audit: PASS.
- `git diff --check`: PASS.
- Deterministic policy/adversarial arena: **5 / 5 contained**.
- Authorization bypass gauntlet: exact baseline **VALID**, then **7 / 7 bypasses rejected**.

The seven rejected authorization classes are amount escalation, resource mutation,
audience mutation, signature forgery, policy drift, expiry and consumed-lease replay.
These are controlled deterministic tests, not a security certification.

Commands used:

```bash
python -m unittest discover -s tests -v
python scripts/release_safety_audit.py
(cd tradegate-hackathon && PYTHONPATH=. python -m unittest discover -s tests -v)
(cd tradegate-hackathon && python -m compileall -q tradegate tests)
(cd tradegate-hackathon && PYTHONPATH=. python demo_attack_suite.py)
npm test --prefix tradegate-hackathon/ui
npm run build --prefix tradegate-hackathon/ui
git diff --check
```

## Signed authorization proof

The new authorization layer uses Ed25519 through Python `cryptography`. The issuer
private key is local, owner-readable (`0600`) and outside the repository. Public
state may expose only the Ed25519 public key/fingerprint and signed lease.

Verified behavior:

- BLOCK and REVIEW issue no authorization lease.
- ALLOW issues `kaching.authorization.v1` with a 30-second default TTL.
- The exact signed action verifies VALID with the trusted public key.
- Signed-payload modification fails signature verification.
- Changed action/amount, resource or audience fails exact-action verification.
- Policy hash drift invalidates the lease.
- Expired leases are rejected.
- A locally consumed lease is rejected on replay.
- Private issuer-key material is absent from the serialized lease/browser DTO.

Replay state is bounded/in-memory and is not claimed to survive restart or operate
across distributed PEPs.

## Fresh live Binance read-only observation

At approximately **2026-09-08 16:13 UTC**, KACHING performed a fresh read-only
BNBUSDT authorization compilation using the existing authenticated Binance setup:

- account authenticated: **true**;
- market source: `binance-rest-fallback:spot`;
- current exchange-contract check: **true**;
- proposal: BUY BNBUSDT, 10 USDT;
- verdict: **BLOCK**; authorized: **0 USDT**;
- reasons: `CASH_BUFFER_BREACH`, `NO_SAFE_NOTIONAL`;
- determining rules: `KCH-CASH-001`, `KCH-NOTIONAL-001`;
- public live safe envelope: **omitted / owner-private**;
- authorization lease issued: **false**, as required for BLOCK.

Policy SHA-256:
`b69dd27694b0e5ed40583bc32334f0b7623bf59c8101164e3851522fbf5fcd9e`

Decision SHA-256:
`d87c413ef6644dd11eb68c08bad0a75c0834b476b8b2a4a258d683eb4bcb88db`

No order-test, live order, transfer or withdrawal was requested. No private balance,
UID, API key, API secret or profile output was printed. This is a dated observation,
not continuous monitoring.

## Independent rendered browser QA

A temporary Playwright Core harness outside the repository launched system Chromium
against the built loopback application. The application itself was not granted any
extra browser privileges.

Authorization UI smoke: **PASS**. Verified:

- HTTP 200 initial load and KACHING rendering;
- deterministic ALLOW produces a visible signed Ed25519 Authorization Lease;
- `/api/state` omits `free_usdt`, API-key/secret and auth-error fields;
- exact signed action at Enforcement Lab: **VALID**;
- +0.01 USDT action mutation: **REJECTED / ACTION_MISMATCH**;
- one-button authorization gauntlet: **7 / 7 rejected**;
- upgraded Judge Mode reaches final scene **7 / 7** and lands in Enforcement Lab;
- 375 / 768 / 1280 / 1440 / 1920 px viewport widths: no horizontal overflow;
- keyboard focus works on workspace navigation;
- reduced-motion path works;
- relevant browser console errors/warnings: **0**.

The browser body/state scan did not expose private balance-field names or credential
labels. Pattern and rendered-text scans reduce risk but cannot mathematically prove
the absence of every possible secret.

A temporary QA screenshot was captured outside the repository. It is evidence only,
not final submission artwork.

## Visual theme status

Authorization semantics are deliberately separate from theme tokens. The user has
approved a final visual direction of true metallic gold, black editorial serif type
and restrained holographic optical sheen. That art-direction correction has **not
yet landed on the public hackathon branch** as of this verification record.

Therefore the authorization UI is functionally browser-verified, but the final
submission screenshots/video must be recaptured and the same browser QA rerun after
the approved metallic-gold theme lands. Current midnight-theme captures are not the
final submission artwork.

## GitHub Actions

The hackathon branch already contains KACHING Python/UI checks in the active CI
workflow. Earlier manual dispatch returned HTTP 422 with GitHub reporting:
**“Actions has been disabled for this user.”** No cloud run was created.

Local verification is green, but cloud CI remains **UNVERIFIED** until GitHub
re-enables Actions for the account and a real workflow run completes.

## Release verdict

**AUTHORIZATION KERNEL: INTEGRATED. FINAL VISUAL SUBMISSION: NOT READY.**

Remaining non-kernel gates before final Track A submission sign-off:

1. user-approved metallic-gold visual theme lands;
2. rerun rendered QA on that exact merged visual build;
3. capture final screenshots and demo video;
4. complete and independently verify the X submission + official Binance survey;
5. cloud CI remains an external account-level blocker and must not be called PASS.

No top-three placement, formal AuthZEN conformance, Binance endorsement or universal
security guarantee is claimed.
