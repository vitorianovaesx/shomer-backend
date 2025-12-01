"""FastAPI application."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Header, status
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from internal.config import load_config
from internal.pipeline import IngestionPipeline
from internal.store.case_store import CaseStore
from internal.store.vault import Vault


class IngestRequest(BaseModel):
    """Ingest request model."""

    url: str


class IngestResponse(BaseModel):
    """Ingest response model."""

    case_id: str
    status: str


# Global pipeline instance
pipeline: IngestionPipeline = None
config = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global pipeline, config
    config = load_config()
    pipeline = IngestionPipeline(config)
    yield
    await pipeline.close()


app = FastAPI(
    title="Shomer Backend API",
    description="Content ingestion, classification, and case management",
    version="0.1.0",
    lifespan=lifespan,
)


def verify_admin_token(authorization: str = Header(None)) -> bool:
    """Verify admin token."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
        )

    token = authorization.replace("Bearer ", "")
    if token != config.api.admin_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin token",
        )

    return True


@app.get("/healthz")
async def healthcheck():
    """Health check endpoint."""
    return {"status": "ok", "service": "shomer-backend"}


@app.post("/ingest", response_model=IngestResponse)
async def ingest(request: IngestRequest):
    """Ingest a URL and create a case."""
    try:
        case_id = await pipeline.ingest(request.url)
        return IngestResponse(case_id=case_id, status="created")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest URL: {str(e)}",
        )


@app.get("/cases/{case_id}/pack.zip")
async def get_pack(case_id: str):
    """Get case pack ZIP file."""
    case_store = CaseStore(Path(config.storage.sqlite_path))
    case = case_store.get_case(case_id)

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {case_id} not found",
        )

    pack_path = Path(case.get("pack_path"))
    if not pack_path or not pack_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pack for case {case_id} not found",
        )

    return FileResponse(
        pack_path,
        media_type="application/zip",
        filename=f"case_{case_id}_pack.zip",
    )


@app.post("/cases/{case_id}/request_vault_access")
async def request_vault_access(case_id: str, authorization: str = Header(None)):
    """Request vault access for a case (admin only)."""
    verify_admin_token(authorization)

    case_store = CaseStore(Path(config.storage.sqlite_path))
    case = case_store.get_case(case_id)

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {case_id} not found",
        )

    # Get artifacts with vault references
    artifacts = case_store.get_artifacts(case_id)
    vault_refs = [
        {
            "artifact_id": a["artifact_id"],
            "artifact_type": a["artifact_type"],
            "vault_ref": a.get("vault_ref"),
        }
        for a in artifacts
        if a.get("vault_ref")
    ]

    return JSONResponse(
        content={
            "case_id": case_id,
            "vault_references": vault_refs,
            "message": "Vault access granted. Use admin CLI to retrieve content.",
        }
    )


@app.get("/cases/{case_id}")
async def get_case(case_id: str):
    """Get case details."""
    case_store = CaseStore(Path(config.storage.sqlite_path))
    case = case_store.get_case(case_id)

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {case_id} not found",
        )

    artifacts = case_store.get_artifacts(case_id)
    return JSONResponse(
        content={
            **case,
            "artifacts": [
                {
                    "artifact_id": a["artifact_id"],
                    "type": a["artifact_type"],
                    "path": a["path"],
                    "hash": a["hash"],
                }
                for a in artifacts
            ],
        }
    )


