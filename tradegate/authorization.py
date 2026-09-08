from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal as D
from pathlib import Path
from threading import RLock
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from .compiler import FinancialIntent, canonical, number


def canonical_action(intent: FinancialIntent, audience: str) -> dict[str, str]:
    intent = intent.normalized()
    if not isinstance(audience, str) or not audience or len(audience) > 128:
        raise ValueError('Invalid authorization audience')
    return {
        'origin': intent.origin,
        'action': intent.action,
        'symbol': intent.symbol,
        'requested_quote_notional': number(intent.requested_quote_notional),
        'audience': audience,
    }


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(canonical(value), sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode()
def intent_sha256(intent: FinancialIntent, audience: str) -> str:
    return hashlib.sha256(_canonical_bytes(canonical_action(intent, audience))).hexdigest()


def _fingerprint(public_key_bytes: bytes) -> str:
    return hashlib.sha256(public_key_bytes).hexdigest()


def _parse_time(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError('Invalid authorization timestamp')
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Authorization timestamp must be aware')
    return parsed


@dataclass(frozen=True)
class AuthorizationResult:
    valid: bool
    reason: str


class ReplayCache:
    def __init__(self, max_entries: int = 512):
        self.max_entries = max_entries
        self._seen: dict[str, datetime] = {}
        self._lock = RLock()

    def consume(self, nonce: str, expires_at: datetime, now: datetime) -> bool:
        with self._lock:
            self._seen = {k: v for k, v in self._seen.items() if v > now}
            if nonce in self._seen:
                return False
            if len(self._seen) >= self.max_entries:
                oldest = min(self._seen, key=self._seen.get)
                self._seen.pop(oldest, None)
            self._seen[nonce] = expires_at
            return True
class AuthorizationIssuer:
    def __init__(self, key_path: Path | str):
        self.key_path = Path(key_path).expanduser()
        self._private_key = self._load_or_create_key()
        self.public_key_bytes = self._private_key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.public_key_fingerprint = _fingerprint(self.public_key_bytes)

    @property
    def public_key_b64(self) -> str:
        return base64.b64encode(self.public_key_bytes).decode('ascii')

    def _load_or_create_key(self) -> Ed25519PrivateKey:
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.key_path.parent.chmod(0o700)
        except OSError:
            pass
        if self.key_path.exists():
            key = serialization.load_pem_private_key(self.key_path.read_bytes(), password=None)
            if not isinstance(key, Ed25519PrivateKey):
                raise ValueError('KACHING issuer key is not Ed25519')
            os.chmod(self.key_path, 0o600)
            return key
        key = Ed25519PrivateKey.generate()
        encoded = key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
        fd = os.open(self.key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(fd, 'wb') as handle:
                handle.write(encoded)
        except Exception:
            try:
                self.key_path.unlink()
            except OSError:
                pass
            raise
        os.chmod(self.key_path, 0o600)
        return key
    def issue(
        self,
        receipt: dict[str, Any],
        intent: FinancialIntent,
        *,
        audience: str,
        now: datetime | None = None,
        ttl_seconds: int = 30,
    ) -> dict[str, Any]:
        if receipt.get('verdict') != 'ALLOW' or receipt.get('authorized') in {None, '0'}:
            raise ValueError('Only ALLOW decisions may issue authorization')
        if not 1 <= ttl_seconds <= 300:
            raise ValueError('Invalid authorization TTL')
        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            raise ValueError('Aware clock required')
        action = canonical_action(intent, audience)
        if (receipt.get('action') != action['action'] or receipt.get('symbol') != action['symbol']
                or receipt.get('origin') != action['origin'] or receipt.get('requested') != action['requested_quote_notional']):
            raise ValueError('Receipt and authorization intent differ')
        unsigned = {
            'schema': 'kaching.authorization.v1',
            'decision_id': receipt['proposal_id'],
            'origin': action['origin'], 'action': action['action'],
            'resource': action['symbol'], 'audience': action['audience'],
            'requested': action['requested_quote_notional'],
            'maximum_authorized': receipt['authorized'],
            'intent_sha256': intent_sha256(intent, audience),
            'policy_version': receipt['policy_version'],
            'policy_sha256': receipt['policy_sha256'],
            'observation_commitment': receipt['observation_commitment'],
            'issued_at': now.isoformat(),
            'expires_at': (now + timedelta(seconds=ttl_seconds)).isoformat(),
            'nonce': secrets.token_hex(16),
            'issuer_key_fingerprint': self.public_key_fingerprint,
            'signature_algorithm': 'Ed25519',
        }
        signature = self._private_key.sign(_canonical_bytes(unsigned))
        return {**unsigned, 'signature': base64.b64encode(signature).decode('ascii')}
class AuthorizationVerifier:
    def __init__(self, trusted_public_key: bytes, replay_cache: ReplayCache | None = None):
        self.public_key = Ed25519PublicKey.from_public_bytes(trusted_public_key)
        self.public_key_fingerprint = _fingerprint(trusted_public_key)
        self.replay_cache = replay_cache or ReplayCache()

    def verify(
        self,
        lease: Any,
        intent: FinancialIntent,
        *,
        audience: str,
        current_policy_sha256: str,
        now: datetime | None = None,
        consume: bool = False,
    ) -> AuthorizationResult:
        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None or not isinstance(lease, dict):
            return AuthorizationResult(False, 'AUTHORIZATION_INVALID')
        if lease.get('schema') != 'kaching.authorization.v1':
            return AuthorizationResult(False, 'AUTHORIZATION_INVALID')
        if lease.get('issuer_key_fingerprint') != self.public_key_fingerprint:
            return AuthorizationResult(False, 'WRONG_ISSUER')
        signature_text = lease.get('signature')
        if not isinstance(signature_text, str):
            return AuthorizationResult(False, 'SIGNATURE_INVALID')
        unsigned = {k: v for k, v in lease.items() if k != 'signature'}
        try:
            signature = base64.b64decode(signature_text, validate=True)
            self.public_key.verify(signature, _canonical_bytes(unsigned))
        except (ValueError, InvalidSignature, TypeError):
            return AuthorizationResult(False, 'SIGNATURE_INVALID')
        try:
            issued_at = _parse_time(lease.get('issued_at'))
            expires_at = _parse_time(lease.get('expires_at'))
        except ValueError:
            return AuthorizationResult(False, 'AUTHORIZATION_INVALID')
        if expires_at <= issued_at or now > expires_at:
            return AuthorizationResult(False, 'AUTHORIZATION_EXPIRED')
        if issued_at - now > timedelta(seconds=5):
            return AuthorizationResult(False, 'AUTHORIZATION_NOT_YET_VALID')
        if lease.get('policy_sha256') != current_policy_sha256:
            return AuthorizationResult(False, 'POLICY_DRIFT')
        if lease.get('audience') != audience:
            return AuthorizationResult(False, 'AUDIENCE_MISMATCH')
        expected = canonical_action(intent, audience)
        if lease.get('resource') != expected['symbol']:
            return AuthorizationResult(False, 'RESOURCE_MISMATCH')
        if lease.get('origin') != expected['origin'] or lease.get('action') != expected['action']:
            return AuthorizationResult(False, 'ACTION_MISMATCH')
        if lease.get('requested') != expected['requested_quote_notional']:
            return AuthorizationResult(False, 'ACTION_MISMATCH')
        if lease.get('intent_sha256') != intent_sha256(intent, audience):
            return AuthorizationResult(False, 'ACTION_MISMATCH')
        try:
            requested = D(expected['requested_quote_notional'])
            ceiling = D(str(lease.get('maximum_authorized')))
            if not requested.is_finite() or not ceiling.is_finite() or requested > ceiling or ceiling <= 0:
                return AuthorizationResult(False, 'AMOUNT_EXCEEDS_AUTHORIZATION')
        except Exception:
            return AuthorizationResult(False, 'AUTHORIZATION_INVALID')
        nonce = lease.get('nonce')
        if not isinstance(nonce, str) or len(nonce) < 16:
            return AuthorizationResult(False, 'AUTHORIZATION_INVALID')
        if consume and not self.replay_cache.consume(nonce, expires_at, now):
            return AuthorizationResult(False, 'REPLAY_DETECTED')
        return AuthorizationResult(True, 'VALID')
