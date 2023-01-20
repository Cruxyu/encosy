from typing import Any, Callable

from .meta import EntityStorageMeta
from .typings import Entities, Entity


class SimpleEntityStorage(EntityStorageMeta):
    def __init__(self):
        self.idx = 0
        self.entities: dict[int, Entity] = {}

    def add(self, entity: Entity) -> int:
        """
        Add entity to storage
        Args:
            entity: Any Entity with Any component

        Returns:
            id of an entity

        """
        self.idx += 1
        self.entities[self.idx] = entity
        return self.idx

    def remove_by_id(self, idx: int) -> Entity:
        """
        Simply remove by id
        Args:
            idx: id of an entity

        Returns:
            entity itself
        """
        return self.entities.pop(idx)

    def remove(self, entity: Entity) -> 'SimpleEntityStorage':
        """
        Remove entity from storage works iteratively

        Args:
            entity: works by comparison of existing entity and new

        Returns:
            self

        """
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

    def get(self, *types: type) -> Entities[Any]:
        """
        Query entities by component types

        Args:
            *types: types of components

        Returns:
            entities with given components

        """
        entities: Entities[Any] = Entities()
        components = set(types)
        for entity in self.entities.values():
            if components <= entity.keys():
                entities.append(entity)
        return entities

    def query_expression(self, expression: Callable[[Entity], Any]) -> Entities[Any]:
        """
        Query entities by expression

        Args:
            expression: expression of type (Entity) -> True or False

        Returns:
            entities
        """
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
