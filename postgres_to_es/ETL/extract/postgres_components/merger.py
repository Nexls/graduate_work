from typing import Generator, List


from psycopg2._psycopg import connection
from psycopg2.extras import DictCursor

from ...state import State
from .etltype import ETLType
from ...utils import coroutine


class Merger:
    """
    Клаcc Merger нужен для выкачивания всех фильмов, задейственных в обновлении данных.
    """
    def __init__(self, _type: ETLType, state: State, conn: connection, limit: int = 100):
        self.type: ETLType = _type
        self.state = state
        self.conn = conn
        self.limit = limit

    @property
    def SQL_merging(self) -> str:
        """
        SQL-скрипт возращающий фильмы с агрегированными полями людей и жанров.
        :return:
        """
        return '''
                SELECT
                fw.id as id, 
                fw.title, 
                fw.description, 
                fw.rating, 
                fw.type, 
                fw.created, 
                fw.modified, 
                array_agg(pfw.profession) as person_professions, 
                array_agg(p.id) as person_ids, 
                array_agg(p.full_name) person_full_name,
                array_agg(distinct g.name) as genre_name,
                array_agg(distinct g.id) as genre_id
            FROM content.film_work fw
            LEFT JOIN content.film_work_person pfw ON pfw.film_work_id = fw.id
            LEFT JOIN content.person p ON p.id = pfw.person_id
            LEFT JOIN content.film_work_genre gfw ON gfw.film_work_id = fw.id
            LEFT JOIN content.genre g ON g.id = gfw.genre_id
            WHERE fw.id IN (%s)
            GROUP BY fw.id, fw.title, fw.description, fw.rating, fw.type, fw.created, fw.modified 
        '''

    @coroutine
    def merg(self) -> Generator[List[DictCursor], None, None]:
        """
        Корутина принимает список фильмов, которые необходимо вытащить из бд и возращает список DictCursor.
        :return:
        """
        film_dict = None
        while data := (yield film_dict):
            format_strings = ','.join(['%s'] * len(data))
            updated_ids_list = [r[0] for r in data]
            with self.conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(self.SQL_merging % format_strings, updated_ids_list)
                film_dict = ('movies', cur.fetchall())