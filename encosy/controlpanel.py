from dataclasses import dataclass
from inspect import signature
from typing import Any, Callable, TypeVar, get_args, get_origin, Generic

T = TypeVar("T")


class Entity(dict[type, T]):
    def __init__(self, *components: Any):
        """
        Basic class for storing components by their type

        If duplicated types passed no error will be raised
        instead duplicate value replace existing one

        :param components: accumulative of any type component
        """
        super().__init__({type(com): com for com in components})


class Entities(list[Entity[T]]):
    """
    Simple class for typing in systems

    def my_system(
        entities: Entities[Entity[Name]]
    ):
        pass
    """

    pass


@dataclass
class SystemConf:
    system: Callable
    command: bool
    resources: dict[type, str]
    components: dict[tuple, str]


class ControlPanel:
    def __init__(self):
        """
        ECS control panel
        """
        self._systems_conf: dict[Callable, SystemConf] = {}
        self._systems_to_drop: dict[Callable, None] = {}
        self._systems_stop: dict[Callable, None] = {}
        self._stop = False

        self._idx = 1
        self._entities: dict[int, Entity] = {}
        self._resources: dict[type, Any] = {}
        self._commands = Commands(self)

    def get_systems(self) -> dict[Callable, SystemConf]:
        """
        Returns systems configuration stored in ControlPanel
        :return: dict as key=Callable or registered functions
        """
        return self._systems_conf

    def get_entities(self) -> dict[int, Entity]:
        """
        Return registered entities in ControlPanel
        DO NOT add new values to a dict instead use .register_entities()
        :return: dict where key=int
        """
        return self._entities

    def get_resources(self) -> dict[type, Any]:
        """
        Return registered resources in ControlPanel
        :return: dict where key=type
        """
        return self._resources

    def _query_entities(self, *component_types: type) -> Entities[Entity[Any]]:
        """
        Hidden function to query components
        Returns list of same tuples types where order is defined with
        the order of component_types
        :param component_types: types to query components
        :return: list[tuple[T1,T2, ... TN]]
        """
        entities: Entities[Entity[Any]] = Entities()
        for entity in self._entities.values():
            for component in component_types:
                if component not in entity:
                    break
            else:
                entities.append(entity)
        return entities

    @staticmethod
    def extract_args_from_system(system: Callable):
        system_conf = SystemConf(
            system=system,
            command=False,
            resources={},
            components={},
        )
        for name, arg in signature(system).parameters.items():
            annotation = arg.annotation
            if name == "commands" or annotation == Commands:
                system_conf.command = True
            elif (
                get_origin(annotation) != Entities
                and get_origin(annotation) != Entity
            ):
                system_conf.resources[annotation] = name
            else:
                if get_origin(annotation) == Entities:
                    argument = get_args(get_args(annotation)[0])
                else:
                    argument = get_args(annotation)
                system_conf.components[argument] = name
        return system_conf

    def register_systems(self, *systems: Callable[[Any], Any]):
        """
        Register any callable.
        Input params of Callable can contain:
            commands: Commands (name and type is reserved)
            resource: Any - same as entity, but only one can exist
            entity: Entity[ComponentType1, ComponentType2, ...]
        :param systems: Callable
        :return: self | ControlPanel
        """
        for system in systems:
            self._systems_conf[system] = ControlPanel.extract_args_from_system(
                system
            )
        return self

    def register_resources(self, *resources: Any):
        """
        Register resources. Each resource should be unique type
        as it is accessed through it
        :param resources: object of eny type
        :return: self | ControlPanel
        """
        for resource in resources:
            self._resources[type(resource)] = resource
        return self

    def register_entities(self, *entities: Entity):
        """
        Register entity. Each entity assigned a unique integer
        :param entities: Entity with components
        :return: self | ControlPanel
        """
        for entity in entities:
            self._entities[self._idx] = entity
            self._idx += 1
        return self

    def register_plugins(self, *plugins: Callable[[Any], None]):
        """
        Register plugins. Plugin is a simple function that takes ControlPanel
        :param plugins: Callable[[ControlPanel]], None]
        :return: self | ControlPanel
        """
        for plugin in plugins:
            plugin(self)
        return self

    def _drop_systems(self, *systems: Callable[[Any], Any]):
        """
        Drop given systems
        :param systems: Callable
        :return: self | ControlPanel
        """
        for system in systems:
            if system in self._systems_conf:
                del self._systems_conf[system]
        return self

    def drop_entities(self, *component_types: type):
        """
        Drop entities based on its components types
        :param component_types: type that entity should contain
        in order to be dropped
        :return: self | ControlPanel
        """
        keys_to_del = []
        for key, entity in self._entities.items():
            for component in component_types:
                if component not in entity:
                    break
            else:
                keys_to_del.append(key)
        for key in keys_to_del:
            del self._entities[key]
        return self

    def drop_entities_with_expression(
        self, expression: Callable[[Entity], bool]
    ):
        """
        Drops entities based on expression of type (entity: Entity) -> bool
        Ex:
            lambda entity: Entity[Name] == "MyName"
        :param expression: Callable[[Entity], bool]
        :return: self | ControlPanel
        """
        keys_to_del = []
        for key, entity in self._entities.items():
            try:
                if expression(entity):
                    keys_to_del.append(key)
            except KeyError:
                pass
        for key in keys_to_del:
            del self._entities[key]
        return self

    def stop_systems(self, *systems):
        """
        Add systems to stop dictionary
        :param systems: Callable
        :return: self | ControlPanel
        """
        for system in systems:
            self._systems_stop[system] = None
        return self

    def start_systems(self, *systems: Callable[[Any], Any]):
        """
        Remove systems from stop dictionary
        :param systems: Callable
        :return: self | ControlPanel
        """
        for system in systems:
            if system in self._systems_stop:
                del self._systems_stop[system]
        return self

    def schedule_drop_systems(self, *systems: Callable[[Any], Any]):
        """
        Schedules drop of a given systems
        Add system to drop queue and call _run_scheduled_drop_systems
        at the end of a tick
        :param systems: Callable
        :return: self | ControlPanel
        """
        for system in systems:
            self._systems_to_drop[system] = None
        return self

    def _run_scheduled_drop_systems(self):
        """
        Runs drop on a system drop queue and clear it
        :return: self | ControlPanel
        """
        self._drop_systems(*self._systems_to_drop.keys())
        self._systems_to_drop = {}
        return self

    def pause(self):
        """
        Set a pause for a tick function (stop = True).
        stop works as a gate in tick function
        :return: self | ControlPanel
        """
        self._stop = True
        return self

    def resume(self):
        """
        Set a resume for a tick function (stop = False).
        stop works as a gate in tick function
        :return: self | ControlPanel
        """
        self._stop = False
        return self

    def _extract_system_input(self, system_conf: SystemConf) -> dict[str, Any]:
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

    def tick(self) -> bool:
        """
        Equivalent to one step where each system
        in a given order (register_system(1->2->3->...) executes
        with a requested params [Any, Commands, Entities(list[tuple[Any]]])
        If requested resource does not exist then KeyError raised
        :return: bool returns False if Dispenser.pause()
        called to resume call .resume()
        """
        if self._stop:
            return False
        for system_conf in self._systems_conf.values():
            if system_conf.system in self._systems_stop:
                continue
            system_conf.system(**self._extract_system_input(system_conf))
        self._run_scheduled_drop_systems()
        return True

    def run(self):
        """
        Simple loop for executing ticks until commands.pause()
        called within any system
        then after current tick new won't start
        :return: self | ControlPanel
        """
        self.resume()
        while self.tick():
            pass
        return self

    def __repr__(self):
        return (
            "ControlPanel\n    Systems: {}\n    Entities: {}\n    "
            "Resources: {}".format(
                self._systems_conf, self._entities, self._resources
            )
        )


class Commands:
    def __init__(self, control_panel: ControlPanel):
        """
        Commands layer to use control panel inside a system
        :param control_panel:
        """
        self._control_panel = control_panel

    def register_entities(self, *entities):
        """
        Register entities for control panel
        :param entities:
        :return: self | Commands
        """
        self._control_panel.register_entities(*entities)
        return self

    def drop_entities(self, *components):
        """
        Drop entities by components
        :param components:
        :return: self | Commands
        """
        self._control_panel.drop_entities(*components)
        return self

    def drop_entities_with_expression(
        self, expression: Callable[[Entity], bool]
    ):
        """
        Drop entities using expression of type (entity: Entity) -> bool
        ex:
            lambda entity: entity[Position].x == 17.0
                            and entity[Position].y == 21.0
            where Position is a component of a given entity
        :param expression: Callable[[Entity], bool]
        :return: self | Commands
        """
        self._control_panel.drop_entities_with_expression(expression)
        return self

    def stop_systems(self, *systems):
        """
        Prevents systems from executing
        :param systems:
        :return: self | Commands
        """
        self._control_panel.stop_systems(*systems)
        return self

    def start_systems(self, *systems):
        """
        Allows systems to be executed
        :param systems:
        :return: self | Commands
        """
        self._control_panel.start_systems(*systems)
        return self

    def schedule_drop_systems(self, *systems):
        """
        Completely remove system, but only after current tick
        :param systems:
        :return: self | Commands
        """
        self._control_panel.schedule_drop_systems(*systems)
        return self

    def pause_control_panel(self):
        """
        Exits from run at the next tick and prevents tick to be executed
        until resume_control_panel is called
        :return: self | Commands
        """
        self._control_panel.pause()
        return self

    def resume_control_panel(self):
        """
        Resume run but only after control_panel.run() is called
        :return: self | Commands
        """
        self._control_panel.resume()
        return self
