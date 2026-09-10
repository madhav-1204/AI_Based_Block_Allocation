from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return a lightweight liveness response without requiring the database."""

    return {"status": "healthy", "service": "railopt-ai"}
