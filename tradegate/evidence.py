from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from .models import AccountSnapshot, MarketSnapshot, RiskDecision, TradeIntent


def _jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    return value


def build_evidence_packet(intent: TradeIntent, market: MarketSnapshot, account: AccountSnapshot, decision: RiskDecision) -> dict[str, Any]:
    body = {
        "schema": "evidencebound.tradegate.v2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "intent": _jsonable(asdict(intent.normalized())),
        "market": _jsonable(asdict(market)),
        "account": _jsonable(asdict(account)),
        "decision": decision.to_dict(),
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    body["evidence_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return body


def verify_evidence_packet(packet: dict[str, Any]) -> bool:
    candidate = dict(packet)
    expected = candidate.pop("evidence_sha256", None)
    if not expected:
        return False
    canonical = json.dumps(candidate, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    actual = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return actual == expected
