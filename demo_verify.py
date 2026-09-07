from __future__ import annotations

import copy
import json
from pathlib import Path

from tradegate.evidence import verify_evidence_packet

PROOF = Path("live-proof-demo.json")

packet = json.loads(PROOF.read_text(encoding="utf-8"))
print("EVIDENCE_SHA256=", packet["evidence_sha256"])
print("ORIGINAL_VERIFIED=", verify_evidence_packet(packet))

tampered = copy.deepcopy(packet)
tampered["decision"]["verdict"] = (
    "ALLOW" if packet["decision"]["verdict"] != "ALLOW" else "BLOCK"
)
print("TAMPERED_VERIFIED=", verify_evidence_packet(tampered))
