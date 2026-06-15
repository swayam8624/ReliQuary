# ReliQuary Website

Minimal companion UI for the ReliQuary research API.

This is not the product by itself. It is a small local surface that explains the
system and generates starter requests for the FastAPI backend.

```bash
npm install
npm run dev
```

Open http://localhost:3000.

Use `NEXT_PUBLIC_API_URL` when the backend is not on port 8000:

```bash
NEXT_PUBLIC_API_URL=http://localhost:9000 npm run dev
```
