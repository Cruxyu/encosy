from .meta import ResourceStorageMeta


class SimpleResourceStorage(ResourceStorageMeta):
    def __init__(self):
        self.resources = {}

    def add(self, resource):
        self.resources[type(resource)] = resource
        return self

    def remove(self, resource: type):
        self.resources.pop(resource)
        return self

    def query(self, *args, **kwargs):
        pass

    def get(self, resource: type):
        return self.resources[resource]

    def __len__(self):
        return len(self.resources)
