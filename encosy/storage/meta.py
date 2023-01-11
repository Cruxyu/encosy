from abc import ABCMeta, abstractmethod


class EntityStorageMeta(metaclass=ABCMeta):
    @abstractmethod
    def query(self, *args, **kwargs):
        """
        Query entities by any of given arguments

        Args:
            *args: positional
            **kwargs: keywords

        Returns:
            entities
        """
        pass

    @abstractmethod
    def add(self, entity):
        """
        Add entity by any condition

        Args:
            entity: any

        Returns:
            self

        """
        pass

    @abstractmethod
    def remove(self, entity):
        """
        Remove entity by any condition

        Args:
            entity: any

        Returns:
            self

        """
        pass

    @abstractmethod
    def get(self, *types):
        """
        Get entity by types of components

        Args:
            *types: components

        Returns:
            entities

        """
        pass

    @abstractmethod
    def query_expression(self, expression):
        """
        Query entities by expression

        Args:
            expression: any callable

        Returns:
            self

        """
        pass


class ResourceStorageMeta(metaclass=ABCMeta):
    @abstractmethod
    def query(self, *args, **kwargs):
        """
        Query resource by any condition

        Args:
            *args: positional
            **kwargs: keyword

        Returns:
            resources

        """
        pass

    @abstractmethod
    def add(self, resource):
        """
        Add resource

        Args:
            resource: any type

        Returns:
            self

        """
        pass

    @abstractmethod
    def remove(self, resource):
        """
        Remove resource by type

        Args:
            resource: type of resource

        Returns:
            self

        """
        pass

    @abstractmethod
    def get(self, resource):
        """
        Get resource by type

        Args:
            resource: type of resource

        Returns:
            self

        """
        pass


class SystemStorageMeta(metaclass=ABCMeta):
    @abstractmethod
    def query(self, *args, **kwargs):
        """
        Return system by any query

        Args:
            *args: positional
            **kwargs: keyword

        Returns:
            systems

        """
        pass

    @abstractmethod
    def add(self, system):
        """
        Add systems

        Args:
            system: any callable

        Returns:
            self

        """
        pass

    @abstractmethod
    def remove(self, system):
        """
        Remove system

        Args:
            system: any callable

        Returns:
            self

        """
        pass

    @abstractmethod
    def get_all(self):
        """
        List of systems

        Returns:
            list of systems

        """
        pass

    @abstractmethod
    def get(self, system):
        """
        Get system config by callable
        
        Args:
            system: any callable

        Returns:
            system config

        """
        pass
