'use client';

import { useMemo, useState } from 'react';

type VaultResult = {
  vault_id?: string;
  secret_id?: string;
  detail?: string;
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
  const [vaultName, setVaultName] = useState('research-vault');
  const [ownerId, setOwnerId] = useState('local-user');
  const [description, setDescription] = useState('Local encrypted ReliQuary vault');
  const [vaultId, setVaultId] = useState('');
  const [secretName, setSecretName] = useState('database-password');
  const [secretValue, setSecretValue] = useState('replace-with-a-real-secret');
  const [logs, setLogs] = useState<LogEntry[]>([
    {
      label: 'Ready',
      status: 'info',
      body: 'Start the local API, then use this console to create a vault, store a secret, and retrieve metadata.',
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
      return parsed as VaultResult;
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

  async function healthCheck() {
    await callApi('Health check', '/health');
  }

  async function createVault() {
    const result = await callApi('Create vault', '/vaults/', {
      method: 'POST',
      headers: defaultHeaders,
      body: JSON.stringify({
        name: vaultName,
        owner_id: ownerId,
        description,
      }),
    });
    if (result?.vault_id) {
      setVaultId(String(result.vault_id));
    }
  }

  async function listVaults() {
    await callApi('List vaults', `/vaults/?owner_id=${encodeURIComponent(ownerId)}`);
  }

  async function storeSecret() {
    await callApi('Store secret', `/vaults/secrets?vault_id=${encodeURIComponent(vaultId)}`, {
      method: 'POST',
      headers: defaultHeaders,
      body: JSON.stringify({
        secret_name: secretName,
        secret_value: secretValue,
        metadata: { source: 'reliquary-web-console' },
      }),
    });
  }

  async function retrieveSecret() {
    await callApi(
      'Retrieve secret metadata',
      `/vaults/secrets/${encodeURIComponent(secretName)}?vault_id=${encodeURIComponent(vaultId)}`,
    );
  }

  return (
    <main className="shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">ReliQuary</p>
          <h1>Vault Console</h1>
          <p>
            Create encrypted vault records, store secret envelopes, and point the backend at local disk,
            Postgres, or S3-compatible storage.
          </p>
        </div>
        <div className="runBox">
          <strong>Mac quick start</strong>
          <code>./scripts/run_mac_gui.sh</code>
          <code>./scripts/doctor_verbose.sh</code>
          <code>python -m uvicorn apps.api.main:app --reload</code>
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <label>
            Local API URL
            <input value={apiUrl} onChange={(event) => setApiUrl(event.target.value)} />
          </label>
          <button onClick={healthCheck}>Check API</button>
        </header>

        <section className="grid">
          <article className="panel">
            <div className="panelHeader">
              <h2>Vault</h2>
              <button onClick={listVaults}>List</button>
            </div>
            <label>
              Name
              <input value={vaultName} onChange={(event) => setVaultName(event.target.value)} />
            </label>
            <label>
              Owner
              <input value={ownerId} onChange={(event) => setOwnerId(event.target.value)} />
            </label>
            <label>
              Description
              <input value={description} onChange={(event) => setDescription(event.target.value)} />
            </label>
            <button className="primary" onClick={createVault}>Create Vault</button>
            <label>
              Active vault ID
              <input value={vaultId} onChange={(event) => setVaultId(event.target.value)} />
            </label>
          </article>

          <article className="panel">
            <div className="panelHeader">
              <h2>Secret</h2>
              <button onClick={retrieveSecret}>Retrieve</button>
            </div>
            <label>
              Secret name
              <input value={secretName} onChange={(event) => setSecretName(event.target.value)} />
            </label>
            <label>
              Secret value
              <textarea value={secretValue} onChange={(event) => setSecretValue(event.target.value)} />
            </label>
            <button className="primary" onClick={storeSecret}>Store Secret</button>
          </article>
        </section>

        <section className="storage">
          <article>
            <strong>Local folder or external drive</strong>
            <code>RELIQUARY_STORAGE_BACKEND=local</code>
            <code>RELIQUARY_LOCAL_VAULT_PATH="$HOME/ReliQuary Vaults"</code>
          </article>
          <article>
            <strong>Postgres</strong>
            <code>RELIQUARY_STORAGE_BACKEND=postgres</code>
            <code>DATABASE_URL=postgresql://reliquary:reliquary@localhost:5432/reliquary</code>
          </article>
          <article>
            <strong>S3-compatible bucket</strong>
            <code>RELIQUARY_STORAGE_BACKEND=s3</code>
            <code>RELIQUARY_S3_BUCKET=your-bucket</code>
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
