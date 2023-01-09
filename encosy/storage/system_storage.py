from .meta import SystemStorageMeta

from dataclasses import dataclass
from typing import Any
from .typings import Entity, Entities, Commands


@dataclass
class SystemConfig:
    callable: ()
    commands: dict[type, str]
    resources: dict[type, str]
    components: dict[tuple, str]
    types: set[type]


def process_system_arguments(system: ()) -> SystemConfig:
    system_conf = SystemConfig(
        callable=system,
        commands={},
        resources={},
        components={},
        types=set()
    )
    for name, annotation in system.__annotations__.items():
        if annotation is Commands:
            system_conf.commands[annotation] = name
        elif annotation is Entities:
            system_conf.components[annotation.__args__] = name
        else:
            system_conf.resources[annotation] = name
        system_conf.types.add(annotation)
    return system_conf


class SimpleSystemStorage(SystemStorageMeta):
    def __init__(self):
        self.systems: dict[(), SystemConfig] = {}

    @staticmethod
    def process_types(*args) -> set:
        types = set()
        for type_ in args:
            types.add(type_)
        return types

    def add(self, system: ()):
        self.systems[system] = process_system_arguments(system)
        return self

    def remove(self, system: ()):
        self.systems.pop(system)
        return self

    def query(self, *args: type):
        types = SimpleSystemStorage.process_types(*args)
        return [
            system_config.callable
            for system_config
            in self.systems.values()
            if types <= system_config.types
        ]


class ComplexSystemStorage(SystemStorageMeta):
    def add(self, system: ()):
        pass

    def remove(self, system: ()):
        pass

    def query(self, *args, **kwargs):
        pass

def _extract_system_input(self, system_conf: SystemConfig) -> dict[str, Any]:
    """
    Extracts input values for given system and returns basic kwargs
    If any of the resources does not exist or isn't registered - KeyError
    :param system_conf: system params
    :return: dict[str, Any] - aka kwargs
    """
    key_word_arguments: dict[str, Any] = {}
    if system_conf.command:
        key_word_arguments["commands"] = self._commands
    for resource, name in system_conf.resources.items():
        key_word_arguments[name] = self._resources[resource]
    for component_types, name in system_conf.components.items():
        key_word_arguments[name] = self._query_entities(*component_types)
    return key_word_arguments
