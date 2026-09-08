# KACHING! — 98-second recording script

Use the final Prismatic Emerald Glass production build at 1440×900 or 1920×1080:
cool green glass, pale metallic-gold display lettering, mint operational text and prismatic
edge refraction. The shot plan totals **98 seconds**. The export path is
[docs/demo/KACHING-98s.mp4](docs/demo/KACHING-98s.mp4); its measured duration,
source build and actual QA status are recorded in
[VERIFICATION.md](docs/VERIFICATION.md). This script alone is not capture evidence.

## Shot list

| Time | Actual UI action / evidence | Required source label |
|---|---|---|
| 00–08 | KACHING! hero: “Before an AI can touch money, it must carry proof.” | OFFLINE FIXTURE DEMO |
| 08–18 | Command deck; show an untrusted proposal and RAW AGENT AUTHORITY: NONE. | DETERMINISTIC FIXTURE |
| 18–30 | Compile policy through the seven visible stages. Keep account/evidence provenance clear. | DETERMINISTIC FIXTURE |
| 30–40 | Hold BLOCK, determining rule IDs, 0.00 USDT authorized and no lease. | DETERMINISTIC FIXTURE |
| 40–52 | Compile REVIEW at 100.00 USDT; show the 24.37 USDT envelope and zero authority. A revised draft still needs recompilation. | DETERMINISTIC FIXTURE |
| 52–66 | Compile ALLOW at 10.00 USDT; show the Ed25519 Authorization Lease, ≤10.00 USDT ceiling, audience, policy, issuer fingerprint and running countdown. | DETERMINISTIC FIXTURE / LOCAL SIGNATURE |
| 66–76 | Open Enforcement Lab and present the exact action while the lease is valid. Hold VALID. Show +0.01 USDT mutation and ACTION_MISMATCH if pacing allows. | DETERMINISTIC FIXTURE / LOCAL VERIFIER |
| 76–90 | Run seven bypasses. Hold baseline VALID, 7/7 rejected and the deterministic rejection reasons. | DETERMINISTIC AUTHORIZATION FIXTURE |
| 90–98 | KACHING! hero: “CAPABILITY ≠ AUTHORIZATION.” “LLMs propose. KACHING! authorizes.” | NO LIVE EXECUTION |

Recompile ALLOW before each take; a 30-second lease must remain valid when the
exact-action check is recorded. The gauntlet mints its own fixture lease and
tests time validity using an injected verifier clock. It does not submit a trade
or change the system clock.

The edit must be understandable muted: keep the verdict, authorized amount,
lease state and rejection reason readable. Preserve the server's actual outputs;
do not turn a fixture into a live observation through captions or voiceover.

## Voiceover

> Before an AI can touch money, it must carry proof.
>
> AI agents can reach financial infrastructure. Capability is not authorization.
>
> This agent proposes a financial action. KACHING! treats it as untrusted.
>
> These local fixtures demonstrate the policy pipeline: observe evidence, verify
> exchange rules, compile deterministic policy, and calculate a safe-action envelope.
>
> BLOCK issues zero authority. REVIEW also issues zero authority: one hundred
> requested, twenty-four thirty-seven admissible. A revised draft needs a new decision.
>
> Only ALLOW issues a short-lived Ed25519 Authorization Lease. It binds this exact
> action, resource, amount, audience, policy and evidence.
>
> Present the exact action and the local enforcement boundary returns VALID.
>
> Change the amount, resource, audience or signature; change policy; let authority
> expire; or replay consumed authority — the verifier rejects the attempt.
>
> Seven tested bypasses. Seven rejected. No live trade is placed.
>
> LLMs propose. KACHING! authorizes.

Use a measured pace and deliberate pauses over the lease and rejection results.
Keep the final export between 80 and 100 seconds. If the package uses an edited
sequence of captured UI states, describe it as an edited demo rather than a
continuous real-time recording.

## Evidence distinctions to retain in the edit

- SHA-256 verifies receipt integrity against a retained original; Ed25519 signs
  the separate authorization lease.
- A safe envelope is a bound, not an automatic amount change or authorization.
- Exact-action VALID verifies KACHING! authority; it is not exchange execution.
- Replay rejection is a consuming-mode check using bounded, local in-memory state.
- Five policy attacks and seven authorization bypasses are different suites.
- Judge Mode contains seven real server-backed scenes and ends at Enforcement Lab.
- Historical live evidence, if used separately, must carry its original date and
  the label RECORDED LIVE EVIDENCE. This offline demo makes no current account claim.

Launch instructions and the seven screenshot paths are in [DEMO.md](DEMO.md).
