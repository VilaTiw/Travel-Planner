import httpx
from fastapi import HTTPException

ART_API_BASE_URL = "https://api.artic.edu/api/v1/artworks"


async def validate_place_exists(external_id: str):
    """Fetches the third-party API to ensure the place exists."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ART_API_BASE_URL}/{external_id}")

        if response.status_code == 404:
            raise HTTPException(status_code=400, detail=f"Place with external ID '{external_id}' not found in Art API.")
        elif response.status_code != 200:
            raise HTTPException(status_code=502, detail="Error communicating with third-party Art API.")

        return True