# KACHING! — Binance Agent OS Track A submission

**Before an AI can touch money, it must carry proof.**

Public source: [am-selenephos/KACHING](https://github.com/am-selenephos/KACHING)


The standalone repository is the submission artifact. The [verification record](docs/VERIFICATION.md)
contains the final source/build identifiers, actual test and browser results,
captured assets, PR state and CI status. This document does not establish that an
entry has been posted or a survey submitted.

## Entry requirements checked September 8, 2026

The official deadline is **September 8, 2026, 23:59 UTC**, which is **September 9,
04:59 PKT**. Track A entry requires following @Binance and reposting the announcement,
replying or quote-reposting with the submission video/demo and GitHub link where
applicable, and completing the survey. [Official Binance hackathon instructions](https://www.binance.com/en/blog/community/8802181509900814931)

- [Official announcement](https://x.com/binance/status/2094810011557838988)
- [Official survey linked by Binance](https://www.binance.com/en/survey/2913aa200aac462c89a737779393f3d4)

The owner must perform those account-specific actions. Eligibility and participation
remain subject to the official terms. Keep any requested Binance UID inside the
official form and absent from the public post.

The public survey page did not expose field labels during this documentation
check. No survey fields, selection, completion state or submission receipt are
inferred. A logged-in form must be inspected separately before reporting its exact
labels. Nothing is posted or submitted by this package.

## Recommended X post

```text
Track A — KACHING! Capability ≠ authorization. Binance state + exchange rules + deterministic policy → ALLOW/REVIEW/BLOCK. ALLOW issues a 30s Ed25519 lease for exact action. Mutated, expired or replayed authority is rejected. No live execution. #AgentOS
https://github.com/am-selenephos/KACHING
```

**Estimated weighted count: 279 / 280**, including the newline and branch URL.
The prose has 253 Unicode characters but a weight of 255: ≠ and → each count as
two. Add one for the newline and 23 for the shortened URL. Attach the video in
the same reply or quote-repost.

## Shorter backup

```text
Track A — KACHING! AI proposes. Policy authorizes. Binance state + exchange rules → ALLOW/REVIEW/BLOCK. ALLOW alone issues an Ed25519 lease. Exact action: VALID. Seven bypasses: REJECTED. No live execution. #AgentOS
https://github.com/am-selenephos/KACHING
```

**Estimated weighted count: 240 / 280**, including the newline and branch URL.
The prose weight is 216; newline plus shortened URL adds 24. These counts apply
to the exact copy above. Check the final composer if adding mentions, wording or
another URL. Attached media through the official client carries no text weight.
[X character-counting rules](https://docs.x.com/fundamentals/counting-characters),
[official twitter-text weight configuration](https://github.com/twitter/twitter-text/blob/master/config/v3.json)

## Submission package

| Item | Source / evidence |
|---|---|
| Public runnable source | Hackathon branch linked above; install and launch in [README](README.md#run-kaching). |
| Video | [96-second shot list and voiceover](DEMO_SCRIPT.md); actual captured path and duration in the verification record. |
| Seven final screenshots | [Capture index](DEMO.md#required-screenshots): command deck, BLOCK, REVIEW envelope, ALLOW lease, exact enforcement, seven bypasses, receipt tamper. |
| Authorization explanation | [Architecture](ARCHITECTURE.md) and [security boundary](SECURITY.md). |
| Evidence of checks | [VERIFICATION.md](docs/VERIFICATION.md), including local results and actual CI availability. |
| Public entry | Owner's reply/quote-repost with video/demo and branch URL; do not mark submitted without its real URL. |
| Survey | Owner's official form; do not mark submitted without observed confirmation. |

## What judges should see

1. A financial proposal is untrusted; raw agent authority is NONE.
2. Read-only Binance account/market observation and current exchange-contract
   checks inform deterministic policy. Recorded evidence carries its actual date;
   fixtures remain clearly labeled.
3. BLOCK and REVIEW issue zero authority and no lease. REVIEW shows a precise
   safe envelope and requires a new compilation after revising the request.
4. ALLOW issues `kaching.authorization.v1`, signed with Ed25519 and bound to the
   exact action, resource, amount, audience, policy and observation commitment.
5. The exact signed action verifies VALID. Seven deterministic bypass cases
   return their specific rejection reasons.
6. Neither the browser nor the local enforcement endpoint places a live trade.

Trading, strategy, news and portfolio agents can all be proposers. KACHING! is the
action-level authorization boundary: **LLMs propose. KACHING! authorizes.**

## Claim limits

- The evaluation endpoint is AuthZEN-inspired; no formal conformance is claimed.
- The receipt checksum verifies retained-original integrity; the separate lease
  provides Ed25519 issuer authentication.
- The signed lease is KACHING! authority, not a Binance-native token, endorsement
  or legal financial instrument.
- Replay rejection is demonstrated in consuming mode with a bounded process-local
  cache; it is not distributed or persistent, and preview checks are non-consuming.
- Observation commitment is signed evidence binding, not a fresh account read by
  the enforcement verifier.
- The boundary does not control independent software holding Binance credentials.
- ALLOW does not guarantee exchange acceptance, profit or universal security.
- Five policy attacks and seven bypass tests are bounded demonstrations.
- No browser or PEP live execution path exists.

Submission readiness requires actual final-build regression and Chromium checks,
seven final captures, a measured video asset, public audit, pushed source and an
updated PR. GitHub CI needs a real run; an account-level Actions block remains
**UNVERIFIED**, even when local gates pass.
