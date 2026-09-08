# KACHING! — Binance Agent OS Track A submission

Public branch: https://github.com/am-selenephos/evidencebound-runtime/tree/hackathon/binance-agent-os-tradegate

## Entry requirements checked September 8, 2026

The official Binance Agent OS Mini Hackathon announcement states the deadline is
**September 8, 2026, 23:59 UTC** — **September 9, 04:59 PKT**.

For Track A: follow `@Binance`, repost the official announcement, then reply or
quote-repost with the Track A demo/video and GitHub link, and complete the official
survey. The owner must perform these account-specific actions. Keep any requested
Binance UID inside the official form; never place it in the public post.

No social post or survey is marked submitted by the repository itself.

## Recommended X post

```text
Track A — KACHING! Capability ≠ authorization. Binance state + exchange rules + deterministic policy → ALLOW/REVIEW/BLOCK. ALLOW issues a 30s Ed25519 lease for exact action. Mutated, expired or replayed authority is rejected. No live execution. #AgentOS
https://github.com/am-selenephos/evidencebound-runtime/tree/hackathon/binance-agent-os-tradegate
```

Post text is 253 raw characters before the URL; using X's conventional shortened
URL length of 23 characters gives an approximate weighted count of **277**. Verify
in X's composer before posting. Attach the demo video to the same reply/quote.

## Shorter backup

```text
Track A — KACHING! Before an AI can touch money, it must carry proof. Deterministic Binance authorization + a short-lived Ed25519 lease. Change the action, tool, policy, signature, time window or replay state and authority is rejected. No live execution. #AgentOS
```

Add the public GitHub branch link and verify the final count in X's composer.

## What the demo should prove

1. real read-only Binance market/account observation and current exchange-contract
   evidence, without exposing private balance or credentials;
2. BLOCK/REVIEW return zero authority and no lease;
3. ALLOW issues `kaching.authorization.v1`, signed with Ed25519;
4. the exact signed action verifies VALID at the local PEP;
5. amount escalation, resource mutation, audience mutation, signature forgery,
   policy drift, expiry and consumed-lease replay are rejected;
6. neither the PEP nor browser has a live execution route.

## Positioning

KACHING does **not** compete with signal bots, strategy agents, news agents or
portfolio copilots. Those systems can be proposers. KACHING is the action-level
authorization boundary beneath them.

The central line is:

> **Capability is not authorization.**

Binance/tool credentials may grant capability. KACHING determines whether this
particular action is authorized under the observed state and policy, then issues
portable KACHING authorization evidence only on ALLOW.

## Claim limits

- `POST /access/v1/evaluation` is **AuthZEN-inspired**, not formal conformance.
- A KACHING Authorization Lease is not a Binance-native token or endorsement.
- The Ed25519 lease provides issuer-authenticated KACHING authorization evidence;
  it does not stop unrelated software that independently holds Binance credentials.
- Replay protection is bounded and in-memory in this hackathon build.
- ALLOW does not guarantee exchange acceptance, price, profit or safety.
- The browser and PEP contain **no live execution path**.

Use the latest `docs/VERIFICATION.md` record for test/browser/live-proof claims.
