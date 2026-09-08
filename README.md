# KACHING!

**Before an AI can touch money, it must carry proof.**

This directory is the executable Track A submission. The original TradeGate
adapter and regression tests remain beneath KACHING's compiler and command deck.

```bash
cd ui
npm ci --ignore-scripts
npm run build
cd ..
python -m tradegate.web
```

Open http://127.0.0.1:8890 and run the judge demo. Offline fixtures are the default.
For live read-only observations, use `python -m tradegate.web --live` with the
owner's existing configured Binance CLI. Never display the CLI profile in a demo.

```bash
python -m unittest discover -s tests -v
python demo_attack_suite.py
python -m compileall -q tradegate tests
```

For a private live receipt, choose a new output path each time:

```bash
python -m tradegate.cli --symbol BNBUSDT --side BUY --quote 10 --human \
  --evidence-out private-evidence-recording.json
python demo_verify.py private-evidence-recording.json
```

The CLI output is sanitized; the evidence file is private and owner-readable only.
No order-test is requested above. Existing files are not overwritten.

[Product overview](../README.md) · [Architecture](../ARCHITECTURE.md) ·
[Security](../SECURITY.md) · [Demo](../DEMO.md) · [Submission](SUBMISSION.md)
