from api.models.properties import Table
from api.services.properties import properties
from fastapi import APIRouter
from fastapi_cache.decorator import cache

router = APIRouter()


@router.get(
    "/",
    status_code=200,
    description="Get table of properties",
)
@cache()
async def get_properties() -> Table:
    return await properties.get_property_entries()


@router.get(
    "/stones/{wall_id}",
    status_code=200,
    description="Get table of stones geometric properties",
)
@cache()
async def get_stone_properties(wall_id: str) -> Table:
    return await properties.get_stones_property_entries(wall_id)
