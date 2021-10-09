from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from uuid import UUID, uuid4


@dataclass
class Movie:
    """
    Объект фильм
    """
    id: UUID = field(default_factory=uuid4)
    title: str = field(default='')
    description: str = field(default='')
    type: str = field(default='')
    rating: float = field(default=None)
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)
    person_professions: List = field(default_factory=list)
    person_ids: List = field(default_factory=list)
    person_full_name: List = field(default_factory=list)
    genre_name: List = field(default_factory=list)
    genre_id: List = field(default_factory=list)
    genres: List = field(default_factory=list, init=False)
    actors: List = field(default_factory=list, init=False)
    actors_names: List = field(default_factory=list, init=False)
    writers: List = field(default_factory=list, init=False)
    writers_names: List = field(default_factory=list, init=False)
    directors: List = field(default_factory=list, init=False)
    directors_names: List = field(default_factory=list, init=False)

    def __post_init__(self):
        set_film_work_person = set()
        for profession, _id, full_name in zip(self.person_professions, self.person_ids, self.person_full_name):
            if (profession, _id, full_name) not in set_film_work_person:
                set_film_work_person.add((profession, _id, full_name))
                obj = {'uuid': str(_id), 'full_name': full_name}
                if profession == 'actor':
                    self.actors.append(obj)
                    self.actors_names.append(full_name)
                elif profession == 'writer':
                    self.writers.append(obj)
                    self.writers_names.append(full_name)
                elif profession == 'director':
                    self.directors.append(obj)
                    self.directors_names.append(full_name)
        for genre_id, genre_name in zip(self.genre_id, self.genre_name):
            self.genres.append({'uuid': str(genre_id), 'name': genre_name})

    def to_json(self):
        return {
            'uuid': str(self.id),
            '@timestamp': self.modified.isoformat(),
            'title': self.title,
            'description': self.description,
            'type': self.type,
            'genre': self.genres,
            'imdb_rating': self.rating,
            'actors': self.actors,
            'actors_names': self.actors_names,
            'writers': self.writers,
            'writers_names': self.actors_names,
            'directors': self.directors,
            'directors_names': self.directors_names,
            'created': self.created.isoformat(),
            'modified': self.modified.isoformat()
        }
