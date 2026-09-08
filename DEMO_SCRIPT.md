# KACHING! — 96-second recording script

Use the verified metallic-gold production build at 1440×900 or 1920×1080.
The shot durations below total **96 seconds**; the actual export duration belongs
in [VERIFICATION.md](../docs/VERIFICATION.md). This document is a recording plan,
not evidence that a video has already been captured.

## Shot list

| Time | Actual UI action / evidence | Required source label |
|---|---|---|
| 00–08 | Command deck; show agent origin, BUY BNBUSDT, 10.00 USDT proposal, untrusted message and RAW AGENT AUTHORITY: NONE. | DETERMINISTIC FIXTURE |
| 08–18 | Hold the AuthN/AuthZ distinction and the seven-stage compiler. Read “Capability is not authorization.” | DETERMINISTIC FIXTURE |
| 18–30 | Show read-only Binance observation, account-authentication status and current exchange-contract check. Keep private account values absent. | LIVE / READ-ONLY only for a current read; otherwise RECORDED LIVE EVIDENCE plus its original timestamp. |
| 30–42 | Compile the BLOCK fixture. Hold BLOCK, determining rule IDs, 0.00 USDT authorized and no lease. | DETERMINISTIC FIXTURE |
| 42–52 | Select REVIEW, compile 100.00 USDT, and show the 24.37 USDT envelope. A revised draft still needs recompilation. | DETERMINISTIC FIXTURE |
| 52–65 | Select ALLOW, compile 10.00 USDT and show the new Ed25519 Authorization Lease, ≤10.00 USDT ceiling, audience, policy, issuer fingerprint and running countdown. | DETERMINISTIC FIXTURE / LOCAL SIGNATURE |
| 65–76 | Open Enforcement Lab; present the exact action while the displayed lease is valid. Hold VALID. Show +0.01 USDT mutation and ACTION_MISMATCH if pacing allows. | DETERMINISTIC FIXTURE / LOCAL VERIFIER |
| 76–88 | Select RUN SEVEN BYPASSES. Hold baseline VALID, 7/7 rejected and all seven deterministic reasons. | DETERMINISTIC AUTHORIZATION FIXTURE |
| 88–96 | Final KACHING! hero: “BEFORE AN AI CAN TOUCH MONEY, IT MUST CARRY PROOF.” Keep “No live execution path” visible. | NO LIVE EXECUTION |

Recompile ALLOW before each take; a 30-second lease must remain valid when the
exact-action check is recorded. The gauntlet mints its own fixture lease and
tests time validity using an injected verifier clock. It is not an attack on
Binance and does not submit a trade.

If live footage is unavailable, the 18–30-second shot may show the existing
sanitized live observation record with its date and an explicit **RECORDED LIVE
EVIDENCE — VERIFICATION RECORD** label. Use “The recorded Binance observation…”
in the voiceover. If neither a usable capture nor a dated record is available,
label the sequence **OFFLINE FIXTURE DEMO** and describe the integration as a
capability, without saying that the fixture is live.

## Voiceover

> AI agents can now reach financial infrastructure.
>
> But capability is not authorization.
>
> This agent proposes a financial action. KACHING! treats that proposal as untrusted.
>
> It reads Binance state, checks exchange rules, compiles deterministic policy,
> and calculates the safe-action envelope.
>
> BLOCK and REVIEW issue no authority. A revised request must be compiled again.
>
> Only ALLOW issues a short-lived Ed25519 authorization lease, bound to that exact
> action, resource, amount, policy, evidence and target tool.
>
> Present the exact action and the local enforcement boundary validates it.
>
> Change the amount, symbol, audience or signature; let authority expire; change
> policy; or replay consumed authority — and KACHING! rejects it.
>
> No live trade is placed.
>
> Models may propose. Policy authorizes.
>
> Before an AI can touch money, it must carry proof.
>
> KACHING.

Read at a measured pace with pauses over the receipt, lease and rejection results.
Keep the final export between 80 and 100 seconds. The source-specific wording
above takes precedence over the generic Binance-state sentence.

## Evidence distinctions to retain in the edit

- SHA-256 verifies receipt integrity against a retained original; Ed25519 signs
  the separate authorization lease.
- A safe envelope is a bound, not an automatic amount change or authorization.
- Exact-action VALID verifies KACHING! authority; it is not exchange execution.
- Replay rejection is a consuming-mode check using bounded, local in-memory state.
- Five policy attacks and seven authorization bypasses are different suites.
- Judge Mode contains seven real server-backed scenes and ends at Enforcement Lab.

Launch instructions and the seven screenshot paths are in [DEMO.md](../DEMO.md).
