from .meta import ResourceStorageMeta
from typing import Any


class SimpleResourceStorage(ResourceStorageMeta):
    def __init__(self):
        self.resources = {}

    def add(self, resource: Any) -> 'SimpleResourceStorage':
        """
        Add resource by type

        Args:
            resource: any

        Returns:
            self

        """
        self.resources[type(resource)] = resource
        return self

    def remove(self, resource: type) -> 'SimpleResourceStorage':
        """
        Remove resource by type

        Args:
            resource: any type

        Returns:
            self

        """
        self.resources.pop(resource)
        return self

    def query(self, *args, **kwargs):
        pass

    def get(self, resource: type) -> Any:
        """
        Get resource by type

        Args:
            resource: type of resource

        Returns:
            Resource of given type

        """
        return self.resources[resource]

    def __len__(self):
        return len(self.resources)
