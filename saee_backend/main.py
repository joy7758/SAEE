"""FastAPI entrypoint for the SAEE MVP API shell."""

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from saee_backend.api.audit import request_audit_middleware
from saee_backend.api.commercial import router as commercial_router
from saee_backend.api.experiment import router as experiment_router
from saee_backend.api.operations import router as operations_router
from saee_backend.api.readiness import router as readiness_router
from saee_backend.api.security import require_api_key, require_jwt_preview_auth, require_rbac_route
from saee_backend.config import SETTINGS


app = FastAPI(
    title="SAEE MVP API",
    description="Black-box long-term competition evaluator for AI systems.",
    version="1.0.0-mvp-shell",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(SETTINGS.allowed_origins),
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-SAEE-API-Key",
        "X-SAEE-Tenant-ID",
        "X-SAEE-Role",
    ],
)

app.include_router(experiment_router, prefix="/experiment", tags=["experiment"])
app.include_router(operations_router, prefix="/operations", tags=["operations"])
app.include_router(readiness_router, prefix="/readiness", tags=["readiness"])
app.include_router(commercial_router, prefix="/commercial", tags=["commercial"])
app.middleware("http")(request_audit_middleware)


@app.exception_handler(RequestValidationError)
async def sanitized_request_validation_error(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Return validation locations and messages without reflecting inputs."""

    details = [
        {
            "type": str(error.get("type", "value_error")),
            "loc": list(error.get("loc", ())),
            "msg": str(error.get("msg", "Invalid request.")),
        }
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": details})


@app.get(
    "/health",
    dependencies=[
        Depends(require_api_key),
        Depends(require_jwt_preview_auth),
        Depends(require_rbac_route("GET /health")),
    ],
)
def health() -> dict[str, str]:
    return {"status": "ok", "probe_scope": "minimal_non_tenant"}


@app.get(
    "/ready",
    dependencies=[
        Depends(require_api_key),
        Depends(require_jwt_preview_auth),
        Depends(require_rbac_route("GET /ready")),
    ],
)
def ready() -> dict[str, object]:
    return {**SETTINGS.readiness_payload(), "probe_scope": "configuration_non_tenant"}
