# ReliQuary Storage and GUI

ReliQuary can now be used without editing code or memorizing curl commands.

## Native Mac GUI

```bash
./scripts/run_mac_gui.sh
```

The GUI supports:

- Local Mac folder storage, including external drives.
- PostgreSQL storage through `DATABASE_URL`.
- S3-compatible object storage through bucket, region, prefix, endpoint URL, and normal AWS credentials.
- Vault creation, vault listing, secret insert, and secret retrieval.

For a non-technical user, the local folder mode is the default. It writes vault records under `~/ReliQuary Vaults` unless another folder or mounted drive is selected.

## Browser Console

```bash
./scripts/bootstrap_mac.sh
python -m uvicorn apps.api.main:app --reload
npm --prefix website install
npm --prefix website run dev
```

Open `http://localhost:3000` and keep the API at `http://localhost:8000`.

The public Vercel build is a static control surface and project entrypoint. For live vault actions against a laptop, run the website locally so browser security policies do not block local API calls from a hosted HTTPS page.

## Storage Modes

Local Mac folder:

```bash
export RELIQUARY_STORAGE_BACKEND=local
export RELIQUARY_LOCAL_VAULT_PATH="$HOME/ReliQuary Vaults"
python -m uvicorn apps.api.main:app --reload
```

Postgres:

```bash
export RELIQUARY_STORAGE_BACKEND=postgres
export DATABASE_URL="postgresql://reliquary:reliquary@localhost:5432/reliquary"
python -m uvicorn apps.api.main:app --reload
```

S3-compatible bucket:

```bash
export RELIQUARY_STORAGE_BACKEND=s3
export RELIQUARY_S3_BUCKET="your-bucket"
export RELIQUARY_S3_REGION="us-east-1"
export RELIQUARY_S3_PREFIX="reliquary"
export RELIQUARY_S3_ENDPOINT_URL="https://optional-s3-compatible-endpoint"
python -m uvicorn apps.api.main:app --reload
```

Production S3 credentials should come from AWS SSO, IAM role, or a secret manager. Do not commit access keys.

## Verbose Verification

```bash
./scripts/doctor_verbose.sh
```

The doctor script prints every stage and writes a full log under `logs/`.
