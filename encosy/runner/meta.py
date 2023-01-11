from abc import ABCMeta, abstractmethod
from typing import Iterable, Callable


class RunnerMeta(metaclass=ABCMeta):
    @abstractmethod
    def run(self, functions: Iterable[Callable]):
        pass
