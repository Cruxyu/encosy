from collections import defaultdict
from inspect import signature
from typing import Callable, get_args, get_origin, Any
from .entity import Entity


Entities = lambda x: list[tuple[x]]


class Distributor:
    def __init__(self):
        self.__systems: dict[Callable, dict[tuple, str]] = {}
        self.__systems_commands: dict[Callable, None] = {}
        self.__systems_resources: dict[Callable, dict[type, str]] = defaultdict(lambda: {})

        self.__systems_to_drop: dict[Callable, None] = {}

        self.__idx = 1
        self.__entities: dict[int, Entity] = {}
        self.__components_entity: defaultdict[type, list[Entity]] = defaultdict(lambda: [])

        self.__resources: dict[type, Any] = {}
        self.__commands = Commands(self)

    def register_systems(self, *systems):
        for system in systems:
            arguments = signature(system).parameters
            system_arguments: dict[tuple, str] = {}
            for name, list_tuple_argument in arguments.items():
                if name == 'commands' or list_tuple_argument.annotation == Commands:
                    self.__systems_commands[system] = None
                elif get_origin(list_tuple_argument.annotation) != list:
                    self.__systems_resources[system][list_tuple_argument.annotation] = name
                else:
                    argument = get_args(get_args(list_tuple_argument.annotation)[0])
                    system_arguments[argument] = name
            self.__systems[system] = system_arguments
        return self

    def register_resources(self, *resources):
        for resource in resources:
            self.__resources[type(resource)] = resource

    def register_entity(self, *entities):
        for entity in entities:
            self.__entities[self.__idx] = entity
            self.__idx += 1
            for component in entity.components.keys():
                self.__components_entity[component].append(entity)
        return self

    def register_plugins(self, *plugins):
        for plugin in plugins:
            plugin(self)

    def drop_systems(self, *systems):
        pass

    def schedule_drop_systems(self, *systems):
        pass

    def run_scheduled_drop_systems(self):
        pass

    def dispense(self):
        for system, arguments in self.__systems.items():
            key_word_arguments = {}
            if system in self.__systems_commands:
                key_word_arguments["commands"] = self.__commands
            if system in self.__systems_resources:
                for resource, name in self.__systems_resources[system].items():
                    key_word_arguments[name] = self.__resources[resource]
            for component_types, name in arguments.items():
                entities = set.intersection(*map(
                    set, [self.__components_entity[component_type] for component_type in component_types]
                ))
                key_word_arguments[name] = [[entity[component_type] for component_type in component_types]
                                            for entity in entities]

            system(**key_word_arguments)

    def __repr__(self):
        return "Dispenser\n    Systems: {}\n    Entities: {}\n    " \
               "Resources: {}".format(self.__systems, self.__entities, self.__resources)


class Commands:
    def __init__(self, distributor: Distributor):
        self.__distributor = distributor

    def register_entity(self, *entities):
        self.__distributor.register_entity(*entities)

    def remove_entity(self):
        pass
