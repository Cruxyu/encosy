from abc import ABCMeta


class EntityStorageMeta(metaclass=ABCMeta):
    def query(self, entity):
        pass

    def add(self, entity):
        pass

    def remove(self, entity):
        pass


class ResourceStorageMeta(metaclass=ABCMeta):
    def query(self, entity):
        pass

    def add(self, entity):
        pass

    def remove(self, entity):
        pass


class SystemStorageMeta(metaclass=ABCMeta):
    def query(self, entity):
        pass

    def add(self, entity):
        pass

    def remove(self, entity):
        pass
