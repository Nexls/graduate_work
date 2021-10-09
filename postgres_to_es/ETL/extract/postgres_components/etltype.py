from enum import Enum


class ETLType(Enum):
    """
    Класс определяющий тип ETL процесса.
    """
    PERSON = 'person'
    GENRE = 'genre'
    FILM_WORK = 'film_work'
