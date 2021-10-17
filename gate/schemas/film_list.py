from fastapi import Query
from pydantic import BaseModel, Field
from settings import LIMIT_PER_PAGE


class FilmRequestBase(BaseModel):
    sort: str = Query(
        default=None,
        description='Поле, по которому будет произведена сортивка. '
                    'Если добавить "-" в начале параметра, то сортировка по desc'
    )
    page_size: int = Query(
        default=LIMIT_PER_PAGE,
        description='Лимит выдачи результатов на странице'
    )
    page_number: int = Query(
        default=0,
        description='Номер страницы результатов'
    )


class FilmFilterRequest(FilmRequestBase):
    filter_genre: str = Field(
        default=None,
        description='Фильтрация по жанру'
    )


class FilmSearchRequest(FilmRequestBase):
    query: str = Query(
        default=None,
        description='Строка поиска по полям: title, description, genre.name, '
                    'actors.full_name, writers.full_name, directors.full_name'
    )
