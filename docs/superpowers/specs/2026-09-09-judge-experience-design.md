# KACHING Judge Experience Design

## Goal
Make the existing KACHING submission instantly understandable and inspectable from GitHub without changing its core authorization semantics, live-execution boundary, or submission claims.

## Risk boundary
The official hackathon materials establish the deadline and require a Track A demo/video plus GitHub, but the public materials reviewed do not explicitly authorize post-deadline material feature additions. Therefore this work is deliberately presentation/accessibility focused: no new financial capability, no live execution, no policy-rule expansion, and no changed 5/5 or 7/7 claims.

## Competitive research
- Skin wins on compression and access: one-line thesis, live static dashboard, GitHub and demo links above the fold. Its hosted web surface is presentation-only and does not expose its trading backend.
- Leash is the nearest technical competitor: it gates Binance MCP tool calls with configurable and temporal behavior policy, hard rules, hook/proxy enforcement, and 217 tests.
- TradeOS also uses a hosted deterministic simulation and separates proposal, risk evaluation, user authorization, and MCP handoff.

KACHING must not copy their product language or layouts. Its differentiated thesis remains: **Capability is not authorization. Before an AI can touch money, it must carry proof.** Its unique proof surface is the Ed25519 exact-action Authorization Lease bound to action, resource, amount, audience, policy, and observation commitment, plus verifier rejection of altered, expired, or replayed authority.

## Judge-first README
The README first viewport will contain:
1. KACHING name and two-line thesis.
2. Three high-signal links: hosted Proof Explorer, 98-second demo, verification evidence.
3. A compact pipeline: `AI proposes → KACHING decides → ALLOW issues signed authority → verifier returns VALID/REJECTED`.
4. Proof strip: 77 Python tests, 8 UI tests, 5/5 policy attacks, 7/7 authorization bypasses, 26/26 browser checks.
5. A 30-second judge path.

Deep architecture, security limits, local setup, and evidence gallery remain below rather than being deleted.

## Hosted Proof Explorer
Create a separate static judge surface under `judge/` so the real React/Python command deck remains untouched. It will be a small Vite/React app with its own visual identity derived from KACHING's prismatic emerald system, not from competitors.

The Proof Explorer will not implement or simulate financial execution. It will display deterministic evidence exported from the real KACHING kernel and clearly label itself:

`RECORDED DETERMINISTIC FIXTURES · NO WALLET · NO MONEY MOVED · CORE KERNEL LIVES IN REPO`

Primary interaction:
- choose BLOCK, REVIEW, or ALLOW evidence;
- inspect determining rules and authorized amount;
- inspect the signed lease specimen for ALLOW;
- inspect exact-action VALID evidence;
- run through the seven recorded bypass rejection classes;
- open source, verification record, or demo video.

## Evidence generation
Add `scripts/export_judge_evidence.py`. It will instantiate the existing fixture-mode service with an ephemeral Ed25519 key, produce BLOCK/REVIEW/ALLOW decisions plus arena/enforcement-arena evidence, normalize volatile timestamps/nonce/signature display metadata only where necessary for a durable static artifact, and write `judge/public/evidence.json`.

The exporter must never enable live mode, read Binance credentials, place orders, or change policy code. The generated artifact is evidence for a static browser presentation, not a second implementation of the authorization kernel.

## Integrity and honesty
The hosted page must make these distinctions explicit:
- recorded fixture evidence is not a live policy decision;
- a displayed lease specimen is KACHING authority, not a Binance token;
- VALID means the KACHING verifier accepted the exact recorded action, not that Binance executed it;
- no hosted page can place an order or access credentials.

The evidence JSON will carry the source commit SHA and its own SHA-256. README and the page will link back to the verification record.

## Deployment
Prefer Vercel because the judge surface is static and can be instant, cacheable, and secret-free. Configure the project root/output so only `judge/` is deployed. The core Python server remains local-only.

A public link is added to README only after external fetch/browser verification succeeds. If Vercel deployment cannot be verified, README will not contain a fake live-demo URL.

## Testing
- Exporter unit test validates no `live` mode and required evidence fields.
- Judge app unit tests validate the three verdicts, proof counts, disclaimer text, and seven rejection rows.
- Vite build must pass.
- Browser QA checks first paint, navigation, BLOCK/REVIEW/ALLOW, lease specimen, seven bypass rows, mobile/desktop layout, console/network health, and all outbound links.
- Existing KACHING gates remain required: 77 Python tests, 8 current UI tests, 5/5 arena, 7/7 gauntlet, compileall, production UI build, release-safety audit, diff check.

## Non-goals
- no new trading strategy;
- no new policy rules or temporal behavior engine;
- no live Binance write path;
- no copying Skin, Leash, TradeOS, or any competitor wording/layout;
- no rewriting the submitted X post or survey;
- no inflated claim that a static Vercel page is executing the Python kernel.
