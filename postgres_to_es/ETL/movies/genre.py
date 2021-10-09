from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class Genre:
    id: UUID
    name: str
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)

    def to_json(self):
        return {
            'uuid': str(self.id),
            '@timestamp': self.modified.isoformat(),
            'name': self.name,
            'created': self.created.isoformat(),
            'modified': self.modified.isoformat()
        }
