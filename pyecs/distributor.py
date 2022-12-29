from collections import defaultdict
from inspect import signature
from typing import Callable, get_args, get_origin, Any

import setuptools.package_index

from .entity import Entity
from dataclasses import dataclass


Entities = lambda x: list[tuple[x]]


@dataclass
class SystemConf:
    system: Callable
    command: bool
    resources: dict[type, str]
    components: dict[tuple, str]


class Distributor:
    def __init__(self):
        self.__systems_conf: dict[Callable, SystemConf] = {}
        self.__systems_to_drop: dict[Callable, None] = {}
        self.__systems_stop: dict[Callable, None] = {}

        self.__idx = 1
        self.__entities: dict[int, Entity] = {}
        self.__resources: dict[type, Any] = {}
        self.__commands = Commands(self)

    def __query_entities(self, *component_types):
        entities = []
        for entity in self.__entities.values():
            for component in component_types:
                if component not in entity:
                    break
            else:
                entities.append(entity)
        return entities

        # self.__components_entity: defaultdict[type, list[Entity]] = defaultdict(lambda: [])
        # return set.intersection(*map(
        #     set, [self.__components_entity[component_type] for component_type in component_types]
        # ))

    def register_systems(self, *systems):
        for system in systems:
            system_conf = SystemConf(
                system=system,
                command=False,
                resources={},
                components={},
            )
            arguments = signature(system).parameters
            for name, list_tuple_argument in arguments.items():
                if name == 'commands' or list_tuple_argument.annotation == Commands:
                    system_conf.command = True
                elif get_origin(list_tuple_argument.annotation) != list:
                    system_conf.resources[list_tuple_argument.annotation] = name
                else:
                    argument = get_args(get_args(list_tuple_argument.annotation)[0])
                    system_conf.components[argument] = name
            self.__systems_conf[system] = system_conf
        return self

    def register_resources(self, *resources):
        for resource in resources:
            self.__resources[type(resource)] = resource

    def register_entity(self, *entities):
        for entity in entities:
            self.__entities[self.__idx] = entity
            self.__idx += 1
            # for component in entity.components.keys():
            #     self.__components_entity[component].append(entity)
        return self

    def register_plugins(self, *plugins):
        for plugin in plugins:
            plugin(self)

    def __drop_systems(self, *systems):
        for system in systems:
            if system in self.__systems_conf:
                del self.__systems_conf[system]

    def drop_entities(self, *component_types):
        keys_to_del = []
        for key, entity in self.__entities.items():
            for component in component_types:
                if component not in entity:
                    break
            else:
                keys_to_del.append(key)
        for key in keys_to_del:
            del self.__entities[key]

    def drop_entities_with_expression(self, expression: Callable):
        keys_to_del = []
        for key, entity in self.__entities.items():
            try:
                if expression(entity):
                    keys_to_del.append(key)
            except KeyError:
                pass
        for key in keys_to_del:
            del self.__entities[key]

    def stop_systems(self, *systems):
        for system in systems:
            self.__systems_stop[system] = None

    def start_systems(self, *systems):
        for system in systems:
            if system in self.__systems_stop:
                del self.__systems_stop[system]

    def schedule_drop_systems(self, *systems):
        for system in systems:
            self.__systems_to_drop[system] = None

    def __run_scheduled_drop_systems(self):
        self.__drop_systems(*self.__systems_to_drop.keys())
        self.__systems_to_drop = {}

    def dispense(self):
        for system_conf in self.__systems_conf.values():
            if system_conf.system in self.__systems_stop:
                continue
            key_word_arguments = {}
            if system_conf.command:
                key_word_arguments["commands"] = self.__commands
            for resource, name in system_conf.resources.items():
                key_word_arguments[name] = resource
            for component_types, name in system_conf.components.items():
                entities = self.__query_entities(*component_types)
                key_word_arguments[name] = [[entity[component_type] for component_type in component_types]
                                            for entity in entities]
            system_conf.system(**key_word_arguments)
        self.__run_scheduled_drop_systems()

    def __repr__(self):
        return "Dispenser\n    Systems: {}\n    Entities: {}\n    " \
               "Resources: {}".format(self.__systems_conf, self.__entities, self.__resources)


class Commands:
    def __init__(self, distributor: Distributor):
        self.__distributor = distributor

    def register_entity(self, *entities):
        self.__distributor.register_entity(*entities)

    def drop_entities(self, *components):
        self.__distributor.drop_entities(*components)

    def drop_entities_with_expression(self, expression: Callable):
        self.__distributor.drop_entities_with_expression(expression)

    def stop_systems(self, *systems):
        self.__distributor.stop_systems(*systems)

    def start_systems(self, *systems):
        self.__distributor.start_systems(*systems)

    def schedule_drop_systems(self, *systems):
        self.schedule_drop_systems(*systems)
