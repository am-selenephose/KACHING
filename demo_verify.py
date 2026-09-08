from __future__ import annotations

import copy
import argparse
import json
from pathlib import Path

from tradegate.evidence import verify_evidence_packet
from tradegate.compiler import digest, verify_receipt

def main():
    parser = argparse.ArgumentParser(description='Verify local KACHING or legacy TradeGate evidence without displaying account data')
    parser.add_argument('proof', nargs='?', type=Path, default=Path('live-proof-demo.json'))
    args = parser.parse_args()
    try:
        packet = json.loads(args.proof.read_text(encoding='utf-8'))
        if 'receipt' in packet:
            receipt = packet['receipt']
            original = (digest({k:v for k,v in packet.items() if k != 'private_evidence_sha256'}) == packet.get('private_evidence_sha256')
                        and verify_receipt(receipt, receipt['decision_sha256']))
            tampered = copy.deepcopy(receipt)
            tampered['verdict'] = 'ALLOW' if receipt['verdict'] != 'ALLOW' else 'BLOCK'
            altered = verify_receipt(tampered, receipt['decision_sha256'])
            evidence_sha = receipt['decision_sha256']
        else:
            original = verify_evidence_packet(packet)
            tampered = copy.deepcopy(packet)
            tampered['decision']['verdict'] = 'ALLOW' if packet['decision']['verdict'] != 'ALLOW' else 'BLOCK'
            altered = verify_evidence_packet(tampered)
            evidence_sha = packet['evidence_sha256']
    except (ValueError, TypeError, KeyError, OSError):
        print('Verification unavailable: invalid or unreadable evidence file.')
        return 1
    print('DECISION_SHA256=', evidence_sha)
    print('ORIGINAL_VERIFIED=', original)
    print('TAMPERED_VERIFIED=', altered)
    print('BASIS=local original digest; not independent issuer authentication')
    return 0 if original and not altered else 1

if __name__ == '__main__':
    raise SystemExit(main())
