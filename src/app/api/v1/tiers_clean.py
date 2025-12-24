from typing import Annotated

from fastapi import APIRouter, Depends
from fastcrud import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...crud.crud_tier import crud_tiers
from ...schemas.tier import TierRead

router = APIRouter(tags=["tiers"])


@router.get("/tiers", response_model=PaginatedListResponse[TierRead])
async def read_tiers(
    db: Annotated[AsyncSession, Depends(async_get_db)], page: int = 1, items_per_page: int = 10
) -> dict:
    tiers_data = await crud_tiers.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=TierRead,
    )

    return paginated_response(crud_data=tiers_data, page=page, items_per_page=items_per_page)


@router.get("/tier/{name}", response_model=TierRead)
async def read_tier(name: str, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict:
    db_tier = await crud_tiers.get(db=db, name=name, schema_to_select=TierRead)
    if db_tier is None:
        from ...core.exceptions.http_exceptions import NotFoundException
        raise NotFoundException("Tier not found")

    return db_tier