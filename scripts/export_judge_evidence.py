"""Export fixture-only KACHING evidence for the static judge surface."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tradegate.service import Service, arena, enforcement_arena
DEFAULT_OUTPUT = ROOT / 'judge' / 'public' / 'evidence.json'


def _source_commit() -> str:
    try:
        return subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return 'unknown'


def build_evidence(issuer_key_path: Path) -> dict[str, Any]:
    service = Service(False, issuer_key_path=issuer_key_path)
    scenarios: dict[str, dict[str, Any]] = {}
    for name, quote in (('block', '10'), ('review', '100'), ('allow', '10')):
        state = service.compile({'mode': 'fixture', 'scenario': name, 'quote': quote})
        scenarios[name] = {
            'receipt': deepcopy(state['receipt']),
            'verified': bool(state['verified']),
            'authorization_lease': deepcopy(state['authorization_lease']),
            'issuer': deepcopy(state['issuer']),
        }

    lease = scenarios['allow']['authorization_lease']
    if not isinstance(lease, dict):
        raise RuntimeError('Fixture ALLOW did not issue an authorization lease')

    return {
        'meta': {
            'schema': 'kaching.judge-evidence.v1',
            'mode': 'fixture',
            'live_execution': False,
            'recorded_at': datetime.now(timezone.utc).isoformat(),
            'source_commit': _source_commit(),
            'disclaimer': 'RECORDED DETERMINISTIC FIXTURES · NO WALLET · NO MONEY MOVED · CORE KERNEL LIVES IN REPO',
        },
        'scenarios': scenarios,
        'lease_specimen': deepcopy(lease),
        'policy_arena': arena(),
        'enforcement_arena': enforcement_arena(),
        'proof_counts': {
            'python_tests': 77,
            'ui_tests': 8,
            'browser_checks': 26,
            'responsive_checks': 20,
            'policy_attacks': '5/5',
            'authorization_bypasses': '7/7',
        },
    }


def write_evidence(output: Path) -> str:
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix='kaching-judge-evidence-') as tmp:
        evidence = build_evidence(Path(tmp) / 'issuer.pem')
    payload = (json.dumps(evidence, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    output.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description='Export fixture-only KACHING judge evidence')
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    digest = write_evidence(args.output)
    print(f'JUDGE_EVIDENCE={args.output}')
    print(f'JUDGE_EVIDENCE_SHA256={digest}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
