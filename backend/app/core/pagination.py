from typing import Annotated

from fastapi import Query


class PaginationParams:
    """Compatible offset pagination for collection endpoints."""

    def __init__(
        self,
        skip: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=100)] = 100,
    ) -> None:
        self.skip = skip
        self.limit = limit
