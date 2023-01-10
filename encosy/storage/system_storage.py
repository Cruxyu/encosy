from .meta import SystemStorageMeta
from .typings import Commands, Entities, SystemConfig


def process_system_arguments(system: ()) -> SystemConfig:
    system_conf = SystemConfig(
        callable=system, commands={}, resources={}, components={}, types=set()
    )
    for name, annotation in system.__annotations__.items():
        if annotation is Commands:
            system_conf.commands[annotation] = name
        elif getattr(annotation, "__origin__", None) is Entities:
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
            for system_config in self.systems.values()
            if types <= system_config.types
        ]

    def get(self, system):
        return self.systems[system]

    def get_all(self):
        return self.systems.values()

    def __len__(self):
        return len(self.systems)
