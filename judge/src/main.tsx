import {useEffect, useMemo, useState} from 'react';
import {createRoot} from 'react-dom/client';
import './proof.css';

type Receipt = {
  verdict: 'BLOCK'|'REVIEW'|'ALLOW'; requested: string; authorized: string;
  safe_envelope: string|null; action: string; symbol: string; reasons: string[];
  determining_rules: string[]; policy_version: string; policy_sha256: string;
  decision_sha256: string; proposal_id: string; mode: string;
};
type Lease = Record<string, string>;
type Scenario = {receipt: Receipt; verified: boolean; authorization_lease: Lease|null; issuer: Record<string,string>|null};
type Evidence = {
  meta: {schema: string; mode: string; live_execution: boolean; recorded_at: string; source_commit: string; disclaimer: string};
  scenarios: Record<'block'|'review'|'allow', Scenario>;
  lease_specimen: Lease;
  policy_arena: {passed: number; total: number; attacks: {name: string; contained: boolean; detail: string}[]};
  enforcement_arena: {baseline: string; passed: number; total: number; bypasses: {name: string; rejected: boolean; reason: string}[]};
  proof_counts: {python_tests: number; ui_tests: number; browser_checks: number; responsive_checks: number; policy_attacks: string; authorization_bypasses: string};
};

const SOURCE = 'https://gitlab.com/am.statementforge/kaching';
const SUBMITTED_SOURCE = 'https://github.com/am-selenephos/KACHING';
const VIDEO = 'https://x.com/Selenephose/status/2097472059890905444';
const SUBMISSION = 'https://x.com/Selenephose/status/2097472059890905444';
const VERIFY = `${SOURCE}/-/blob/main/docs/VERIFICATION.md`;
const SUBMISSION_SNAPSHOT = '052af0841e17596958953f038c7b782ad4defe74';
const short = (value?: string) => !value ? '—' : value.length < 30 ? value : `${value.slice(0, 14)}…${value.slice(-10)}`;

function App() {
  const [evidence, setEvidence] = useState<Evidence|null>(null);
  const [scenario, setScenario] = useState<'block'|'review'|'allow'>('allow');
  const [error, setError] = useState('');
  useEffect(() => {
    fetch('/evidence.json', {cache: 'no-store'}).then(async response => {
      if (!response.ok) throw new Error(`Evidence unavailable (${response.status})`);
      return response.json();
    }).then(setEvidence).catch(err => setError(err instanceof Error ? err.message : 'Evidence unavailable'));
  }, []);

  const selected = evidence?.scenarios[scenario];
  const receipt = selected?.receipt;
  const verdictClass = receipt?.verdict.toLowerCase() || 'none';
  const proofItems = useMemo(() => evidence ? [
    [`${evidence.proof_counts.python_tests}`, 'Python tests'],
    [`${evidence.proof_counts.ui_tests}`, 'UI tests'],
    [evidence.proof_counts.policy_attacks, 'policy attacks contained'],
    [evidence.proof_counts.authorization_bypasses, 'authorization bypasses rejected'],
    [`${evidence.proof_counts.browser_checks}/26`, 'browser checks'],
  ] : [], [evidence]);

  return <main className="shell" data-verdict={verdictClass}>
    <div className="ambient" aria-hidden="true" />
    <header className="topbar">
      <a className="brand" href="#top">KACHING!</a>
      <div className="edition">BINANCE AGENT OS · TRACK A</div>
      <nav>
        <a href={SOURCE}>Public source ↗</a>
        <a href={SUBMITTED_SOURCE}>Submitted GitHub ↗</a>
        <a href={VIDEO}>98s demo ↗</a>
        <a href={SUBMISSION}>Submission ↗</a>
        <a href={VERIFY}>Verification ↗</a>
      </nav>
    </header>

    <section className="hero" id="top">
      <p className="eyebrow">PROOF-CARRYING FINANCIAL AUTHORIZATION</p>
      <h1>Before an AI can touch money,<br/><span>it must carry proof.</span></h1>
      <p className="thesis">Capability is not authorization.</p>
      <p className="sub">An AI can propose an action. KACHING decides whether authority exists, issues it only for the exact permitted action, and rejects changed, expired, or replayed authority.</p>
      <div className="hero-actions">
        <a className="primary" href="#proof">Explore the proof ↓</a>
        <a href={VIDEO}>Watch the 98-second demo ↗</a>
      </div>
      <div className="boundary">RECORDED DETERMINISTIC FIXTURES · NO WALLET · NO MONEY MOVED · CORE KERNEL LIVES IN REPO</div>
      <div className="snapshot-note"><strong>SUBMISSION SNAPSHOT</strong><code>{SUBMISSION_SNAPSHOT.slice(0, 8)}</code><span>captured before the deadline · later commits are judge-access / presentation hardening</span></div>
    </section>

    {error && <div className="error">{error}</div>}
    {!evidence && !error && <div className="loading">Loading recorded evidence…</div>}

    {evidence && <>
      <section className="proof-strip" aria-label="Verification counts">
        {proofItems.map(([value,label]) => <div key={label}><strong>{value}</strong><span>{label}</span></div>)}
      </section>

      <section className="pipeline" aria-label="Authorization pipeline">
        <span>AI proposes</span><i>→</i><span>KACHING decides</span><i>→</i><span>ALLOW issues signed authority</span><i>→</i><span>VALID / REJECTED</span>
      </section>

      <section className="explorer" id="proof">
        <div className="section-head">
          <div><p className="eyebrow">01 · DECISION PROOF</p><h2>Authority is an artifact,<br/>not an opinion.</h2></div>
          <p>Three recorded fixture outcomes from the real KACHING kernel. Switch them without granting this hosted page any financial capability.</p>
        </div>
        <div className="scenario-tabs" role="tablist" aria-label="Fixture scenario">
          {(['block','review','allow'] as const).map(key => <button key={key} className={scenario === key ? 'active' : ''} onClick={() => setScenario(key)}>{key.toUpperCase()}</button>)}
        </div>
        {receipt && <div className="decision-grid">
          <article className="decision-card">
            <p className="label">VERDICT</p>
            <div className={`verdict ${verdictClass}`}>{receipt.verdict}</div>
            <dl>
              <div><dt>Requested</dt><dd>{receipt.requested} USDT</dd></div>
              <div><dt>Authorized</dt><dd>{receipt.authorized} USDT</dd></div>
              <div><dt>Safe envelope</dt><dd>{receipt.safe_envelope ? `${receipt.safe_envelope} USDT` : 'none'}</dd></div>
              <div><dt>Action</dt><dd>{receipt.action} · {receipt.symbol}</dd></div>
            </dl>
          </article>
          <article className="rules-card">
            <p className="label">DETERMINING RULES</p>
            <div className="rule-list">{receipt.determining_rules.map(rule => <code key={rule}>{rule}</code>)}</div>
            <p className="label second">WHY</p>
            <ul>{receipt.reasons.map(reason => <li key={reason}>{reason}</li>)}</ul>
            <div className="hash"><span>Decision SHA</span><code>{short(receipt.decision_sha256)}</code></div>
            <div className="hash"><span>Policy SHA</span><code>{short(receipt.policy_sha256)}</code></div>
          </article>
        </div>}
      </section>

      <section className="lease-section">
        <div className="section-head">
          <div><p className="eyebrow">02 · SIGNED AUTHORITY</p><h2>ALLOW carries its own boundary.</h2></div>
          <p>This is a recorded Ed25519 Authorization Lease specimen. It is KACHING authority, not a Binance-native token.</p>
        </div>
        <div className="lease-card">
          <div className="lease-title"><span>AUTHORIZATION LEASE</span><strong>Ed25519</strong></div>
          <div className="lease-grid">
            {[
              ['Action', evidence.lease_specimen.action], ['Resource', evidence.lease_specimen.resource],
              ['Ceiling', `${evidence.lease_specimen.maximum_authorized} USDT`], ['Audience', evidence.lease_specimen.audience],
              ['Policy', short(evidence.lease_specimen.policy_sha256)], ['Evidence', short(evidence.lease_specimen.observation_commitment)],
              ['Issuer', short(evidence.lease_specimen.issuer_key_fingerprint)], ['Signature', short(evidence.lease_specimen.signature)],
            ].map(([label,value]) => <div key={label}><span>{label}</span><code>{value}</code></div>)}
          </div>
        </div>
      </section>

      <section className="gauntlet">
        <div className="section-head">
          <div><p className="eyebrow">03 · ENFORCEMENT PROOF</p><h2>Exact action: {evidence.enforcement_arena.baseline}.<br/>Seven bypasses: rejected.</h2></div>
          <div className="score">{evidence.enforcement_arena.passed}<small>/ {evidence.enforcement_arena.total}</small></div>
        </div>
        <div className="bypass-grid">
          {evidence.enforcement_arena.bypasses.map((row,index) => <article key={row.name}>
            <span className="num">0{index+1}</span><div><strong>{row.name}</strong><code>{row.reason}</code></div><b>{row.rejected ? 'REJECTED' : 'CHECK'}</b>
          </article>)}
        </div>
        <p className="interpretation">VALID here means the KACHING verifier accepted the exact recorded action. It does not mean Binance executed a trade.</p>
      </section>

      <section className="judge-path">
        <p className="eyebrow">30-SECOND JUDGE PATH</p>
        <ol><li>Switch BLOCK → REVIEW → ALLOW.</li><li>Inspect the signed exact-action lease.</li><li>Read the seven mutation/replay rejection reasons.</li><li>Open the repo for the real Python kernel, tests, and security boundary.</li></ol>
        <div className="judge-links"><a className="primary" href={SOURCE}>Open source ↗</a><a href={VERIFY}>Read verification ↗</a></div>
      </section>

      <footer><span>KACHING! · LLMs propose. KACHING! authorizes.</span><code>Evidence source {short(evidence.meta.source_commit)}</code></footer>
    </>}
  </main>;
}

createRoot(document.getElementById('root')!).render(<App />);
