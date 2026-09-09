# KACHING! — 30-second judge path

**Thesis:** Capability is not authorization. Before an AI can touch money, it must carry proof.

## Fastest path

1. Open the hosted **Proof Explorer**: `https://kaching-proof.miniup.app`.
2. Watch the official 98-second Track A video: `https://x.com/Selenephose/status/2097472059890905444`.
3. That same X post is the original public Track A submission and was published before the deadline.
4. Switch **BLOCK → REVIEW → ALLOW**.
5. Observe that BLOCK and REVIEW authorize **0.00 USDT** and issue no lease.
6. On ALLOW, inspect the recorded Ed25519 Authorization Lease bound to the exact action, resource, amount ceiling, audience, policy and evidence commitment.
7. Read the enforcement baseline: **exact action → VALID**.
8. Read the seven recorded bypass results: amount, resource, audience, signature, policy, expiry and replay are **REJECTED**.

## Submission snapshot

Pre-deadline comparison snapshot: `052af0841e17596958953f038c7b782ad4defe74`. Later repository work is judge-access / presentation hardening; use that snapshot to inspect what existed at submission time.

## What is live vs recorded

The hosted Proof Explorer is static and secret-free. It presents **recorded deterministic fixture evidence exported by the real KACHING kernel**. It does not execute the Python policy engine in the browser, does not connect to Binance, and cannot move money.

The authoritative implementation is this repository:

- Python authorization kernel: `tradegate/`
- Local command deck: `ui/`
- Deterministic evidence exporter: `scripts/export_judge_evidence.py`
- Machine-readable submission verification: `docs/VERIFICATION.md`

## Reproduce the real kernel

After dependencies are installed, the quickest verification is:

```bash
./scripts/judge_verify.sh
```

Or launch the full command deck manually:

```bash
git clone https://gitlab.com/am.statementforge/kaching.git
cd KACHING
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
npm ci --ignore-scripts --prefix ui
npm run build --prefix ui
python -m tradegate.web
```

Open `http://127.0.0.1:8890` and select **Run judge demo**.

No exchange credentials are required for the deterministic fixture path, and the browser has no live order, transfer, withdrawal, or credential-management route.
