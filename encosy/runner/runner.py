from .meta import RunnerMeta
from typing import Iterable, Callable
from multiprocessing import Process


class SimpleRunner(RunnerMeta):
    def run(self, functions: Iterable[Callable]):
        for function in functions:
            function()


class ParallelRunner(RunnerMeta):
    def run(self, functions: Iterable[Callable]):
        processors = []
        for function in functions:
            process = Process(target=function)
            process.start()
            processors.append(process)
        for process in processors:
            process.join()
