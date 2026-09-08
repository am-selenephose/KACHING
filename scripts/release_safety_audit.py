from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "build",
    "dist",
}

BLOCKED_DIRS = {
    ".netlify",
    "artifacts",
    "credentials",
    "data",
    "grant-evidence",
    "logs",
    "snapshots",
}

BLOCKED_NAMES = {
    ".env",
    ".envrc",
    "=26.0.0",
    "FETCH_HEAD",
    "credentials",
    "credentials.json",
    "id_ed25519",
    "id_rsa",
}

BLOCKED_SUFFIXES = {
    ".7z",
    ".db",
    ".gz",
    ".key",
    ".p12",
    ".pem",
    ".pfx",
    ".rar",
    ".sqlite",
    ".sqlite3",
    ".tar",
    ".tgz",
    ".zip",
    ".zst",
}

TEXT_SUFFIXES = {
    ".c",
    ".cfg",
    ".cpp",
    ".css",
    ".csv",
    ".go",
    ".h",
    ".html",
    ".hpp",
    ".ini",
    ".java",
    ".js",
    ".jsx",
    ".json",
    ".kt",
    ".lock",
    ".md",
    ".mjs",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".sh",
    ".sql",
    ".swift",
    ".ts",
    ".tsx",
    ".toml",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}

TEXT_NAMES = {".gitignore", "Dockerfile", "LICENSE", "Makefile"}

SECRET_PATTERNS = {
    "assigned_credential": re.compile(
        r'''(?:api[_-]?(?:key|secret)|authorization|bearer|cookie)\s*["']?\s*[:=]\s*["']?[A-Za-z0-9_+/=.-]{32,}''',
        re.IGNORECASE,
    ),
    "private_key": re.compile(
        r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----",
        re.IGNORECASE,
    ),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "stripe_secret": re.compile(r"\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{16,}\b"),
    "google_api_key": re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    "slack_token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{16,}\b"),
}


@dataclass(frozen=True, order=True)
class AuditHit:
    label: str
    path: str
    line_number: int = 0

    def location(self) -> str:
        return f"{self.path}:{self.line_number}" if self.line_number else self.path


def audit_repository(root: str | Path) -> list[AuditHit]:
    repository_root = Path(root).resolve()
    if not repository_root.is_dir():
        raise ValueError(f"audit root is not a directory: {repository_root}")

    hits: list[AuditHit] = []
    for path in sorted(repository_root.rglob("*")):
        relative = path.relative_to(repository_root)

        if any(part in SKIP_DIRS for part in relative.parts):
            continue

        if path.is_symlink():
            hits.append(AuditHit("symlink_present", str(relative)))
            continue

        if path.is_dir():
            if path.name in BLOCKED_DIRS:
                hits.append(AuditHit("blocked_runtime_directory", str(relative)))
            continue

        if any(part in BLOCKED_DIRS for part in relative.parts[:-1]):
            continue

        if (path.name.endswith('.json') and path.name.startswith(('live-proof', 'private-evidence', 'tradegate-evidence'))) or path.name in BLOCKED_NAMES or (
            path.name.startswith(".env.") and path.name != ".env.example"
        ):
            hits.append(AuditHit("blocked_file_name", str(relative)))

        if path.suffix.lower() in BLOCKED_SUFFIXES:
            hits.append(AuditHit("blocked_file_suffix", str(relative)))

        if not path.is_file():
            continue

        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in TEXT_NAMES:
            continue

        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            hits.append(AuditHit("non_utf8_text_file", str(relative)))
            continue

        for line_number, line in enumerate(lines, start=1):
            for label, pattern in SECRET_PATTERNS.items():
                if pattern.search(line):
                    hits.append(AuditHit(label, str(relative), line_number))

    return sorted(set(hits))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when a public EvidenceBound checkout contains local or secret material."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="repository root to audit",
    )
    args = parser.parse_args(argv)

    hits = audit_repository(args.root)
    if hits:
        print("PUBLIC_AUDIT=REVIEW_REQUIRED")
        for hit in hits:
            print(f"{hit.label}\t{hit.location()}")
        return 1

    print("PUBLIC_AUDIT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
