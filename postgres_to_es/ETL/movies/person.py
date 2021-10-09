from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class Person:
    id: UUID
    full_name: str
    gender: str
    roles: list = field(default_factory=list)
    film_ids: list = field(default_factory=list)
    filmworks: list = field(default_factory=list, init=False)
    birth_date: datetime = field(default_factory=datetime.now)
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        filmworks_set = set()
        for role, film_id in zip(self.roles, self.film_ids):
            if (role, film_id) not in filmworks_set:
                filmworks_set.add((role, film_id))
                self.filmworks.append({'uuid': str(film_id), 'role': role})

    def to_json(self):
        return {
            'uuid': str(self.id),
            '@timestamp': self.modified.isoformat(),
            'full_name': self.full_name,
            'gender': self.gender,
            'filmworks': self.filmworks,
            'birth_date': self.birth_date.isoformat(),
            'created': self.created.isoformat(),
            'modified': self.modified.isoformat()
        }
