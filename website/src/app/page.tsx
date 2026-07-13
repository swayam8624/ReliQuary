'use client';

import { useMemo, useState } from 'react';

type ApiResult = {
  vault_id?: string;
  decision?: 'allow' | 'redact' | 'deny';
  visible_result?: string;
  trust_score?: number;
  required_score?: number;
  reasons?: string[];
  revealed_value?: string | null;
  [key: string]: unknown;
};

type LogEntry = {
  label: string;
  status: 'ok' | 'error' | 'info';
  body: string;
};

const defaultHeaders = { 'Content-Type': 'application/json' };

export default function Home() {
  const [apiUrl, setApiUrl] = useState(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');
  const [vaultName, setVaultName] = useState('brain-vault');
  const [ownerId, setOwnerId] = useState('alice');
  const [description, setDescription] = useState('Local trusted memory vault');
  const [vaultId, setVaultId] = useState('');
  const [secretName, setSecretName] = useState('apple-password-note');
  const [secretValue, setSecretValue] = useState('replace-with-a-real-secret');
  const [requestUser, setRequestUser] = useState('alice');
  const [trustScore, setTrustScore] = useState(95);
  const [sensitivity, setSensitivity] = useState('secret');
  const [remoteAddress, setRemoteAddress] = useState('127.0.0.1');
  const [deviceVerified, setDeviceVerified] = useState(true);
  const [localSession, setLocalSession] = useState(true);
  const [biometricVerified, setBiometricVerified] = useState(true);
  const [decision, setDecision] = useState<ApiResult | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([
    {
      label: 'Ready',
      status: 'info',
      body: 'Create a vault, store a secret, then evaluate high-trust and low-trust requests.',
    },
  ]);

  const normalizedApiUrl = useMemo(() => apiUrl.replace(/\/$/, ''), [apiUrl]);

  async function callApi(label: string, path: string, init?: RequestInit) {
    try {
      const response = await fetch(`${normalizedApiUrl}${path}`, init);
      const text = await response.text();
      const parsed = text ? JSON.parse(text) : {};
      if (!response.ok) {
        throw new Error(JSON.stringify(parsed, null, 2));
      }
      setLogs((current) => [{ label, status: 'ok', body: JSON.stringify(parsed, null, 2) }, ...current]);
      return parsed as ApiResult;
    } catch (error) {
      setLogs((current) => [
        {
          label,
          status: 'error',
          body: error instanceof Error ? error.message : String(error),
        },
        ...current,
      ]);
      return null;
    }
  }

  async function createVault() {
    const result = await callApi('Create vault', '/vaults/', {
      method: 'POST',
      headers: defaultHeaders,
      body: JSON.stringify({ name: vaultName, owner_id: ownerId, description }),
    });
    if (result?.vault_id) {
      setVaultId(String(result.vault_id));
    }
  }

  async function storeSecret() {
    await callApi('Store secret envelope', `/vaults/secrets?vault_id=${encodeURIComponent(vaultId)}`, {
      method: 'POST',
      headers: defaultHeaders,
      body: JSON.stringify({
        secret_name: secretName,
        secret_value: secretValue,
        metadata: { source: 'reliquary-web-console', sensitivity },
      }),
    });
  }

  async function requestSecret() {
    const result = await callApi('Trust-gated request', '/access/request-secret', {
      method: 'POST',
      headers: defaultHeaders,
      body: JSON.stringify({
        vault_id: vaultId,
        resource_name: secretName,
        sensitivity,
        trust_score: trustScore,
        subject: {
          user_id: requestUser,
          device_verified: deviceVerified,
          local_session: localSession,
          biometric_verified: biometricVerified,
          remote_address: remoteAddress,
          user_agent: 'reliquary-web-console',
        },
      }),
    });
    if (result) {
      setDecision(result);
    }
  }

  async function simulateAttacker() {
    setRequestUser('remote-script');
    setTrustScore(30);
    setRemoteAddress('203.0.113.10');
    setDeviceVerified(false);
    setLocalSession(false);
    setBiometricVerified(false);
  }

  const decisionClass = decision?.decision || 'idle';

  return (
    <main className="shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">ReliQuary</p>
          <h1>Brain Vault</h1>
          <p>
            A local trusted memory vault: store secrets, ask for them, and watch the trust gate decide
            whether to reveal, redact, or deny.
          </p>
        </div>
        <div className="runBox">
          <strong>Mac quick start</strong>
          <code>./scripts/run_mac_gui.sh</code>
          <code>python -m uvicorn apps.api.main:app --reload</code>
          <code>cmake -S visualizer/vulkan -B visualizer/vulkan/build</code>
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <label>
            Local API URL
            <input value={apiUrl} onChange={(event) => setApiUrl(event.target.value)} />
          </label>
          <button onClick={() => callApi('Health check', '/health')}>Check API</button>
        </header>

        <section className="brain">
          <div className="node storage">Storage</div>
          <div className="edge" />
          <div className={`node gate ${decisionClass}`}>
            <strong>{decision?.decision?.toUpperCase() || 'TRUST GATE'}</strong>
            <span>
              {decision ? `${decision.trust_score}/${decision.required_score} trust` : 'waiting for request'}
            </span>
          </div>
          <div className="edge" />
          <div className="node answer">
            {decision?.decision === 'allow' && 'Secret revealed'}
            {decision?.decision === 'redact' && 'Metadata only'}
            {decision?.decision === 'deny' && 'No disclosure'}
            {!decision && 'Answer'}
          </div>
        </section>

        <section className="grid">
          <article className="panel">
            <div className="panelHeader">
              <h2>Vault Setup</h2>
              <button onClick={createVault}>Create</button>
            </div>
            <label>Name<input value={vaultName} onChange={(event) => setVaultName(event.target.value)} /></label>
            <label>Owner<input value={ownerId} onChange={(event) => setOwnerId(event.target.value)} /></label>
            <label>Description<input value={description} onChange={(event) => setDescription(event.target.value)} /></label>
            <label>Active vault ID<input value={vaultId} onChange={(event) => setVaultId(event.target.value)} /></label>
          </article>

          <article className="panel">
            <div className="panelHeader">
              <h2>Secret</h2>
              <button onClick={storeSecret}>Store</button>
            </div>
            <label>Secret name<input value={secretName} onChange={(event) => setSecretName(event.target.value)} /></label>
            <label>Secret value<textarea value={secretValue} onChange={(event) => setSecretValue(event.target.value)} /></label>
            <label>
              Sensitivity
              <select value={sensitivity} onChange={(event) => setSensitivity(event.target.value)}>
                <option value="public">public</option>
                <option value="private">private</option>
                <option value="sensitive">sensitive</option>
                <option value="secret">secret</option>
                <option value="sealed">sealed</option>
              </select>
            </label>
          </article>
        </section>

        <section className="grid">
          <article className="panel">
            <div className="panelHeader">
              <h2>Request Context</h2>
              <button onClick={simulateAttacker}>Remote Deny</button>
            </div>
            <label>Requesting user<input value={requestUser} onChange={(event) => setRequestUser(event.target.value)} /></label>
            <label>Remote address<input value={remoteAddress} onChange={(event) => setRemoteAddress(event.target.value)} /></label>
            <label>Trust score<input type="number" min="0" max="100" value={trustScore} onChange={(event) => setTrustScore(Number(event.target.value))} /></label>
            <div className="checks">
              <label><input type="checkbox" checked={deviceVerified} onChange={(event) => setDeviceVerified(event.target.checked)} /> Device</label>
              <label><input type="checkbox" checked={localSession} onChange={(event) => setLocalSession(event.target.checked)} /> Local</label>
              <label><input type="checkbox" checked={biometricVerified} onChange={(event) => setBiometricVerified(event.target.checked)} /> Biometric</label>
            </div>
            <button className="primary" onClick={requestSecret}>Ask Brain Vault</button>
          </article>

          <article className={`decisionCard ${decisionClass}`}>
            <h2>Decision</h2>
            <strong>{decision?.decision?.toUpperCase() || 'NO REQUEST YET'}</strong>
            <p>{decision?.visible_result || 'Create a request to see what the vault will disclose.'}</p>
            {decision?.revealed_value ? <pre>{decision.revealed_value}</pre> : null}
            <ul>
              {(decision?.reasons || []).map((reason) => <li key={reason}>{reason}</li>)}
            </ul>
          </article>
        </section>

        <section className="logs">
          <h2>Result Log</h2>
          {logs.map((entry, index) => (
            <article className={`log ${entry.status}`} key={`${entry.label}-${index}`}>
              <strong>{entry.label}</strong>
              <pre>{entry.body}</pre>
            </article>
          ))}
        </section>
      </section>
    </main>
  );
}
