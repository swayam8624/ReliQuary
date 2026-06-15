"""Compatibility entrypoint for local hosts that import ``main:app``.

The real application lives in ``apps.api.main``. Keep this tiny shim so older
Procfiles and quick demos still start the same FastAPI app.
"""

from apps.api.main import app


if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
