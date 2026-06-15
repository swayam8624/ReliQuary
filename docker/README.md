# Docker

Run the local research stack:

```bash
docker compose -f docker/docker-compose.yml up --build
```

- API: http://localhost:8000/docs
- Website: http://localhost:3000
- Postgres: `localhost:5432`

Start only Postgres for local development:

```bash
docker compose -f docker/docker-compose.yml up -d postgres
```

Then run:

```bash
RELIQUARY_STORAGE_BACKEND=postgres \
DATABASE_URL=postgresql://reliquary:reliquary-dev-password@localhost:5432/reliquary \
python scripts/postgres_vault_flow.py
```
