# KACHING! security boundary

KACHING is a hackathon/research authorization kernel, not a certified financial
control, custody system, security guarantee or promise against loss.

## Hard execution boundary

- There is **no live order-placement, transfer or withdrawal path** in the browser,
  authorization issuer, verifier or Enforcement Lab.
- The preserved CLI can call Binance `order-test`, which is non-executing and is
  gated behind ALLOW. REVIEW and BLOCK cannot reach order-test.
- The local PEP verifies KACHING authorization evidence only; it never forwards an
  action to Binance.

## Credentials and private account state

- Binance credentials remain under the owner's existing Binance CLI configuration.
- API keys, secrets, UID, cookies, authorization headers, raw CLI diagnostics and
  profile files are never returned in browser DTOs.
- Live public receipts omit balances and exact balance-derived safe envelopes. A
  balance-constrained envelope can itself disclose sensitive account information.
- Private evidence files use exclusive creation with `0600` permissions and are
  blocked/ignored by the release audit.
- Credentials exposed outside secure local storage must be revoked and replaced.

## Ed25519 issuer key

ALLOW-only authorization leases are signed by a local Ed25519 issuer. The default
private-key path is under `~/.config/kaching/`; its directory is restricted where
possible and the key file is forced to mode `0600`. The private key is not stored
in the repository, not serialized into leases and not sent to the browser.

The public key and SHA-256 fingerprint are intentionally public verification
material. Anyone who obtains the private issuer key can forge KACHING leases for
that issuer; key compromise therefore requires replacing the key and treating old
leases as untrusted. This hackathon build does not implement hardware-backed keys,
key rotation infrastructure or revocation distribution.

## Exact-action authorization

The signed lease binds origin, action, resource/symbol, requested amount, intended
audience/tool, policy hash, observation commitment, issuer identity, nonce and
short validity window. The verifier checks the Ed25519 signature before relying on
those claims.

Rejected conditions include:

- changed action or amount;
- changed resource;
- changed audience;
- invalid/forged signature;
- wrong issuer;
- expired/not-yet-valid lease;
- changed current policy hash;
- amount above the signed authorization ceiling;
- replay after a locally consumed lease.

Replay consumption is an **in-memory, single-process** demonstration. Restarting
the process loses the replay cache. It is not distributed replay protection.

## Evidence and policy boundary

- Browser callers cannot submit policy or account observations.
- Natural-language metadata has no policy-setting authority.
- Missing authentication, disabled trading permission, invalid/stale market state,
  invalid/stale exchange-contract state and malformed numeric values fail closed.
- Exchange metadata is public read-only Binance state and is not an execution call.
- The public receipt's SHA-256 identifies decision integrity against the locally
  retained original. The **lease**, not the receipt checksum, carries issuer
  authentication via Ed25519.

## Local HTTP boundary

The server binds `127.0.0.1` by default and rejects unexpected Host/Origin,
cross-site Fetch Metadata, duplicate JSON keys, non-standard numeric constants,
non-JSON POSTs and bodies above 16 KiB. Responses use no-store, CSP, nosniff and
no-referrer headers. Static serving is constrained to the built UI assets.

This is a trusted single-user loopback application, not an authenticated
multi-tenant service. Local malware or another process with the user's privileges
remains outside this threat model.

## Fundamental limitation

KACHING cannot prevent software from bypassing it when that software separately
holds usable Binance credentials. Strong production enforcement would require the
financial credential/tool capability to be exclusively reachable through a
reviewed PEP or equivalent infrastructure.

The KACHING lease is not a Binance-native capability, not Binance endorsement, not
formal AuthZEN conformance, not a legal authorization instrument, and not proof an
exchange will accept or profit from an order.

## Responsible demo use

Keep withdrawals/transfers disabled. Use least-privilege credentials. Never show
API Management, profile files, private evidence, UID or balances in the recording.
Use deterministic fixtures for adversarial demonstrations and label them as such.
