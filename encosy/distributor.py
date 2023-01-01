from dataclasses import dataclass
from inspect import signature
from typing import Any, Callable, get_args, get_origin

Entities = lambda x: list[tuple[x]]  # type: ignore  # noqa


class Entity:
    def __init__(self, *components: Any):
        """

        :param components:
        """
        types = [type(component) for component in components]
        if len(types) != len(set(types)):
            raise ValueError(
                "Duplicated components are not allowed and leads to overriding"
            )
        self.__components: dict[type, Any] = {
            type(com): com for com in components
        }

    def __getitem__(self, key):
        return self.__components[key]

    def __contains__(self, key):
        return key in self.__components

    def __len__(self):
        return len(self.__components)

    def __repr__(self):
        return "Entity with components {}".format(
            tuple(self.__components.values())
        )


@dataclass
class SystemConf:
    system: Callable
    command: bool
    resources: dict[type, str]
    components: dict[tuple, str]


class Distributor:
    def __init__(self):
        """ """
        self.__systems_conf: dict[Callable, SystemConf] = {}
        self.__systems_to_drop: dict[Callable, None] = {}
        self.__systems_stop: dict[Callable, None] = {}
        self.__stop = False

        self.__idx = 1
        self.__entities: dict[int, Entity] = {}
        self.__resources: dict[type, Any] = {}
        self.__commands = Commands(self)

    def get_systems(self):
        """

        :return:
        """
        return self.__systems_conf

    def get_entities(self):
        """

        :return:
        """
        return self.__entities

    def get_resources(self):
        """

        :return:
        """
        return self.__resources

    def __query_entities(self, *component_types: type):
        """

        :param component_types:
        :return:
        """
        entities = []
        for entity in self.__entities.values():
            for component in component_types:
                if component not in entity:
                    break
            else:
                entities.append(entity)
        return entities

    def register_systems(self, *systems: Callable[[Any], Any]):
        """

        :param systems:
        :return:
        """
        for system in systems:
            system_conf = SystemConf(
                system=system,
                command=False,
                resources={},
                components={},
            )
            arguments = signature(system).parameters
            for name, list_tuple_argument in arguments.items():
                if (
                    name == "commands"
                    or list_tuple_argument.annotation == Commands
                ):
                    system_conf.command = True
                elif get_origin(list_tuple_argument.annotation) != list:
                    system_conf.resources[
                        list_tuple_argument.annotation
                    ] = name
                else:
                    argument = get_args(
                        get_args(list_tuple_argument.annotation)[0]
                    )
                    system_conf.components[argument] = name
            self.__systems_conf[system] = system_conf
        return self

    def register_resources(self, *resources: Any):
        """

        :param resources:
        :return:
        """
        for resource in resources:
            self.__resources[type(resource)] = resource
        return self

    def register_entity(self, *entities: Entity):
        """

        :param entities:
        :return:
        """
        for entity in entities:
            self.__entities[self.__idx] = entity
            self.__idx += 1
        return self

    def register_plugins(self, *plugins: Callable[[Any], None]):
        """

        :param plugins:
        :return:
        """
        for plugin in plugins:
            plugin(self)
        return self

    def __drop_systems(self, *systems: Callable[[Any], Any]):
        """

        :param systems:
        :return:
        """
        for system in systems:
            if system in self.__systems_conf:
                del self.__systems_conf[system]
        return self

    def drop_entities(self, *component_types: type):
        """

        :param component_types:
        :return:
        """
        keys_to_del = []
        for key, entity in self.__entities.items():
            for component in component_types:
                if component not in entity:
                    break
            else:
                keys_to_del.append(key)
        for key in keys_to_del:
            del self.__entities[key]
        return self

    def drop_entities_with_expression(
        self, expression: Callable[[Entity], bool]
    ):
        """

        :param expression:
        :return:
        """
        keys_to_del = []
        for key, entity in self.__entities.items():
            try:
                if expression(entity):
                    keys_to_del.append(key)
            except KeyError:
                pass
        for key in keys_to_del:
            del self.__entities[key]
        return self

    def stop_systems(self, *systems):
        """

        :param systems:
        :return:
        """
        for system in systems:
            self.__systems_stop[system] = None
        return self

    def start_systems(self, *systems: Callable[[Any], Any]):
        """

        :param systems:
        :return:
        """
        for system in systems:
            if system in self.__systems_stop:
                del self.__systems_stop[system]
        return self

    def schedule_drop_systems(self, *systems: Callable[[Any], Any]):
        """

        :param systems:
        :return:
        """
        for system in systems:
            self.__systems_to_drop[system] = None
        return self

    def __run_scheduled_drop_systems(self):
        """

        :return:
        """
        self.__drop_systems(*self.__systems_to_drop.keys())
        self.__systems_to_drop = {}
        return self

    def pause(self):
        """

        :return:
        """
        self.__stop = True
        return self

    def resume(self):
        """

        :return:
        """
        self.__stop = False
        return self

    def __extract_system_input(
        self, system_conf: SystemConf
    ) -> dict[str, Any]:
        """

        :param system_conf:
        :return:
        """
        key_word_arguments = {}
        if system_conf.command:
            key_word_arguments["commands"] = self.__commands
        for resource, name in system_conf.resources.items():
            key_word_arguments[name] = self.__resources[resource]
        for component_types, name in system_conf.components.items():
            entities = self.__query_entities(*component_types)
            key_word_arguments[name] = [
                [entity[component_type] for component_type in component_types]
                for entity in entities
            ]
        return key_word_arguments

    def tick(self):
        """

        :return:
        """
        if self.__stop:
            return False
        for system_conf in self.__systems_conf.values():
            if system_conf.system in self.__systems_stop:
                continue
            system_conf.system(**self.__extract_system_input(system_conf))
        self.__run_scheduled_drop_systems()
        return True

    def run(self):
        """

        :return:
        """
        while self.tick():
            pass
        return self

    def __repr__(self):
        return (
            "Dispenser\n    Systems: {}\n    Entities: {}\n    "
            "Resources: {}".format(
                self.__systems_conf, self.__entities, self.__resources
            )
        )


class Commands:
    def __init__(self, distributor: Distributor):
        """

        :param distributor:
        """
        self.__distributor = distributor

    def register_entity(self, *entities):
        """

        :param entities:
        :return:
        """
        self.__distributor.register_entity(*entities)
        return self

    def drop_entities(self, *components):
        """

        :param components:
        :return:
        """
        self.__distributor.drop_entities(*components)
        return self

    def drop_entities_with_expression(self, expression: Callable):
        """

        :param expression:
        :return:
        """
        self.__distributor.drop_entities_with_expression(expression)
        return self

    def stop_systems(self, *systems):
        """

        :param systems:
        :return:
        """
        self.__distributor.stop_systems(*systems)
        return self

    def start_systems(self, *systems):
        """

        :param systems:
        :return:
        """
        self.__distributor.start_systems(*systems)
        return self

    def schedule_drop_systems(self, *systems):
        """

        :param systems:
        :return:
        """
        self.__distributor.schedule_drop_systems(*systems)
        return self

    def pause_distributor(self):
        """

        :return:
        """
        self.__distributor.pause()
        return self

    def resume_distributor(self):
        """

        :return:
        """
        self.__distributor.resume()
        return self
