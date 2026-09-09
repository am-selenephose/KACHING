import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class JudgeEvidenceTests(unittest.TestCase):
    def test_judge_evidence_is_fixture_only_and_complete(self):
        from scripts.export_judge_evidence import build_evidence

        with tempfile.TemporaryDirectory() as tmp:
            evidence = build_evidence(Path(tmp) / 'issuer.pem')

        self.assertEqual(evidence['meta']['mode'], 'fixture')
        self.assertFalse(evidence['meta']['live_execution'])
        self.assertEqual(evidence['scenarios']['block']['receipt']['verdict'], 'BLOCK')
        self.assertEqual(evidence['scenarios']['review']['receipt']['verdict'], 'REVIEW')
        self.assertEqual(evidence['scenarios']['allow']['receipt']['verdict'], 'ALLOW')
        self.assertEqual(evidence['policy_arena']['passed'], 5)
        self.assertEqual(evidence['policy_arena']['total'], 5)
        self.assertEqual(evidence['enforcement_arena']['baseline'], 'VALID')
        self.assertEqual(evidence['enforcement_arena']['passed'], 7)
        self.assertEqual(evidence['enforcement_arena']['total'], 7)
        self.assertIn('signature', evidence['lease_specimen'])
        self.assertNotIn('private', str(evidence).lower())

    def test_exporter_cli_runs_from_repo_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'evidence.json'
            result = subprocess.run(
                [sys.executable, 'scripts/export_judge_evidence.py', '--output', str(output)],
                cwd=Path(__file__).resolve().parents[1],
                text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output.is_file())
            self.assertIn('JUDGE_EVIDENCE_SHA256=', result.stdout)


if __name__ == '__main__':
    unittest.main()
