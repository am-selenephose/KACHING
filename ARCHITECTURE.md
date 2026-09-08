# KACHING! architecture

KACHING is a local **Policy Decision Point (PDP)** plus a separate local
**Policy Enforcement Point (PEP) simulation** for financial-agent actions. It is
AuthZEN-inspired, not a claim of formal AuthZEN conformance.

## Trust model

The proposer is untrusted. Natural-language metadata is untrusted. Requested
action parameters are untrusted. A caller cannot submit policy, account state or
issuer keys through the browser.

Trusted local components are the KACHING process, owner-selected policy, Binance
observation adapter and local Ed25519 issuer key. Credentials remain managed by
the owner's Binance CLI outside the repository.

The default authorization posture is deny. **BLOCK and REVIEW authorize zero.**
Only ALLOW is eligible for a signed authorization lease.

## Decision pipeline

```text
FinancialIntent
    ↓
01 Normalize
02 Observe market/account state
03 Verify evidence + exchange contract
04 Compile deterministic policy
05 Calculate Decimal safe envelope
06 Authorize: ALLOW / REVIEW / BLOCK
07 Attest decision receipt
    ↓ ALLOW only
Ed25519 Authorization Lease
    ↓
PEP verifier
    ↓
VALID / REJECTED
```

`Compiler.compile()` remains deterministic: it performs no network calls and has
no execution capability. Observation acquisition happens before compilation.

## Canonical action identity

Authorization binds a canonical action containing:

- origin (`agent`, `human`, or `external`);
- action;
- symbol/resource;
- requested quote notional;
- audience/tool identifier.

Canonical JSON uses deterministic key ordering and Decimal normalization. Its
SHA-256 is `intent_sha256`. Changing any policy-relevant field changes the
action identity. Explanatory metadata is excluded from authorization identity and
therefore cannot rewrite policy.

## Binance observation layer

`BinanceCLI` preserves the existing authenticated account observation and live
market adapter. Public Spot REST remains the fallback for ticker/depth reads when
the CLI public request wrapper is unavailable.

KACHING additionally reads `/api/v3/exchangeInfo` as a read-only exchange
contract. The compiler fails closed when the contract is missing, stale, malformed,
for the wrong symbol, not `TRADING`, lacks MARKET support, lacks
`quoteOrderQtyMarketAllowed`, or rejects the proposed notional under parsed
notional filters.

Exchange-contract outcomes appear under explicit rule identity
`KCH-EXCHANGE-001`. Other determining rule IDs identify the policy conditions
that actually decided the verdict.

## Safe action envelope

For valid BUY observations, KACHING computes with `Decimal` and rounds down to
0.01 USDT:

```text
max(0, min(
    policy maximum quote notional,
    free quote balance × maximum balance fraction,
    free quote balance − minimum cash buffer,
    visible ask depth ÷ minimum depth multiple
))
```

A request above a positive envelope yields REVIEW and zero authorization. A zero
envelope yields BLOCK. Live public DTOs hide the exact balance-derived envelope.

## Decision receipt

Every decision receipt includes policy version/hash, determining rules, sanitized
checks/reasons, evidence commitment and `decision_sha256`. The running service
retains up to 100 original decision digests, so a caller cannot simply alter the
receipt and recalculate its self-reported checksum.

This receipt checksum is integrity evidence, not issuer authentication.

## Authorization lease

Only an ALLOW receipt may be converted into `kaching.authorization.v1`. The
lease includes:

- exact canonical action and `intent_sha256`;
- decision ID and maximum authorized amount;
- audience;
- policy version/hash;
- observation commitment;
- issue/expiry timestamps (30-second default);
- random nonce;
- Ed25519 issuer fingerprint;
- Ed25519 signature.

The issuer private key is generated locally at `~/.config/kaching/` by default,
with owner-only file permissions. Only the public key and fingerprint may be
returned to the UI.

## Enforcement verifier

The verifier checks signature before trusting the lease payload, then enforces:

1. trusted issuer fingerprint;
2. valid Ed25519 signature;
3. valid issue/expiry window;
4. unchanged current policy hash;
5. exact audience;
6. exact resource, origin, action and amount;
7. canonical intent hash;
8. amount not above the signed authorization ceiling;
9. optional one-time consumption via bounded in-memory replay cache.

The PEP returns only `VALID` or a deterministic rejection reason. It has no order
placement function. The replay cache is process-local and intentionally not a
claim of distributed replay protection.

## Authorization API

The loopback bridge exposes an AuthZEN-inspired evaluation shape:

| Endpoint | Purpose |
|---|---|
| `GET /api/state` | sanitized current decision, lease issuer and ledger |
| `POST /api/compile` | KACHING-native decision request |
| `POST /access/v1/evaluation` | Subject / Action / Resource / Context evaluation |
| `POST /api/verify` | compare public receipt with retained original digest |
| `POST /api/enforce` | verify a signed lease against an exact proposed action |
| `POST /api/arena` | five deterministic policy attacks |
| `POST /api/enforcement-arena` | seven authorization-bypass checks |

The HTTP server binds `127.0.0.1`, rejects wrong Host/Origin/cross-site Fetch
Metadata, accepts JSON-only bounded POST bodies, rejects duplicate keys and
non-standard numeric constants, applies CSP/no-store headers, and serves only the
built UI assets.

There is no browser route for order-test, live order placement, transfer,
withdrawal, credential retrieval or policy mutation.

## UI

The React/TypeScript Command Deck visualizes authentication separately from
authorization. ALLOW can display a short-lived signed Authorization Lease. The
Enforcement Lab lets a judge present the exact action or mutate amount, resource,
audience/signature and replay state; the seven-bypass gauntlet exercises the real
server-side verifier in one action.

Visual theme tokens are independent of authorization semantics so final art
direction can change without rewriting the financial core.

## Existing-core preservation

Legacy `TradeGovernor`, evidence compatibility, CLI proof generation and the
non-executing Binance `order-test` path remain. The CLI now also fetches the live
exchange contract before authorization. `order-test` still requires ALLOW and is
never exposed through the browser. No code path here places a live order.
