from fastapi import Query
from pydantic import BaseModel
from services.query_constructor import LIMIT_PER_PAGE


class PersonRequestBase(BaseModel):
    page_size: int = Query(
        default=LIMIT_PER_PAGE,
        description='Лимит выдачи результатов на странице'
    )
    page_number: int = Query(
        default=0,
        description='Номер страницы результатов'
    )


class PersonSearchRequest(PersonRequestBase):
    query: str = Query(
        default=None,
        description='Строка поиска по полям: full_name'
    )
