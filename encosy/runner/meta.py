from abc import ABCMeta, abstractmethod
from typing import Callable, Iterable


class RunnerMeta(metaclass=ABCMeta):
    @abstractmethod
    def run(self, functions: Iterable[Callable]):
        """
        Runner class is used for executing functions either consecutive or
        in parallel

        Args:
            functions: generator - list of functions

        Returns:

        """
        pass
