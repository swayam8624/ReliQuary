'use client';

import { useMemo, useState } from 'react';

type ResearchRequestState = {
  name: string;
  owner: string;
  secretName: string;
  secretValue: string;
};

export default function Home() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const [state, setState] = useState<ResearchRequestState>({
    name: 'research-vault',
    owner: 'alice',
    secretName: 'api-token',
    secretValue: 'sk-research-keep-this-private',
  });

  const curl = useMemo(() => {
    const body = JSON.stringify({
      name: state.name,
      description: 'Local ReliQuary research vault',
      owner_id: state.owner,
    });
    return `curl -s -X POST ${apiUrl}/vaults/ \\
  -H 'Content-Type: application/json' \\
  -d '${body}'`;
  }, [apiUrl, state.name, state.owner]);

  return (
    <main className="shell">
      <section className="hero">
        <nav className="nav">
          <strong>ReliQuary</strong>
          <a href="#run">Run locally</a>
        </nav>

        <div className="heroGrid">
          <div>
            <h1>Context-bound storage for secrets you do not want sitting loose.</h1>
            <p className="lead">
              ReliQuary is an open-source research system: create encrypted vault records,
              attach secrets, score context, route decisions through agents, and keep a
              Merkle-style audit trail.
            </p>
            <div className="actions">
              <a className="button" href="#run">Try the local API</a>
              <a className="button secondary" href="https://github.com/SwayamSingal/ReliQuary">Source</a>
            </div>
          </div>

          <div className="panel">
            <div className="panelHeader">Local research flow</div>
            <ol>
              <li>Create a vault for an owner.</li>
              <li>Verify access context and trust.</li>
              <li>Route sensitive access through API and agent surfaces.</li>
            </ol>
          </div>
        </div>
      </section>

      <section className="section" id="run">
        <div>
          <h2>Clone, run, see a result</h2>
          <p>
            Start the FastAPI service and use the docs. The website stays intentionally small;
            the backend is the research system.
          </p>
        </div>
        <pre><code>{`python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn apps.api.main:app --reload`}</code></pre>
      </section>

      <section className="section two">
        <div className="card">
          <h2>Generate a vault request</h2>
          <label>
            Vault name
            <input value={state.name} onChange={(event) => setState({ ...state, name: event.target.value })} />
          </label>
          <label>
            Owner
            <input value={state.owner} onChange={(event) => setState({ ...state, owner: event.target.value })} />
          </label>
          <label>
            Secret name
            <input value={state.secretName} onChange={(event) => setState({ ...state, secretName: event.target.value })} />
          </label>
          <label>
            Secret value
            <input value={state.secretValue} onChange={(event) => setState({ ...state, secretValue: event.target.value })} />
          </label>
        </div>

        <div className="card dark">
          <h2>Request</h2>
          <pre><code>{curl}</code></pre>
          <p>
            API docs are available at <code>{apiUrl}/docs</code> after the backend starts.
          </p>
        </div>
      </section>

      <section className="section">
          <h2>What problem this research targets</h2>
          <p>
            Normal apps often treat secrets as plain rows in a database. ReliQuary explores a stricter
            pattern: encrypted vault objects, auditable access events, and policy/context checks before
            a secret is released. The current repo is a research prototype, not a finished hosted product.
          </p>
      </section>
    </main>
  );
}
