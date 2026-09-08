# KACHING! architecture

KACHING! is a local Policy Decision Point (PDP) plus a logical Policy
Enforcement Point (PEP) simulation for financial-agent actions. The evaluation
shape is AuthZEN-inspired; no formal AuthZEN conformance is claimed.

The PDP, issuer and PEP verifier are logical components in one trusted
single-user Python process. They are not separately deployed or isolated security
services in this prototype.

## Trust model

Untrusted inputs include the proposer, natural-language metadata, requested action
parameters and caller-supplied identity labels. `origin` and `subject.type` are
assertions, not authenticated agent or human identities; `subject.id` is not used
for access control.

Trusted local inputs include:

- the code-configured policy;
- acquired market, account and exchange-contract snapshots;
- the KACHING! process and its in-memory receipt anchors;
- the local Ed25519 issuer private key;
- the public key selected by the in-process verifier.

Binance credentials remain in the owner's existing Binance CLI configuration and
outside the repository. Browser callers cannot provide policy, account state or
issuer keys. The default posture is deny: BLOCK and REVIEW authorize zero; only
ALLOW is eligible for a signed lease.

## Runtime topology

```text
Browser on 127.0.0.1
        │ JSON / same local origin
        ▼
Python HTTP bridge
        │
        ├── Service
        │    ├── observation adapter
        │    ├── Compiler / PDP
        │    ├── Ed25519 issuer
        │    ├── AuthorizationVerifier / logical PEP
        │    ├── receipt anchors (memory)
        │    ├── replay cache (memory)
        │    └── decision ledger (memory)
        │
        └── built React UI
```

The browser/PEP surface has no financial execution method. The same process can
optionally perform read-only observations when launched with `--live`.

## Decision path

```text
FinancialIntent
    │
    ├─ 01 Normalize
    ├─ 02 Observe market/account state
    ├─ 03 Verify evidence structure, provenance labels and exchange contract
    ├─ 04 Compile code-configured policy
    ├─ 05 Calculate Decimal safe envelope
    ├─ 06 Authorize: ALLOW / REVIEW / BLOCK
    └─ 07 Attest decision receipt
            │
            └─ ALLOW only → Ed25519 Authorization Lease
                                      │
                                      └─ local verifier → VALID / REJECTED
```

The policy-decision calculation is reproducible for fixed normalized inputs,
policy, observation mode and supplied clock. Compilation performs no network call
or execution. A complete receipt is intentionally unique because it includes a
timestamp, random proposal ID and a salted private-evidence commitment.

## Canonical action identity

Authorization binds a canonical action containing:

- origin (`agent`, `human`, or `external`);
- action;
- symbol/resource;
- requested quote notional;
- audience/tool identifier.

Canonical JSON uses sorted keys and normalized Decimal strings. Its SHA-256 is
`intent_sha256`. Changing a policy-relevant field changes the identity.
Explanatory metadata is excluded from authorization identity and cannot rewrite
policy.

## Observation adapters

In fixture mode, KACHING! constructs explicitly labeled deterministic account,
market and exchange-contract snapshots. These are demonstration data, not current
Binance state.

In live mode, the adapter:

1. reads public ticker and depth through Binance CLI, with Binance Spot REST as a
   public-market fallback;
2. reads authenticated account state through Binance CLI;
3. reads `/api/v3/exchangeInfo` through public Spot REST.

The exchange-contract parser intentionally covers only symbol identity, status,
MARKET-order support, `quoteOrderQtyMarketAllowed`, observation time and notional
bounds. It does not implement the complete `exchangeInfo` contract such as all
lot-size, price, asset-permission or filter-applicability rules. Missing, stale,
malformed or unsupported contract state fails closed, but ALLOW cannot predict
exchange acceptance.

## Safe-action envelope

For structurally valid BUY observations, KACHING! calculates with `Decimal` and
rounds down to 0.01 USDT:

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
This is a per-decision bound, not a fund reservation or cumulative-spend budget.

## Decision receipt

Every public decision receipt includes:

- policy version and SHA-256;
- evaluated and determining rule identities;
- sanitized checks, reasons and remediation;
- a salted local observation commitment;
- `decision_sha256`.

The service retains original decision digests for at most 100 proposals. Receipt
verification compares a submitted object with that retained digest, so changing a
receipt and recalculating its self-reported hash is insufficient. The digest and
anchor provide local integrity checking, not issuer authentication or Binance
attestation.

The private observation commitment hashes locally assembled intent, policy,
observations and a random nonce. It reduces balance-guessing risk and binds the
receipt to retained local evidence, but the exchange does not sign it and the PEP
does not reopen it.

## Authorization Lease

Only an ALLOW receipt can become `kaching.authorization.v1`. The default lease
lasts 30 seconds and contains:

- canonical origin, action, resource and requested amount;
- intended audience;
- decision ID and maximum authorized amount;
- intent, policy and observation hashes;
- issue/expiry timestamps and random nonce;
- issuer public-key fingerprint;
- Ed25519 signature.

The issuer private key is generated at
`~/.config/kaching/issuer-ed25519.pem` by default. It is an unencrypted PKCS#8 PEM
protected by directory/file permissions (`0700`/`0600` where supported). Of key
material, only the public key and fingerprint are returned to the browser. The
signed lease itself is also returned and displayed; it is not treated as secret
in this non-executing demo.

### Fixture/live trust limitation

Fixture and live ALLOW decisions currently use the same issuer and verifier, and
the lease does not encode observation mode. A fixture ALLOW therefore produces a
cryptographically valid demo lease. This is acceptable only because the PEP has
no execution capability. A production design must disable fixture issuance in
the production trust domain and use separate keys/configuration so fixture
authority can never reach a financial executor.

## Local enforcement verifier

After validating schema and trusted issuer fingerprint, the verifier validates
the Ed25519 signature before evaluating signed claims. It then checks:

1. validity window, with up to five seconds of future clock-skew tolerance;
2. current code-configured policy hash;
3. exact audience;
4. exact resource, origin, action and requested amount;
5. canonical intent SHA-256;
6. positive authorization ceiling not below the request;
7. optional nonce consumption through a bounded in-memory replay cache.

The verifier does **not** refresh account, market or exchange state; authenticate
the proposer; reserve funds; aggregate multiple leases; revalidate the observation
commitment; or revoke an earlier unexpired lease when a new decision is compiled.
Multiple independently issued leases may coexist until expiry.

`consume=false` is the API default and supports repeatable previews. When
`consume=true`, the nonce is recorded in a 512-entry process-local cache. The
cache is neither durable nor distributed and may evict an unexpired entry under
capacity pressure. The replay demonstration is therefore bounded evidence, not a
production one-time-use guarantee.

## Local HTTP API

| Endpoint | Purpose |
|---|---|
| `GET /api/state` | Current sanitized receipt, signed lease, public issuer data and stage ledger. |
| `POST /api/compile` | Native proposal compilation. |
| `POST /access/v1/evaluation` | AuthZEN-inspired Subject / Action / Resource / Context mapping. |
| `POST /api/verify` | Receipt comparison with a retained original digest. |
| `POST /api/enforce` | Signed-lease verification against a proposed exact action. |
| `POST /api/arena` | Five deterministic policy/evidence attacks. |
| `POST /api/enforcement-arena` | Seven deterministic authorization-bypass checks. |

The HTTP server binds to `127.0.0.1`. It requires the exact loopback Host header,
rejects disallowed Origin and `Sec-Fetch-Site: cross-site`, accepts JSON-only POST
bodies up to 16 KiB, rejects duplicate object keys and non-standard numeric
constants, constrains static serving to built assets, and sends CSP, no-store,
nosniff and no-referrer headers.

This bridge has no TLS, caller authentication or authenticated agent identity.
Origin-less local clients are accepted. In `--live` mode, any accepted loopback
caller can trigger read-only CLI/REST observations; run it only in a trusted local
session.

## Volatile state

Receipt anchors, the current receipt/lease, replay entries and the decision ledger
are memory-only and reset on process restart. The anchor collection holds at most
100 decisions. The ledger holds at most 70 compiler-stage rows and is not a
durable security audit log; HTTP and enforcement attempts are not recorded there.

## UI authority state

The React/TypeScript Command Deck presents authentication availability separately
from authorization. Editing an ALLOW proposal produces a new draft, immediately
hides the prior visible lease and disables its UI enforcement controls until the
draft is recompiled. The server-side verifier still relies on lease contents, not
UI visibility, and a previously issued unexpired lease is not revoked.

The visual system is independent of authorization semantics. Current browser QA
locks the dark cool-green palette, localized holographic prism, absence of the
rejected shard element, responsive layout and stale-visible-authority behavior.

## Non-execution boundary

There is no browser route for order-test, live order placement, transfer,
withdrawal, credential retrieval or policy mutation. The legacy CLI can invoke
Binance `order-test`, a non-executing validation call, only after an ALLOW receipt;
it is not exposed through the browser or PEP. No code path in this repository
places a live order.
