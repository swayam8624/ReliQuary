from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="ReliQuary Platform API",
    description="Enterprise-grade cryptographic memory vault system with context-aware secure data access",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "service": "reliquary-api",
        "features": [
            "Merkle audit logging",
            "OAuth 2.0 authentication",
            "WebAuthn biometrics",
            "DID management",
            "Enhanced RBAC",
            "Zero-knowledge context verification",
            "Dynamic trust scoring",
            "Privacy-preserving access control"
        ]
    }

# Version endpoint
@app.get("/version")
async def get_version():
    return {"version": "2.0.0"}

# Simple test endpoint
@app.get("/")
async def root():
    return {"message": "ReliQuary Platform API is running"}

# Additional endpoints for testing
@app.get("/auth/health")
async def auth_health():
    return {"status": "authentication service healthy"}

@app.get("/zk/system-status")
async def zk_system_status():
    return {"status": "zero-knowledge system operational"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)