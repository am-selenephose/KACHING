"""Deterministic authorization. No model, network call, or execution capability."""
from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, ROUND_DOWN, localcontext
from typing import Any

from .governor import RiskPolicy
from .models import AccountSnapshot, MarketSnapshot, TradeIntent

D = Decimal
STAGES = ('Normalize', 'Observe', 'Verify evidence', 'Compile policy',
          'Safe envelope', 'Authorize', 'Attest')


def number(value: Decimal) -> str:
    if not value.is_finite():
        raise ValueError('Non-finite decimal')
    text = format(value, 'f')
    return (text.rstrip('0').rstrip('.') if '.' in text else text) or '0'


def canonical(value: Any) -> Any:
    if isinstance(value, Decimal):
        return number(value)
    if isinstance(value, dict):
        return {k: canonical(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [canonical(v) for v in value]
    return value


def digest(value: Any) -> str:
    data = json.dumps(canonical(value), sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(data.encode()).hexdigest()


@dataclass(frozen=True)
class FinancialIntent:
    origin: str
    action: str
    symbol: str
    requested_quote_notional: Decimal
    metadata: dict[str, Any] = field(default_factory=dict)

    def normalized(self) -> FinancialIntent:
        trade = TradeIntent(self.symbol, self.action, self.requested_quote_notional).normalized()
        if self.origin not in {'agent', 'human', 'external'}:
            raise ValueError('Unsupported origin')
        if not isinstance(self.metadata, dict):
            raise ValueError('Metadata must be an object')
        if len(json.dumps(self.metadata, allow_nan=False)) > 4096:
            raise ValueError('Metadata is too large')
        return FinancialIntent(self.origin, trade.side, trade.symbol, trade.quote_notional, self.metadata)


@dataclass(frozen=True)
class Policy(RiskPolicy):
    version: str = 'kaching-v1'
    market_snapshot_max_age: int = 60

    def validate(self) -> None:
        for key, value in asdict(self).items():
            if key not in {'version', 'market_snapshot_max_age'}:
                if not isinstance(value, D) or not value.is_finite() or value < 0 or value > D('1e12'):
                    raise ValueError('Invalid policy value')
        if not D('0') < self.max_balance_fraction <= 1 or self.min_depth_multiple <= 0:
            raise ValueError('Invalid policy limits')
        if self.max_quote_notional <= 0 or not 1 <= self.market_snapshot_max_age <= 300:
            raise ValueError('Invalid policy maximum')
        if self.review_spread_bps > self.max_spread_bps or self.review_abs_24h_move_pct > self.max_abs_24h_move_pct:
            raise ValueError('Review threshold exceeds blocking threshold')

    @property
    def sha256(self) -> str:
        self.validate()
        return digest(asdict(self))


@dataclass(frozen=True)
class Compilation:
    receipt: dict[str, Any]
    safe_envelope: Decimal
    private_evidence: dict[str, Any]


def valid_decimal(value: Any, *, negative: bool = False) -> bool:
    return (isinstance(value, D) and value.is_finite()
            and (negative or value >= 0) and abs(value) <= D('1e18')
            and len(value.as_tuple().digits) <= 40 and value.as_tuple().exponent >= -18)


class Compiler:
    def __init__(self, policy: Policy | None = None):
        self.policy = policy or Policy()
        self.policy.validate()

    def compile(self, intent: FinancialIntent, market: MarketSnapshot,
                account: AccountSnapshot, *, mode: str = 'live',
                now: datetime | None = None) -> Compilation:
        intent = intent.normalized()
        if mode not in {'live', 'fixture'}:
            raise ValueError('Invalid observation mode')
        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            raise ValueError('Aware clock required')
        p = self.policy
        reasons: list[str] = []
        review: list[str] = []
        checks: dict[str, bool | None] = {
            'Account authentication': account.authenticated is True,
            'Market integrity': False, 'Spread': None, '24h movement': None,
            'Visible depth': None, 'Cash buffer': None, 'Balance fraction': None,
        }
        if account.authenticated is not True:
            reasons.append('ACCOUNT_AUTH_UNAVAILABLE')
        if account.trading_enabled is not True:
            reasons.append('ACCOUNT_TRADING_UNAVAILABLE')
        if mode == 'live':
            try:
                account_time = datetime.fromisoformat(account.observed_at.replace('Z', '+00:00'))
                if not 0 <= (now - account_time).total_seconds() <= p.market_snapshot_max_age:
                    reasons.append('ACCOUNT_DATA_STALE')
            except (ValueError, TypeError, AttributeError):
                reasons.append('INVALID_ACCOUNT_TIMESTAMP')
        if intent.action != 'BUY':
            reasons.append('SELL_INVENTORY_UNAVAILABLE')
        if not valid_decimal(account.free_usdt):
            reasons.append('INVALID_ACCOUNT_STATE')
        market_valid = all(valid_decimal(getattr(market, key), negative=key == 'price_change_pct_24h')
                           for key in ('bid', 'ask', 'last_price', 'price_change_pct_24h', 'bid_depth_usdt', 'ask_depth_usdt'))
        if market_valid:
            market_valid = market.bid > 0 and market.ask >= market.bid and market.last_price > 0
        if not market_valid:
            reasons.append('INVALID_MARKET_SNAPSHOT')
        if market.symbol != intent.symbol:
            reasons.append('SYMBOL_MISMATCH')
        try:
            observed = datetime.fromisoformat(market.observed_at.replace('Z', '+00:00'))
            age = (now - observed).total_seconds()
            if not 0 <= age <= p.market_snapshot_max_age:
                reasons.append('MARKET_DATA_STALE' if age > 0 else 'MARKET_TIME_IN_FUTURE')
        except (ValueError, TypeError, AttributeError):
            reasons.append('INVALID_MARKET_TIMESTAMP')
        source_valid = ((market.source == 'fixture' and account.source == 'fixture') if mode == 'fixture' else
                        (market.source in {'binance-cli:spot', 'binance-rest-fallback:spot'}
                         and account.source == 'binance-cli:account'))
        if not source_valid:
            reasons.append('OBSERVATION_PROVENANCE_INVALID')
        checks['Market integrity'] = market_valid and not any(r in reasons for r in (
            'SYMBOL_MISMATCH', 'MARKET_DATA_STALE', 'MARKET_TIME_IN_FUTURE',
            'INVALID_MARKET_TIMESTAMP', 'OBSERVATION_PROVENANCE_INVALID'))
        safe = D('0')
        metrics: dict[str, str] = {}
        if not reasons:
            with localcontext() as ctx:
                ctx.prec = 60
                spread, move = market.spread_bps, abs(market.price_change_pct_24h)
                safe = max(D('0'), min(p.max_quote_notional,
                           account.free_usdt * p.max_balance_fraction,
                           account.free_usdt - p.min_cash_buffer_usdt,
                           market.ask_depth_usdt / p.min_depth_multiple)).quantize(D('.01'), rounding=ROUND_DOWN)
                checks.update({'Spread': spread <= p.max_spread_bps,
                               '24h movement': move <= p.max_abs_24h_move_pct,
                               'Visible depth': market.ask_depth_usdt >= intent.requested_quote_notional * p.min_depth_multiple,
                               'Cash buffer': account.free_usdt - intent.requested_quote_notional >= p.min_cash_buffer_usdt,
                               'Balance fraction': intent.requested_quote_notional <= account.free_usdt * p.max_balance_fraction})
                metrics = {'spread_bps': f'{spread:.4f}', 'abs_24h_move_pct': number(move)}
                if not checks['Spread']:
                    reasons.append('SPREAD_TOO_WIDE')
                elif spread > p.review_spread_bps:
                    review.append('SPREAD_ELEVATED')
                if not checks['24h movement']:
                    reasons.append('EXTREME_24H_MOVE')
                elif move > p.review_abs_24h_move_pct:
                    review.append('HIGH_24H_MOVE')
                if safe == 0:
                    if not checks['Cash buffer']:
                        reasons.append('CASH_BUFFER_BREACH')
                    reasons.append('NO_SAFE_NOTIONAL')
                elif intent.requested_quote_notional > safe:
                    review.append('REQUEST_EXCEEDS_SAFE_ENVELOPE')
        if reasons:
            safe = D('0')
        verdict = 'BLOCK' if reasons else ('REVIEW' if review else 'ALLOW')
        reasons = reasons or review or ['ALL_CHECKS_PASSED']
        authorized = intent.requested_quote_notional if verdict == 'ALLOW' else D('0')
        remediation = self.remediate(reasons, safe if mode == 'fixture' else None)
        # Salt is private: a public observation commitment must not be a balance-guessing oracle.
        # Invalid input is represented safely; no NaN is serialized into a proof.
        private = {'intent': canonical(asdict(intent)),
                   'policy': canonical(asdict(p)),
                   'observation': {'market': {k: str(v) for k,v in asdict(market).items()},
                                   'account': {'free_usdt': str(account.free_usdt),
                                               'source': account.source,
                                               'authenticated': account.authenticated,
                                               'trading_enabled': account.trading_enabled,
                                               'observed_at': account.observed_at}},
                   'nonce': secrets.token_hex(32)}
        receipt = {
            'schema': 'kaching.receipt.v1', 'proposal_id': secrets.token_hex(8),
            'generated_at': now.isoformat(), 'mode': mode,
            'origin': intent.origin, 'action': intent.action, 'symbol': intent.symbol,
            'requested': number(intent.requested_quote_notional), 'authorized': number(authorized),
            'safe_envelope': number(safe) if mode == 'fixture' else None,
            'envelope_visibility': 'public-fixture' if mode == 'fixture' else 'owner-private',
            'verdict': verdict, 'reasons': reasons, 'remediation': remediation,
            'checks': checks, 'metrics': metrics,
            'market_source': market.source if market.source in {'fixture', 'binance-cli:spot', 'binance-rest-fallback:spot'} else 'unavailable',
            'account_authenticated': account.authenticated is True,
            'policy_version': p.version, 'policy_sha256': p.sha256,
            'observation_commitment': digest(private),
        }
        receipt['decision_sha256'] = digest(receipt)
        private['receipt'] = receipt
        private['private_evidence_sha256'] = digest(private)
        return Compilation(receipt, safe, private)

    @staticmethod
    def remediate(reasons: list[str], safe: Decimal | None) -> list[str]:
        actions = {
            'REQUEST_EXCEEDS_SAFE_ENVELOPE': f'Reduce requested size to at most {number(safe)} USDT and compile a new proposal.' if safe is not None else 'Reduce requested size within the private owner envelope and compile a new proposal.',
            'NO_SAFE_NOTIONAL': 'Restore sufficient account funding or have the owner explicitly revise policy, then compile again.',
            'CASH_BUFFER_BREACH': 'Restore the required cash buffer before proposing a buy.',
            'ACCOUNT_AUTH_UNAVAILABLE': 'Restore authenticated Binance account observation.',
            'ACCOUNT_TRADING_UNAVAILABLE': 'Account trading permission is unavailable. Owner intervention is required.',
            'ACCOUNT_DATA_STALE': 'Refresh authenticated account state before compiling again.',
            'INVALID_ACCOUNT_STATE': 'Refresh a valid authenticated account observation.',
            'SELL_INVENTORY_UNAVAILABLE': 'This build authorizes BUY only; SELL requires a base-asset inventory policy.',
            'ALL_CHECKS_PASSED': 'Policy permits this proposal. This build does not execute live orders.',
            'SPREAD_ELEVATED': 'Wait for spread to return below the review threshold and compile again.',
            'HIGH_24H_MOVE': 'Wait for 24h movement to return below the review threshold and compile again.',
            'SPREAD_TOO_WIDE': 'Refresh market data when spread is within policy.',
            'EXTREME_24H_MOVE': 'Refresh market data when 24h movement is within policy.',
        }
        return list(dict.fromkeys(actions.get(reason, 'Refresh a valid, fresh observation from the configured source.') for reason in reasons))


def verify_receipt(receipt: Any, trusted_digest: str) -> bool:
    if not isinstance(receipt, dict) or not isinstance(trusted_digest, str) or len(trusted_digest) != 64:
        return False
    try:
        expected = receipt.get('decision_sha256')
        return (isinstance(expected, str) and hmac.compare_digest(expected, trusted_digest)
                and hmac.compare_digest(digest({k:v for k,v in receipt.items() if k != 'decision_sha256'}), trusted_digest))
    except (ValueError, TypeError, RecursionError):
        return False


def human_receipt(r: dict[str, Any]) -> str:
    return '\n'.join(('KACHING! — FINANCIAL ACTION RECEIPT',
        f"SOURCE: {r['mode'].upper()}", f"ACTION: {r['action']} {r['symbol']}",
        f"REQUESTED: {r['requested']} USDT", f"AUTHORIZED: {r['authorized']} USDT",
        f"VERDICT: {r['verdict']}", 'WHY: ' + ', '.join(r['reasons']),
        f"POLICY: {r['policy_version']}", f"POLICY SHA-256: {r['policy_sha256']}",
        f"DECISION SHA-256: {r['decision_sha256']}",
        'INTEGRITY: verify against the retained original digest; not an issuer signature.'))
