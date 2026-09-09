# KACHING! — 30-second judge path

**Thesis:** Capability is not authorization. Before an AI can touch money, it must carry proof.

## Fastest path

1. Open the hosted **Proof Explorer**: `https://kaching-proof.miniup.app`.
2. Switch **BLOCK → REVIEW → ALLOW**.
3. Observe that BLOCK and REVIEW authorize **0.00 USDT** and issue no lease.
4. On ALLOW, inspect the recorded Ed25519 Authorization Lease bound to the exact action, resource, amount ceiling, audience, policy and evidence commitment.
5. Read the enforcement baseline: **exact action → VALID**.
6. Read the seven recorded bypass results: amount, resource, audience, signature, policy, expiry and replay are **REJECTED**.

## What is live vs recorded

The hosted Proof Explorer is static and secret-free. It presents **recorded deterministic fixture evidence exported by the real KACHING kernel**. It does not execute the Python policy engine in the browser, does not connect to Binance, and cannot move money.

The authoritative implementation is this repository:

- Python authorization kernel: `tradegate/`
- Local command deck: `ui/`
- Deterministic evidence exporter: `scripts/export_judge_evidence.py`
- Machine-readable submission verification: `docs/VERIFICATION.md`

## Reproduce the real kernel

```bash
git clone https://github.com/am-selenephos/KACHING.git
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
