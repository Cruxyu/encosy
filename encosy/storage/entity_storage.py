from .meta import EntityStorageMeta
from .typings import Entity, SystemConfig

from typing import Any


class SimpleEntityStorage(EntityStorageMeta):
    def __init__(self):
        self.entities = set()

    def add(self, entity: Entity):
        self.entities.add(entity)

    def remove(self, entity: Entity):
        self.entities.remove(entity)

    def query(self, *args, **kwargs):
        pass

    def get(self, *types):
        entities = []
        components = set(types)
        for entity in self.entities:
            if components <= entity.keys():
                entities.append(entity)
        return entities

    def query_expression(self, expression: ()):
        entities = []
        for entity in self.entities:
            try:
                expression(entity)
            except KeyError:
                continue
            else:
                entities.append(entity)
        return entities
