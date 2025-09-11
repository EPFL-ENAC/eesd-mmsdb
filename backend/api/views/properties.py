from fastapi import APIRouter

from api.services.properties import Properties
from api.models.properties import Property


router = APIRouter()
properties = Properties()


@router.get(
    "/",
    status_code=200,
    description="Get table of properties",
)
async def get_properties() -> list[list[Property]]:
    return await properties.get_property_entries()


@router.get(
    "/stones/{wall_id}",
    status_code=200,
    description="Get table of stones geometric properties",
)
async def get_stone_properties(wall_id: str) -> list[list[Property]]:
    return await properties.get_stones_property_entries(wall_id)
