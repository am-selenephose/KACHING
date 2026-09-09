# KACHING! verification record — September 9, 2026

This record separates locally reproduced evidence from external release and
account actions. It is not a claim of deployment, trade execution, contest entry,
placement, prize, revenue or cloud-CI success.

## Source identity

| Field | Observed value |
|---|---|
| Public repository | `https://github.com/am-selenephos/KACHING` |
| Local repository root | Standalone KACHING repository root; no nested product directory |
| Local branch | `main` |
| Browser-tested UI checkpoint | `199af1a8afe4f33e398f1a06d30024c4eb93a6e9` |
| Checkpoint subject | `feat(ui): finish prismatic emerald interface and revoke stale visible authority` |
| Remote `main` observed before final release push | `190bdd44f79ca86621f7689a297255c393f9f173` |

The browser-tested UI checkpoint is committed locally. The measured screenshots,
video and release documentation were packaged in release payload commit
`f9e0e9e0975da62f68dca655edc274c51b280306`. That commit was pushed to `main`,
and local/remote SHA equality was observed before this documentation-only follow-up.

### Browser-tested UI source hashes

| Source | SHA-256 |
|---|---|
| `ui/src/main.tsx` | `993f14be30297fc6b3fe275aaaf663d940e6177ac72a59579a8bdea9131a6a67` |
| `ui/src/emerald.css` | `44321412bb3ed1fa8974cecd46f98c8bdb98b630c13237444555282380a46cb1` |
| `ui/src/style.css` | `7b4b13c89f82ff3c7215e43a5a70493ddb7382f38ca977cbf46f9cc651386769` |
| `ui/index.html` | `f2854a5e1451463c7d164e8aec47b6785b87b784f0d66f74303ef1151de76114` |

These values match the `sourceHashes` in
[`docs/browser-qa.json`](browser-qa.json) and the files present at checkpoint
`199af1a` when the browser QA was rerun.

## Local executable regression

The following checks were reproduced from the standalone repository on September
9, 2026. The first constrained attempt could not open loopback sockets; after the
test environment granted loopback network permission, the complete Python suite
was rerun and passed.

| Gate | Result | Evidence |
|---|---|---|
| Python unittest suite | **PASS** | 77 run, 0 failures, 0 errors, 0 skipped |
| UI unit suite | **PASS** | 8 declared `test()` cases across 2 files; npm command exited 0 |
| Python bytecode compilation | **PASS** | `compileall` exited 0 |
| TypeScript check + Vite production build | **PASS** | 18 modules transformed; build exited 0 |
| Deterministic policy/evidence arena | **PASS** | 5 / 5 contained |
| Authorization-bypass gauntlet | **PASS** | baseline VALID; 7 / 7 rejected |
| Public release-safety audit | **PASS** | `PUBLIC_AUDIT=PASS` |

Commands:

```bash
python -m unittest discover -s tests -v
python demo_attack_suite.py
python -m compileall -q tradegate tests
npm test --prefix ui
npm run build --prefix ui
python scripts/release_safety_audit.py
git diff --check
```

The deterministic attack output was:

```text
5 / 5 POLICY ATTACKS CONTAINED
BASELINE — VALID
7 / 7 AUTHORIZATION BYPASSES REJECTED
```

The seven rejected classes and server reasons were:

| Bypass | Result |
|---|---|
| Amount escalation | `ACTION_MISMATCH` |
| Resource mutation | `RESOURCE_MISMATCH` |
| Audience mutation | `AUDIENCE_MISMATCH` |
| Signature forgery | `SIGNATURE_INVALID` |
| Policy drift | `POLICY_DRIFT` |
| Expired lease | `AUTHORIZATION_EXPIRED` |
| Consumed-lease replay | `REPLAY_DETECTED` |

These are controlled fixture tests, not a security certification.

## Post-submission judge-access polish

After the Track A deadline, the repository received **presentation and
reproducibility-only** changes so a judge can inspect the already-built KACHING
behavior with less setup friction. These changes do **not** add a live execution
path or change the authorization-policy semantics described by the submission
evidence above.

Current judge-access surfaces:

- public source mirror: `https://gitlab.com/am.statementforge/kaching`;
- submitted GitHub source URL: `https://github.com/am-selenephos/KACHING` (the owner account is currently flagged by GitHub and returns 404 to unauthenticated requests);
- public static Proof Explorer: `https://kaching-proof.miniup.app`;
- direct repository-hosted 98-second MP4:
  `https://gitlab.com/am.statementforge/kaching/-/raw/main/docs/demo/KACHING-98s.mp4`;
- original public Track A post:
  `https://x.com/Selenephose/status/2097465082141905231`;
- one-command deterministic verification: `./scripts/judge_verify.sh`;
- machine-readable fixture evidence: `judge/public/evidence.json`.

The hosted Proof Explorer is static, secret-free fixture presentation. It cannot
access a wallet, read exchange credentials, place orders, transfer funds or
withdraw funds. The authoritative Python implementation remains in this
repository. The direct MP4 link is provided so video review does not depend on an
X login or embed working for the reviewer.

The current repository regression contains **79 Python tests total** (the
original 77 product tests plus 2 judge-evidence/export regression tests), **8 UI
tests**, and **5 judge-surface tests**. The original 77/8 product-test counts in
this record remain the historically measured submission evidence rather than
being retroactively rewritten.

## Rendered Chromium QA

The final UI source hashes above were served through the actual local Python
bridge and exercised with system Chromium `151.0.7922.173`. The machine-readable
record timestamp is `2026-09-08T23:05:54.294Z`.

Status: **PASS — 26 / 26 checks**.

Verified browser behavior includes:

- HTTP 200 and the KACHING! application title;
- local loading of Gloock, Newsreader and IBM Plex Mono;
- dark cool-green token `--night: #020d0d`;
- localized prism film and pointer-responsive optical sheen;
- zero rejected hero shard elements in the rendered DOM;
- BLOCK with zero authority and no lease;
- REVIEW at 100.00 USDT with a 24.37 USDT envelope and zero authority;
- remediation changes only the draft until recompilation;
- ALLOW lease fields and a live 30-to-29-second countdown;
- editing an ALLOW proposal hides the prior visible authority;
- reload does not present an earlier lease as authority for a current draft;
- exact signed action VALID;
- individual amount, resource, audience, signature and replay rejection paths;
- seven-bypass gauntlet 7 / 7;
- original receipt PASS and tampered copy FAIL;
- policy/evidence arena 5 / 5;
- Judge Mode reaches the Enforcement Lab and 7 / 7 result;
- expandable ledger event identity;
- visible keyboard focus;
- reduced-motion styling and reduced-motion Judge Mode completion;
- no rendered private-field labels in the bounded scan;
- zero relevant console warnings/errors and zero failed requests.

Responsive evidence covers all four workspaces — Command Deck, Enforcement Lab,
Adversarial Arena and Decision Ledger — at 375, 768, 1280, 1440 and 1920 pixels:
**20 / 20 viewport/workspace combinations with no horizontal overflow**.

The private-label and secret-pattern scans reduce accidental-disclosure risk; they
cannot prove absence of every possible secret. The rendered test is a local
point-in-time result, not continuous monitoring.

## Final screenshot artifacts

Each capture is 1920×1080 and was produced by the browser QA run tied to the source
hashes above.

| Artifact | SHA-256 |
|---|---|
| `docs/screenshots/01-command-deck.png` | `1e6c11835c188a8c50ba199a9917016adad81c29e9e1f9630a0003cd3a4dd7c4` |
| `docs/screenshots/02-block.png` | `587da7718258294de3cc28b67d66b54c7eb0aad6a7c71c972f44c7c61cadc0ac` |
| `docs/screenshots/03-review-safe-envelope.png` | `3330a95a66cfa3def14176278055830cce1df7e4776aea6ccb5e0498365a7e28` |
| `docs/screenshots/04-authorization-lease.png` | `ae0ed57faa4b21b02ad2b81fc04bc6adf58731f1c557eec849f4dc29e4f6e1d7` |
| `docs/screenshots/05-enforcement-valid.png` | `57dc7279c6ceff9d494779e88939b6358232baf77c9a8bd48d5f41619e36a869` |
| `docs/screenshots/06-seven-bypasses.png` | `5ca604d2530f8eb962d6cee696a87aa2c0ee3915a290e0206931633e9e596e3d` |
| `docs/screenshots/07-receipt-tamper.png` | `eeca12e7ec839dd3ef7cb7549600cdce017d078b6444ca8faf7bbfe1895787f6` |

The same hashes are stored in the browser QA JSON.

## Demo video gate

Status: **PASS locally**. The final fixture-only browser recording exists at
`docs/demo/KACHING-98s.mp4` and was regenerated after the UI checkpoint commit.

| Field | Measured value |
|---|---|
| Duration | **98 seconds** |
| Resolution | **1920×1080** |
| Video codec | **h264** |
| Pixel format | **yuv420p** |
| Frame rate | **30/1** |
| File size | **13233989 bytes** |
| MP4 SHA-256 | `e393b1184b2542403dd8a29b5b918dd856c9f7dddfb5e73f6d3ecc406e67f0e8` |
| Thumbnail SHA-256 | `0beda985b6340ead2218a183c1ae250e3f7ae57e4ff549063dd9fd0ad3ad53dc` |
| UI checkpoint shown by recording | `199af1a8afe4f33e398f1a06d30024c4eb93a6e9` |

The recording uses an isolated fixture-only server with an ephemeral Ed25519 issuer
key and does not enable live Binance observations or financial execution. It includes
explicit on-screen captions, so the BLOCK → REVIEW → ALLOW → VALID → 7/7 rejection
story remains understandable when muted. The exported MP4 has no audio stream; the
prepared voiceover remains in `DEMO_SCRIPT.md` if narration is added later.

## Live Binance evidence status

This final package does not include a retained public artifact that independently
proves a current authenticated Binance account observation. The deterministic
submission demo therefore makes **no current account-state or live-execution
claim**. `--live` is an optional read-only local mode, not a requirement for the
fixture demo.

No order-test, live order, transfer or withdrawal was performed by this
verification pass.

## GitHub Actions status

The repository contains an active `KACHING CI` workflow covering Python 3.11,
3.12 and 3.13 plus Node 24 UI gates. A read-only GitHub check on September 9
reported that repository Actions permissions were enabled and the workflow was
active, but `gh run list` returned no runs.

An earlier manual dispatch attempt recorded HTTP 422 with GitHub reporting
“Actions has been disabled for this user.” No completed workflow run exists in
the observed evidence. Cloud CI is therefore **UNVERIFIED / ACCOUNT-LEVEL
BLOCKER**, not PASS. Recheck once after the final push; only an actual completed
green run may change this status.

## Security-model evidence boundary

The local results above do not remove these architectural limitations:

- fixture and live ALLOW decisions share one issuer/verifier trust root, and the
  lease does not encode observation mode;
- the PEP is a logical verifier in the same local process, not an isolated
  executor boundary;
- enforcement does not refresh financial state, reserve funds, aggregate spend or
  revalidate the observation commitment;
- multiple unexpired leases may coexist;
- replay consumption is optional, memory-only and bounded;
- caller/subject identities are not authenticated;
- receipt anchors and the visible ledger reset on restart;
- the issuer PEM is unencrypted and protected only by OS permissions;
- no browser or PEP live execution path exists.

See [SECURITY.md](../SECURITY.md) for the complete claim boundary.

## External submission handoff

A final public Track A post is now externally addressable at:
`https://x.com/Selenephose/status/2097465082141905231`. The repository also
contains the 98-second MP4 and exposes the direct raw-file URL above.

The owner reports that the official survey returned a submitted/check-mark
confirmation. That account-specific survey receipt is not stored as a public,
machine-verifiable repository artifact, so the repository does not independently
prove the survey response itself.

Still **UNVERIFIED** here: contest acceptance, placement, prize, payment or
revenue. A public post and owner-reported survey success do not imply any of those
outcomes.

## Current verdict

| Gate | Verdict |
|---|---|
| Authorization and UI local regression | **PASS** |
| Exact rendered Chromium QA | **PASS** |
| Seven final screenshots | **PASS locally; final hashes pinned** |
| 80–100 second demo video | **PASS locally — 98s H.264 1920×1080** |
| Final release payload commit and clean-tree gate | **PASS — `f9e0e9e`** |
| Local/remote `main` SHA equality | **PASS at release payload checkpoint; final doc-only head rechecked in handoff** |
| GitHub Actions | **UNVERIFIED / ACCOUNT-LEVEL BLOCKER** |
| Public X Track A post | **VERIFIED URL PRESENT** |
| Official survey | **OWNER-REPORTED SUBMITTED; PUBLIC RECEIPT NOT STORED** |

**LOCAL PRODUCT EVIDENCE: PASS. PUBLIC X POST: VERIFIED. SURVEY: OWNER-REPORTED SUBMITTED. CONTEST OUTCOME: UNVERIFIED.**
