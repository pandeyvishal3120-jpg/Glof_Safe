from fastapi import APIRouter, Query
from misinformation import verify_claim

router = APIRouter(
    prefix="/misinformation",
    tags=["Misinformation Verification"]
)


@router.get("/verify")
def verify_disaster_claim(
    claim: str = Query(..., min_length=1)
):
    return verify_claim(claim)
