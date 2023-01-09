from abc import ABCMeta, abstractmethod


class EntityStorageMeta(metaclass=ABCMeta):
    @abstractmethod
    def query(self, entity):
        pass

    @abstractmethod
    def add(self, entity):
        pass

    @abstractmethod
    def remove(self, entity):
        pass


class ResourceStorageMeta(metaclass=ABCMeta):
    @abstractmethod
    def query(self, entity):
        pass

    @abstractmethod
    def add(self, entity):
        pass

    @abstractmethod
    def remove(self, entity):
        pass


class SystemStorageMeta(metaclass=ABCMeta):
    @abstractmethod
    def query(self, entity):
        pass

    @abstractmethod
    def add(self, entity):
        pass

    @abstractmethod
    def remove(self, entity):
        pass
