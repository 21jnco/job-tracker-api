from dataclasses import dataclass

from fastapi import Query
from sqlalchemy import Select


@dataclass
class PaginationParams:
    limit: int
    offset: int


def get_pagination_params(
        limit: int = Query(default=10, ge=1, le=100),
        offset: int = Query(default=0, gt=0)
) -> PaginationParams:
    return PaginationParams(limit=limit, offset=offset)


def apply_pagination(query: Select, pagination: PaginationParams):
    return query.offset(pagination.offset).limit(pagination.limit)