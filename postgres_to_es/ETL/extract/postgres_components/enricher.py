import logging
from typing import Generator

from psycopg2._psycopg import connection

from ...state import State
from .etltype import ETLType
from ...utils import coroutine


class Enricher:
    """
    Класс Enricher получает список id'ишников фильмов, связанных с обновляемыми данными.
    """
    def __init__(self, _type: ETLType, state: State, conn: connection, limit: int = 100):
        self.type = _type
        self.state = state
        self.conn = conn
        self.limit = limit
        self.logger = logging.getLogger(f'{self.__class__.__name__}_{self.type.value}')

    @property
    def SQL_enrich(self) -> str:
        """
        Возращает SQL запрос, который имеет смысл выполнять только для person и genre.
        :return:
        """
        return f'''
                SELECT DISTINCT film_work_id 
                FROM content.film_work_{self.type.value}
                WHERE {self.type.value}_id in (%s)
                '''

    @coroutine
    def enrich(self, target) -> Generator:
        """
        Обогатитель данных для person и genre. Берет из таблици соотношение film_work_TYPE id'ишники связанных фильмов.
        Для ETLType.FILM_WORK ничего не делает и присваивает списку фильмов переданные id'ишники.
        :param target:
        :return:
        """
        film_ids = None
        while data := (yield film_ids):
            if self.type is not ETLType.FILM_WORK:
                format_strings = ','.join(['%s'] * len(data))
                updated_ids_list = [r[0] for r in data]
                with self.conn.cursor() as cur:
                    cur.execute(self.SQL_enrich % format_strings, updated_ids_list)
                    film_ids = cur.fetchall()
            else:
                film_ids = data
            self.logger.debug(f'Extract Enricher {len(film_ids)} raw rows')
            film_ids = target.send(film_ids)
