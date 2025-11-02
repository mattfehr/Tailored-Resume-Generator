from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["Health"])
async def health_check():
    """Simple health endpoint to verify backend is alive."""
    return {"status": "ok", "message": "ResuMatch AI backend running"}
