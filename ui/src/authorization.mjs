/** @param {{expires_at:string}} lease */
export function leaseCountdown(lease, nowMs = Date.now()) {
  const expires = Date.parse(lease.expires_at);
  if (!Number.isFinite(expires)) return 'invalid';
  const remaining = Math.ceil((expires - nowMs) / 1000);
  return remaining > 0 ? `${remaining}s` : 'expired';
}

/**
 * Build a local enforcement-simulation request. The signed lease is never mutated.
 * @param {Record<string, any>} lease
 * @param {'exact'|'amount'|'resource'|'audience'|'signature'|'replay'} mutation
 */
export function buildEnforcementRequest(lease, mutation = 'exact') {
  const request = {
    lease,
    origin: lease.origin,
    action: lease.action,
    symbol: lease.resource,
    quote: lease.requested,
    audience: lease.audience,
    consume: mutation === 'replay',
  };
  if (mutation === 'amount') request.quote = incrementCent(lease.requested);
  if (mutation === 'resource') request.symbol = lease.resource === 'BTCUSDT' ? 'ETHUSDT' : 'BTCUSDT';
  if (mutation === 'audience') request.audience = 'other.tool';
  if (mutation === 'signature') request.lease = {...lease, signature: mutateSignature(lease.signature)};
  return request;
}

/** @param {string} value */
function incrementCent(value) {
  const [whole, fraction = ''] = String(value).split('.');
  const cents = BigInt(whole) * 100n + BigInt((fraction + '00').slice(0, 2));
  const next = cents + 1n;
  return `${next / 100n}.${String(next % 100n).padStart(2, '0')}`;
}

/** @param {string} value */
function mutateSignature(value) {
  if (typeof value !== 'string' || value.length === 0) return 'invalid';
  const last = value.at(-1);
  return value.slice(0, -1) + (last === 'A' ? 'B' : 'A');
}
