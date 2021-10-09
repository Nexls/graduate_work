from datetime import datetime
from typing import Generator
import logging

from psycopg2._psycopg import connection
from psycopg2.extras import DictCursor

from .etltype import ETLType
from ...state import State
from ...utils import coroutine

class Producer:
    """
    Класс Producer выкачивает из БД id'ишники обновленных данных.
    """

    def __init__(self, _type: ETLType, state: State, conn: connection, limit: int = 100):
        self.type = _type
        self.state = state
        self.conn = conn
        self.limit = limit
        self.logger = logging.getLogger(f'{self.__class__.__name__}_{self.type.value}')

    @property
    def modified(self) -> datetime:
        """
        Получение из state актуальной данной обновления данных.
        Если в state нет, то дата обновления становит равной 2000-01-01
        :return:
        """
        modified = self.state.get_state(f'{self.type.value}_modified')
        if not modified:
            modified = datetime(2000, 1, 1).strftime('%Y-%m-%d')
            self.state.set_state(f'{self.type.value}_modified', modified)
        return modified

    @property
    def SQL_modified_ids(self):
        """
        SQL-скрипт получения изменившихся данных от заданой даты.
        :return:
        """
        return f'''
                SELECT id
                FROM content.{self.type.value}
                WHERE modified > \'{self.modified}\'
                ORDER BY modified;
                '''

    @property
    def _sql_script_infomation(self):
        """
        SQL-скрипт для получения полной информации о жанрах и персонах
        :return:
        """
        if self.type is ETLType.GENRE:
            return f'''
                    SELECT id, name, created, modified
                    FROM content.genre
                    WHERE id in (%s);
                    '''
        else:
            return f'''
                    SELECT p.id, p.full_name, p.gender, p.birth_date, p.created, p.modified,
                           array_agg(fwp.profession) as roles,
                           array_agg(fwp.film_work_id) as film_ids
                    FROM content.person as p
                    LEFT JOIN content.film_work_person fwp on p.id = fwp.person_id
                    WHERE p.id in (%s)
                    GROUP BY p.id
                    '''

    @coroutine
    def _get_information_from_type(self) -> Generator:
        ids = None
        while data := (yield ids):
            format_strings = ','.join(['%s'] * len(data))
            updated_ids_list = [r[0] for r in data]
            with self.conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(self._sql_script_infomation % format_strings, updated_ids_list)
                information = cur.fetchall()
            ids = (f'{self.type.value}', information)

    def generate_ids(self, target) -> Generator:
        """
        Получение списка id изменившихся объектов и отправка их в следующий пайплайн target.
        :return: Корутина
        """
        rows_count = 0
        self.logger.info(f'Extract updated_at is {self.modified}')
        with self.conn.cursor(name=f'{self.type.value}_producer') as cur:
            cur.execute(self.SQL_modified_ids)
            while rows := cur.fetchmany(self.limit):
                self.logger.debug(f'Extract Producer {len(rows)} raw rows')
                yield target.send(rows)
                if self.type in [ETLType.GENRE, ETLType.PERSON]:
                    yield self._get_information_from_type().send(rows)
                rows_count += len(rows)
        self.logger.debug(f'Extract raw data count is {rows_count}')
