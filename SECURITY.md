# KACHING! security boundary

KACHING! is a local hackathon/research authorization prototype. It is not a
certified financial control, custody system, security guarantee, legal
authorization instrument or promise against loss.

## Demonstrated guarantees

Within the tested local process and stated assumptions:

- BLOCK and REVIEW authorize zero and issue no lease.
- Only ALLOW can issue an Ed25519-signed Authorization Lease.
- The verifier binds the lease to exact origin, action, resource, requested
  amount, intended audience, policy hash, observation commitment, issuer, nonce
  and validity window.
- Changed amount, resource, audience, signature or policy is rejected.
- An expired lease is rejected; issuance more than five seconds in the future is
  rejected.
- A second consuming verification is rejected while its nonce remains in the
  process-local replay cache.
- Receipt changes fail against the process-retained original digest.
- Missing/malformed policy inputs and observations fail closed in tested paths.
- The browser and logical PEP have no order, transfer or withdrawal method.

The 5/5 policy/evidence suite and 7/7 authorization-bypass suite are bounded,
deterministic demonstrations. They are not a penetration test, formal
verification or security certification.

## Hard execution boundary

- The browser, authorization issuer, verifier and Enforcement Lab do not place
  live orders, transfers or withdrawals.
- The legacy CLI can invoke Binance `order-test`, which is a non-executing
  validation call, only after ALLOW.
- The local PEP returns VALID or a rejection reason; it does not forward an action
  to Binance.

VALID therefore means “accepted by this local KACHING! verifier,” not “executed,”
“accepted by Binance,” or “profitable.”

## Critical fixture/live separation limitation

Fixture and live ALLOW decisions currently share the same Ed25519 issuer and
trusted verifier. The signed lease does not encode whether its observations were
fixture or live. Consequently, the deterministic ALLOW fixture produces a valid
cryptographic lease accepted by the demo PEP.

This is safe only inside the current non-executing demonstration. **Do not connect
this issuer/verifier configuration to a real execution capability.** A production
design must disable fixture issuance in the production environment and separate
fixture/live keys, configuration and trust roots.

## Enforcement is not a fresh risk decision

At enforcement time, KACHING! validates the signed lease, proposed action, current
code-configured policy hash and local clock. It does not:

- refresh Binance account balances or trading permission;
- refresh price, depth or exchange-contract state;
- reopen or independently attest the observation commitment;
- reserve funds or maintain a cumulative-spend budget;
- coordinate concurrent financial actions;
- revoke older unexpired leases after a new compilation;
- require the presented lease to equal the UI's current lease.

Market/account conditions may change during the 30-second default lease window,
and multiple independently issued leases may coexist. The safe envelope is a
per-decision bound, not reserved capital.

## Replay limitation

`/api/enforce` defaults to non-consuming preview mode, and the caller chooses
whether `consume=true`. Preview validation can repeat while a lease remains valid.

Consuming mode uses a 512-entry, process-local, memory-only cache. Restart clears
it, separate verifier processes do not share it, and capacity pressure may evict
an unexpired nonce. The replay test proves the intended behavior in one bounded
process; it does not establish durable or distributed exactly-once execution.

## Credentials and account privacy

- Binance credentials remain in the owner's Binance CLI configuration and are not
  stored in the repository.
- API keys, secrets, UID, cookies, authorization headers, raw CLI diagnostics and
  CLI profile files are not returned in browser DTOs.
- Live public receipts omit balances and the exact balance-derived safe envelope,
  because the bound itself may disclose account information.
- The CLI writes private evidence through exclusive file creation at mode `0600`;
  its default private-evidence filename patterns are blocked by the release audit.
- A credential exposed outside secure local storage must be revoked and replaced.

`--live` permits any accepted loopback caller to trigger authenticated read-only
CLI observations. Enable it only in a trusted local session, close the server
afterward, and never expose the port beyond loopback.

## Issuer key

The default issuer key lives at
`~/.config/kaching/issuer-ed25519.pem`. The application attempts to restrict its
directory to `0700` and forces the file to `0600`. The private key is not stored in
the repository, serialized into a lease or returned to the browser.

The key is an **unencrypted PKCS#8 PEM** protected only by operating-system file
permissions. This prototype has no passphrase, HSM, hardware-backed isolation,
key rotation workflow or revocation distribution. Anyone who obtains the private
key can forge leases trusted by that verifier.

Of issuer key material, the browser receives only the public key and SHA-256
fingerprint. It also receives the complete signed lease. That is acceptable for a
non-executing demo, but an executable bearer-capability design would need
authenticated delivery and least-disclosure state APIs.

## Evidence boundary

The public decision receipt carries a SHA-256 digest checked against a locally
retained original. It is not a signature. The separate Authorization Lease is
signed with Ed25519 and carries issuer authentication.

The observation commitment is a salted hash of locally assembled intent, policy,
market/account snapshots and private nonce. It binds local records and reduces
balance-guessing risk; it is not Binance-signed attestation, proof of transport
origin to a third party, or proof that observations remain fresh at enforcement.

Receipt anchors, the current decision and lease, the replay cache and stage ledger
are volatile. Restart removes them. At most 100 receipt anchors and 70 stage-ledger
rows are retained. The ledger records compiler stages, not HTTP/enforcement events,
and is not a durable security audit log.

## Exchange-contract boundary

The `exchangeInfo` adapter checks symbol, status, MARKET support,
`quoteOrderQtyMarketAllowed`, freshness and applicable notional bounds. It does not
implement every exchange filter or permission, including the complete lot-size,
price and asset-rule surface. Passing these checks cannot guarantee Binance will
accept an order.

## Local HTTP boundary

The server binds to `127.0.0.1` and enforces:

- exact loopback Host;
- no disallowed Origin;
- rejection of `Sec-Fetch-Site: cross-site`;
- JSON-only POST requests up to 16 KiB;
- rejection of duplicate JSON keys and non-standard numeric constants;
- constrained static paths;
- CSP, `no-store`, `nosniff` and `no-referrer` response headers.

The bridge has **no TLS or caller authentication**. Origin-less local programs are
accepted. Subject type, origin and agent/human labels are caller assertions, not
authenticated identities. This is a trusted single-user loopback application, not
an authenticated multi-tenant service. Local malware or another process running
with the user's privileges is outside the threat model.

## Fundamental bypass

KACHING! cannot prevent independent software from bypassing it when that software
separately holds usable Binance credentials. Strong financial enforcement requires
the credential/tool capability to be reachable only through a reviewed, isolated
PEP or equivalent control plane.

## Minimum production work

Before any real financial executor is considered, at minimum:

1. remove fixture issuance from the production trust domain;
2. separate PDP, issuer and PEP services and identities;
3. authenticate callers and subject/workload identities;
4. use hardware-backed keys with rotation and revocation;
5. implement durable, shared replay and idempotency state;
6. reserve/aggregate financial exposure across concurrent leases;
7. revalidate current account, market and complete exchange constraints at the
   actual execution boundary;
8. produce durable tamper-evident security audit logs;
9. threat-model, test and independently review the integrated executor.

## Responsible demo use

Use deterministic fixtures for adversarial demonstrations and keep them visibly
labeled. Keep withdrawals and transfers disabled. Never record API Management,
profile files, private evidence, UID, keys or balances. Do not describe the demo
as live execution, Binance endorsement, formal AuthZEN conformance or a universal
security solution.
