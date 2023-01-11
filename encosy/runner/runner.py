from multiprocessing import Process
from typing import Callable, Iterable

from .meta import RunnerMeta


class SimpleRunner(RunnerMeta):
    def run(self, functions: Iterable[Callable]):
        """
        Executes functions in consecutive order

        Args:
            functions: basically generator

        Returns:

        """
        for function in functions:
            function()


class ParallelRunner(RunnerMeta):
    def run(self, functions: Iterable[Callable]):
        """
        Executes each tick in parallel

        Args:
            functions: basically generator

        Returns:

        """
        processors = []
        for function in functions:
            process = Process(target=function)
            process.start()
            processors.append(process)
        for process in processors:
            process.join()
