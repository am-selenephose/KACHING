/** Display only: never convert financial values to binary floating point.
 * @param {string | null | undefined} value
 */
export function formatAmount(value) {
  if (value == null) return '—';
  const [integer, fraction = ''] = value.split('.');
  return `${integer.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}.${fraction.padEnd(2, '0')}`;
}

/** A draft is not authorization. The caller must clear old evidence and recompile.
 * @param {{mode:string, verdict:string, safe_envelope:string|null, reasons:string[]} | null} receipt
 * @returns {string | null}
 */
export function admissibleDraft(receipt) {
  return receipt?.mode === 'fixture' && receipt.verdict === 'REVIEW'
    && receipt.reasons.includes('REQUEST_EXCEEDS_SAFE_ENVELOPE')
    ? receipt.safe_envelope : null;
}
