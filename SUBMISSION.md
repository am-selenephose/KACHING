# Binance Agent OS Mini Hackathon — Track A Submission

## Confirmed entry steps

1. Follow `@Binance` on X.
2. Repost the official Agent OS Mini Hackathon announcement.
3. Reply or quote-repost with the Track A submission.
4. Attach the video/demo and public GitHub link.
5. Complete the Binance survey before 2026-09-08 23:59 UTC.

## Exact X copy

```text
Track A — EvidenceBound TradeGate: a fail-closed pre-trade governor for Binance Agent OS. AI proposes; TradeGate validates live Binance state, returns ALLOW/REVIEW/BLOCK, and binds each decision to a tamper-evident SHA-256 receipt. #AgentOS #Binance

https://github.com/am-selenephos/evidencebound-runtime/tree/hackathon/binance-agent-os-tradegate
```

Attach the 110-second demo video to the same reply or quote-repost.

## Survey inputs to have ready

Confirmed from the public hackathon flow / same survey guidance:
- Track choice: **Track A / build an AI agent with Agent OS**
- main Binance account UID
- public X submission/quote-repost URL
- public GitHub URL if the form exposes a repository field

The survey is a dynamic Binance page. Its exact Track A field labels were not extractable by the available read-only fetcher. Do not invent labels: open the survey while logged in and confirm the visible fields before final submit.

Known survey URL:
`https://www.binance.com/survey/2913aa200aac462c89a737779393f3d4`

## Do not expose

- API key or secret
- Binance profile files
- account balances
- UID in the public GitHub repo or demo recording
- `live-proof.json` or `live-proof-demo.json`

## Demo claim boundary

Safe claim: a production-account authenticated read and live BNBUSDT market observation produced a genuine deterministic BLOCK; the receipt verified, and a modified protected verdict failed verification. No live order or transfer was executed.
