from typing import Annotated

from fastapi import APIRouter, Depends
from fastcrud import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...crud.crud_rate_limit import crud_rate_limits
from ...schemas.rate_limit import RateLimitRead

router = APIRouter(tags=["rate_limits"])


@router.get("/rate_limits", response_model=PaginatedListResponse[RateLimitRead])
async def read_rate_limits(
    db: Annotated[AsyncSession, Depends(async_get_db)], page: int = 1, items_per_page: int = 10
) -> dict:
    rate_limits_data = await crud_rate_limits.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=RateLimitRead,
    )

    return paginated_response(crud_data=rate_limits_data, page=page, items_per_page=items_per_page)