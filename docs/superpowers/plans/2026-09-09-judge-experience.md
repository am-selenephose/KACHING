# KACHING Judge Experience Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the existing KACHING GitHub submission into a judge-first, one-click experience with a hosted static Proof Explorer generated from real fixture evidence, while leaving the core authorization kernel unchanged.

**Architecture:** Preserve `tradegate/` and the existing `ui/` as the authoritative kernel and local command deck. Add one Python evidence exporter that runs the real fixture-mode service and emits a static JSON artifact, plus a separate `judge/` Vite/React app that renders only that evidence. Deploy `judge/` to Vercel and expose the verified URL prominently from README.

**Tech Stack:** Python 3.11+, existing `tradegate` service, React 19, TypeScript 5.9, Vite 8, static JSON, Vercel.

**Spec:** `docs/superpowers/specs/2026-09-09-judge-experience-design.md`

## Global Constraints

- Do not modify core policy decisions, lease semantics, or financial execution boundaries.
- No live Binance reads or writes from the hosted judge surface.
- No credentials, wallet state, API keys, or private evidence in committed artifacts.
- Every hosted-data claim must be labeled as recorded deterministic fixture evidence.
- Preserve the existing 77 Python + 8 UI baseline and 5/5 + 7/7 claims unless fresh verification proves otherwise.
- Do not copy competitor wording, screenshots, layouts, or product concepts.

---

### Task 1: Export real deterministic judge evidence

**Files:**
- Create: `scripts/export_judge_evidence.py`
- Create: `tests/test_judge_evidence.py`
- Create/generated: `judge/public/evidence.json`

**Interfaces:**
- Consumes: `tradegate.service.Service`, `arena`, `enforcement_arena`.
- Produces: JSON object with `meta`, `scenarios`, `policy_arena`, `enforcement_arena`, and `lease_specimen`.

- [ ] **Step 1: Write exporter test first**

```python
from pathlib import Path
from scripts.export_judge_evidence import build_evidence


def test_judge_evidence_is_fixture_only_and_complete(tmp_path: Path):
    evidence = build_evidence(tmp_path / "issuer.pem")
    assert evidence["meta"]["mode"] == "fixture"
    assert evidence["meta"]["live_execution"] is False
    assert evidence["scenarios"]["block"]["receipt"]["verdict"] == "BLOCK"
    assert evidence["scenarios"]["review"]["receipt"]["verdict"] == "REVIEW"
    assert evidence["scenarios"]["allow"]["receipt"]["verdict"] == "ALLOW"
    assert evidence["policy_arena"]["passed"] == evidence["policy_arena"]["total"] == 5
    assert evidence["enforcement_arena"]["passed"] == evidence["enforcement_arena"]["total"] == 7
```

- [ ] **Step 2: Run failing test**

Run: `python -m unittest tests.test_judge_evidence -v`
Expected: FAIL because exporter does not exist yet.

- [ ] **Step 3: Implement minimal exporter**

`build_evidence(key_path)` must instantiate `Service(False, issuer_key_path=key_path)`, compile fixture BLOCK/REVIEW/ALLOW scenarios, call the two arena helpers, capture source commit with `git rev-parse HEAD`, and return JSON-safe data. The module CLI writes canonical pretty JSON to `judge/public/evidence.json` and prints its SHA-256.

- [ ] **Step 4: Run exporter and test**

Run:
`python -m unittest tests.test_judge_evidence -v`
`python scripts/export_judge_evidence.py`
Expected: PASS and a generated `judge/public/evidence.json` with no secret path or private key material.

- [ ] **Step 5: Commit**

```bash
git add scripts/export_judge_evidence.py tests/test_judge_evidence.py judge/public/evidence.json
git commit -m "feat: export deterministic KACHING judge evidence"
```

### Task 2: Build the static KACHING Proof Explorer

**Files:**
- Create: `judge/package.json`
- Create: `judge/package-lock.json`
- Create: `judge/tsconfig.json`
- Create: `judge/index.html`
- Create: `judge/src/main.tsx`
- Create: `judge/src/proof.css`
- Create: `judge/tests/proof.test.mjs`
- Reuse: `judge/public/evidence.json`

**Interfaces:**
- Consumes: `/evidence.json` from Task 1.
- Produces: static Vite site requiring no API server.

- [ ] **Step 1: Add failing static-content test**

The test reads `src/main.tsx` and evidence JSON and asserts presence of the exact disclaimer, three verdict labels, `7 / 7`, and links for source/demo/verification.

- [ ] **Step 2: Run failing test**

Run: `npm test --prefix judge`
Expected: FAIL before implementation.

- [ ] **Step 3: Implement Proof Explorer**

First viewport must show:
- `KACHING!`
- `Before an AI can touch money, it must carry proof.`
- `Capability is not authorization.`
- evidence disclaimer;
- buttons: `Explore BLOCK`, `Explore REVIEW`, `Explore ALLOW`;
- proof strip: `77 Python`, `8 UI`, `5/5 policy attacks`, `7/7 bypasses`, `26/26 browser checks`;
- links: `Source`, `98s demo`, `Verification`.

Below fold, render determining rules, authorized amount, safe envelope, Ed25519 lease specimen fields, exact-action baseline, and all seven bypass rejection reasons. Styling must remain KACHING Prismatic Emerald Glass, not competitor-derived.

- [ ] **Step 4: Test and build**

Run:
`npm ci --ignore-scripts --prefix judge`
`npm test --prefix judge`
`npm run build --prefix judge`
Expected: all judge tests pass and `judge/dist/index.html` exists.

- [ ] **Step 5: Commit**

```bash
git add judge
git commit -m "feat: add static KACHING proof explorer"
```

### Task 3: Make GitHub judge-first

**Files:**
- Modify: `README.md`
- Create: `docs/JUDGE_PATH.md`

**Interfaces:**
- Consumes: final hosted URL only after Task 4 external verification.
- Produces: first-screen GitHub narrative and a 30-second judge path.

- [ ] **Step 1: Add the judge-path document**

It must explain in under one screen:
`proposal → BLOCK/REVIEW/ALLOW → signed lease → exact VALID → seven bypasses rejected`, with explicit fixture/no-execution labels.

- [ ] **Step 2: Restructure README top**

Above the existing architecture, add:
- hero and thesis;
- live Proof Explorer link placeholder token `__KACHING_LIVE_DEMO__` only on a temporary branch/worktree, never committed to main;
- 98s demo link;
- verification link;
- proof strip;
- 30-second judge path;
- one paragraph: `Authorization is an artifact, not an opinion.`

Keep all existing deep documentation below.

- [ ] **Step 3: Verify markdown links except live URL**

Run a local link/path check that every relative README link exists.
Expected: PASS.

### Task 4: Deploy and externally verify the Proof Explorer

**Files:**
- Create: `vercel.json` if needed for root-to-`judge/dist` build/output routing.
- Modify: `README.md` replacing `__KACHING_LIVE_DEMO__` with the observed public URL.
- Modify: `docs/JUDGE_PATH.md` adding the same URL.

**Interfaces:**
- Consumes: built `judge/` app.
- Produces: public HTTPS URL.

- [ ] **Step 1: Deploy static judge app to Vercel**

Configure build command `npm ci --ignore-scripts --prefix judge && npm run build --prefix judge` and output directory `judge/dist`.

- [ ] **Step 2: Externally verify before linking**

Check public HTTP 200, title, thesis, disclaimer, all three verdicts, seven bypass rows, and zero failed same-origin asset requests. Test desktop and mobile widths.

- [ ] **Step 3: Insert only the verified public URL into README and judge path**

No placeholder or protected preview URL may be committed.

- [ ] **Step 4: Commit deployment metadata and README polish**

```bash
git add README.md docs/JUDGE_PATH.md vercel.json
git commit -m "docs: make KACHING judge-first with live proof explorer"
```

### Task 5: Full regression and release verification

**Files:**
- No intended source changes unless a gate exposes a defect.

- [ ] **Step 1: Existing KACHING gates**

Run:
`python -m unittest discover -s tests -v`
`python demo_attack_suite.py`
`python -m compileall -q tradegate tests`
`npm test --prefix ui`
`npm run build --prefix ui`
`python scripts/release_safety_audit.py`
`git diff --check`

Expected: existing counts remain green, with new exporter test added to Python total.

- [ ] **Step 2: Judge gates**

Run:
`python scripts/export_judge_evidence.py`
`npm test --prefix judge`
`npm run build --prefix judge`

Expected: PASS and evidence JSON unchanged after regeneration except intentionally documented source SHA if commit moved.

- [ ] **Step 3: Browser QA public URL**

Verify desktop + mobile, all outbound links, evidence disclaimer, BLOCK/REVIEW/ALLOW switching, lease specimen, and seven rejection classes.

- [ ] **Step 4: Push main and verify exact remote SHA**

Run:
`git push origin main`
`git rev-parse HEAD`
`git ls-remote origin refs/heads/main`
Expected: exact SHA match and clean tree.
