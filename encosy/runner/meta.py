from abc import ABCMeta, abstractmethod
from typing import Callable, Iterable


class RunnerMeta(metaclass=ABCMeta):
    @abstractmethod
    def run(self, functions: Iterable[Callable]):
        pass
