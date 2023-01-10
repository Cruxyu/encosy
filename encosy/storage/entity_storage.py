from typing import Any, Callable

from .meta import EntityStorageMeta
from .typings import Entities, Entity


class SimpleEntityStorage(EntityStorageMeta):
    def __init__(self):
        self.idx = 0
        self.entities: dict[int, Entity] = {}

    def add(self, entity: Entity):
        self.idx += 1
        self.entities[self.idx] = entity
        return self

    def remove(self, entity: Entity):
        key_to_del = 0
        for key, entity_to_del in self.entities.items():
            if entity_to_del == entity:
                key_to_del = key
                break
        if key_to_del:
            self.entities.pop(key_to_del)
        return self

    def query(self, *args, **kwargs):
        pass

    def get(self, *types):
        entities: Entities[Any] = Entities()
        components = set(types)
        for entity in self.entities.values():
            if components <= entity.keys():
                entities.append(entity)
        return entities

    def query_expression(self, expression: Callable[[Entity], Any]):
        entities: Entities[Any] = Entities()
        for entity in self.entities.values():
            try:
                if expression(entity):
                    entities.append(entity)
            except KeyError:
                continue
        return entities

    def __len__(self):
        return len(self.entities)
