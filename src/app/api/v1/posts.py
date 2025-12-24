from typing import Annotated

from fastapi import APIRouter, Depends
from fastcrud import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...crud.crud_posts import crud_posts
from ...schemas.post import PostRead

router = APIRouter(tags=["posts"])


@router.get("/posts", response_model=PaginatedListResponse[PostRead])
async def read_posts(
    db: Annotated[AsyncSession, Depends(async_get_db)], page: int = 1, items_per_page: int = 10
) -> dict:
    posts_data = await crud_posts.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=PostRead,
    )

    return paginated_response(crud_data=posts_data, page=page, items_per_page=items_per_page)