# KACHING! — Binance Agent OS Track A handoff

**Before an AI can touch money, it must carry proof.**

Public source: [am-selenephos/KACHING](https://github.com/am-selenephos/KACHING)

This file is prepared submission copy. It does not prove that an X post, video
upload, survey, contest entry or deployment has occurred. Confirm those actions
with their real public URLs or receipts before marking the entry complete.

## One-line description

KACHING! turns an AI agent's untrusted financial proposal into BLOCK, REVIEW or
an exact-action Ed25519 authorization lease—then rejects changed or replayed
authority before any execution capability is involved.

## Submission description

AI agents can analyze markets and call financial tools, but capability is not
authorization. A model holding a plausible instruction—or even credentials—does
not prove that a specific action is permitted under current policy and evidence.
The missing layer is an inspectable boundary between proposal and execution.

KACHING! is that boundary. It accepts an untrusted financial intent, observes
account/market state, checks a partial Binance exchange contract, compiles
code-configured policy and calculates a Decimal safe-action envelope. The result
is one of three explicit verdicts. BLOCK and REVIEW authorize zero. Only ALLOW
can issue a short-lived Ed25519 Authorization Lease bound to the exact origin,
action, resource, amount, tool audience, policy hash and observation commitment.

The local Enforcement Lab proves the distinction. Present the exact signed action
and the verifier returns VALID. Change the amount, resource, audience, signature
or policy; use expired authority; or replay a consumed lease, and it returns a
specific rejection reason. The deterministic demo reports 5/5 policy/evidence
attacks contained and 7/7 authorization bypasses rejected. Receipt tampering is
also checked against a process-retained original digest.

KACHING! is deliberately non-executing. The browser and logical PEP place no
order, transfer or withdrawal. Offline fixtures are clearly labeled, while an
optional local `--live` mode performs read-only observations. The interface makes
the trust transition visible: raw agent authority is NONE; REVIEW is not silent
approval; and an edited draft immediately loses its displayed lease until it is
recompiled.

This is a bounded hackathon prototype, not a production financial control.
Fixture/live leases currently share a demo trust root, replay state is local and
memory-only, and enforcement does not refresh balances or reserve funds. Those
limits are documented because proof-carrying authorization is useful only when its
trust boundary is honest.

## Judge fast path

1. Clone the public repository and follow [Run locally](README.md#run-locally).
2. Open `http://127.0.0.1:8890`.
3. Select **Run judge demo**.
4. Observe BLOCK and REVIEW returning zero authority.
5. Observe the ALLOW fixture issuing a 30-second Ed25519 lease.
6. Open Enforcement Lab: exact action → VALID.
7. Run the bypass gauntlet: 7 / 7 → REJECTED.
8. Read the [verification record](docs/VERIFICATION.md) and
   [security boundary](SECURITY.md).

The deterministic fixtures require no exchange credentials and never place a
trade.

## What is actually verified locally

| Evidence | Result |
|---|---|
| Python regression | 77 / 77 passed |
| UI unit cases | 8 / 8 passed |
| Policy/evidence attacks | 5 / 5 contained |
| Authorization bypasses | 7 / 7 rejected; baseline VALID |
| Rendered Chromium QA | 26 / 26 checks passed |
| Responsive QA | 20 / 20 workspace/viewport combinations passed |
| Browser console/network record | 0 relevant console entries; 0 failed requests |
| Final screenshots | 7 local 1920×1080 captures, each SHA-256 pinned |
| Final demo MP4 | 98.0s, H.264, 1920×1080, SHA-256 pinned |
| Public release-safety scan | PASS |

These are point-in-time local results tied to the hashes in
[`docs/browser-qa.json`](docs/browser-qa.json). Cloud CI, remote SHA equality and external submission actions have separate statuses in
[VERIFICATION.md](docs/VERIFICATION.md).

## Technical highlights

- Seven-stage policy path: Normalize → Observe → Verify evidence → Compile policy
  → Safe envelope → Authorize → Attest.
- Exact-action Ed25519 lease with a 30-second default TTL.
- Canonical JSON and Decimal normalization for policy-relevant identity.
- Server-retained digest anchors prevent a caller from merely resealing a modified
  receipt.
- Read-only Binance CLI account adapter, public Spot market fallback and partial
  `exchangeInfo` contract checks.
- Host/Origin/Fetch Metadata guard, bounded JSON, duplicate-key rejection, CSP and
  constrained static serving on `127.0.0.1`.
- Browser-visible stale-authority revocation after proposal edits.
- Reproducible offline judge fixtures, seven final evidence captures and a
  machine-readable browser QA record.

## Demo assets

| Item | Repository location | Status source |
|---|---|---|
| Recording plan | [DEMO_SCRIPT.md](DEMO_SCRIPT.md) | Fixed 98-second shot plan |
| Final MP4 | [`docs/demo/KACHING-98s.mp4`](docs/demo/KACHING-98s.mp4) | PASS locally: 98.0s, H.264, 1920×1080; hash in VERIFICATION.md |
| Seven screenshots | [DEMO.md](DEMO.md#required-screenshots) | Hashes in VERIFICATION.md and browser QA JSON |
| Architecture | [ARCHITECTURE.md](ARCHITECTURE.md) | Exact logical trust boundary |
| Security model | [SECURITY.md](SECURITY.md) | Limitations and production gaps |
| Copy-paste form | [docs/SUBMISSION_COPY.html](docs/SUBMISSION_COPY.html) | Local handoff artifact |

## Recommended X copy

```text
Track A: KACHING! turns untrusted AI financial intent into BLOCK, REVIEW, or an exact-action Ed25519 lease. Exact action: VALID. Seven bypasses: REJECTED. No live execution. #AgentOS
https://github.com/am-selenephos/KACHING
```

Attach the final video through the official client. Check the final composer if
adding mentions, wording or another URL. Do not claim that this copy has been
posted without the real post URL.

### Short backup

```text
KACHING! Capability is not authorization. Only ALLOW issues a signed exact-action lease. BLOCK and REVIEW issue zero. Seven bypasses rejected. No live execution. #AgentOS
https://github.com/am-selenephos/KACHING
```

## External entry handoff

The project notes record these official references:

- [Binance hackathon instructions](https://www.binance.com/en/blog/community/8802181509900814931)
- [Binance announcement on X](https://x.com/binance/status/2094810011557838988)
- [Official Binance survey](https://www.binance.com/en/survey/2913aa200aac462c89a737779393f3d4)

The previously recorded deadline was September 8, 2026 at 23:59 UTC. This
repository does not independently establish current eligibility, an extension or
late-entry availability. The owner must inspect the official surfaces while
signed in and retain actual confirmation.

Required owner-controlled evidence before saying “submitted”:

- [ ] final video uploaded and its public/unlisted URL recorded;
- [ ] official X reply or quote-post published with the video and repository URL;
- [ ] final X post URL recorded;
- [ ] official survey completed while signed in;
- [ ] survey confirmation/receipt observed and retained privately;
- [ ] any required follow/repost conditions completed;
- [ ] no Binance UID or private account data placed in the public post.

No checked box should be inferred from a prepared document.

## Claim limits judges should know

- The evaluation endpoint is AuthZEN-inspired, not formally conformant.
- The receipt digest is local integrity evidence; the lease is the Ed25519-signed
  object.
- Fixture and live ALLOW decisions currently share one demo issuer/verifier, and
  the lease does not encode mode.
- Enforcement does not refresh Binance state, reserve funds, aggregate spend or
  revalidate the observation commitment.
- Multiple unexpired leases may coexist; compiling a new proposal does not revoke
  an older lease.
- Replay rejection is opt-in consuming mode with a bounded process-local cache.
- Caller/subject identity labels are not authenticated.
- The PEP is a logical verifier in the same trusted local process.
- The signed lease is KACHING! authority, not a Binance-native token or Binance
  endorsement.
- No browser or PEP live execution path exists.
- ALLOW does not guarantee exchange acceptance, profit or general security.

## Release status

Local product evidence and rendered QA are green. Final release status remains
governed by [VERIFICATION.md](docs/VERIFICATION.md): final clean-tree regression,
push, local/remote SHA equality, cloud-CI recheck and owner
submission evidence must not be inferred from this copy.
