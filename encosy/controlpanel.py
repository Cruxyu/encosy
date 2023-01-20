from typing import Any, Callable, Generator

from .runner import DefaultRunner, RunnerMeta
from .storage import (
    DefaultEntityStorage,
    DefaultResourceStorage,
    DefaultSystemStorage,
    EntityStorageMeta,
    ResourceStorageMeta,
    SystemStorageMeta,
)
from .storage.typings import Commands, Entity, SystemConfig


class ControlPanel:
    def __init__(
        self,
        system_storage: SystemStorageMeta | None = None,
        entity_storage: EntityStorageMeta | None = None,
        resource_storage: ResourceStorageMeta | None = None,
        runner: RunnerMeta | None = None,
    ):
        """
        ECS control panel

        Each storage unit represents and fulfill the purpose for distributing
        storing and querying items that associate with it

        Args:
            system_storage: Object that implements SystemStorageMeta
            entity_storage: Object that implements ResourceStorageMeta
            resource_storage: Object that implements ResourceStorageMeta
            runner: Object that implements RunnerMeta
        """

        if system_storage is None:
            system_storage = DefaultSystemStorage()
        if entity_storage is None:
            entity_storage = DefaultEntityStorage()
        if resource_storage is None:
            resource_storage = DefaultResourceStorage()
        if runner is None:
            runner = DefaultRunner()

        self.system_storage = system_storage
        self.entity_storage = entity_storage
        self.resource_storage = resource_storage
        self.runner = runner

        self._systems_to_drop: dict[Callable[[Any], Any], None] = {}
        self._systems_stop: dict[Callable[[Any], Any], None] = {}
        self._stop = False

        self._commands = Commands(self)

    def register_systems(
        self, *systems: Callable[[Any], Any]
    ) -> "ControlPanel":
        """
        Register any Callable.
        Input params of function can contain:
            - commands: Commands (name and type is reserved)
            - resource: Any - same as entity, but only one can exist
            - entity: Entity[ComponentType1, ComponentType2, ...]

        Args:
            *systems: Callable that contain definition or typing for input
                [Commands, Entities[ ListOfComponents ], Any],
                Any is considered as resource

        Returns:
            self
        """
        for system in systems:
            self.system_storage.add(system)
        return self

    def register_resources(self, *resources: Any) -> "ControlPanel":
        """
        Register resources. Each resource should be unique type
        as it is accessed through it

        Args:
            *resources: Object of any type

        Returns:
            self
        """
        for resource in resources:
            self.resource_storage.add(resource)
        return self

    def register_entities(self, *entities: Any) -> list[Any]:
        """
        Register entity. Each entity assigned a unique integer

        Args:
            *entities: Entity of any type that suits entity_storage.add
                by default the type is 'Entity'

        Returns:
            list of idx but not strict to it

        """
        return [self.entity_storage.add(entity) for entity in entities]

    def register_plugins(
        self, *plugins: Callable[["ControlPanel"], Any]
    ) -> "ControlPanel":
        """
        Register plugins. Plugin is a simple function that takes ControlPanel

        Args:
            *plugins: simple function to that takes ControlPanel and apply
                onto self immediately

        Returns:
            self

        """
        for plugin in plugins:
            plugin(self)
        return self

    def _remove_system(self, *systems: Callable[[Any], Any]) -> "ControlPanel":
        """
        Drop given systems

        Args:
            *systems: same callable as in system register

        Returns:
            self

        """
        for system in systems:
            self.system_storage.remove(system)
        return self

    def remove_entities(self, *component_types: type) -> "ControlPanel":
        """
        Drop entities based on its components types

        Args:
            *component_types: remove entities by type of components

        Returns:
            self

        """
        entities = self.entity_storage.get(*component_types)
        for entity in entities:
            self.entity_storage.remove(entity)
        return self

    def drop_entities_with_expression(
        self, expression: Callable[[Entity], bool]
    ) -> "ControlPanel":
        """
        Drops entities based on expression of type (entity: Entity) -> bool
        Ex:
            - lambda entity: Entity[Name] == "MyName"

        Args:
            expression: callable that takes entity as input and return if it is
                True or False

        Returns:
            self

        """
        entities = self.entity_storage.query_expression(expression)
        for entity in entities:
            self.entity_storage.remove(entity)
        return self

    def stop_systems(self, *systems: Callable[[Any], Any]) -> "ControlPanel":
        """
        Add systems to stop dictionary

        Args:
            *systems: used as hash to stop system

        Returns:
            self

        """
        for system in systems:
            self._systems_stop[system] = None
        return self

    def start_systems(self, *systems: Callable[[Any], Any]) -> "ControlPanel":
        """
        Remove systems from stop dictionary

        Args:
            *systems: used as hash to resume systems

        Returns:
            self

        """
        for system in systems:
            if system in self._systems_stop:
                self._systems_stop.pop(system)
        return self

    def schedule_drop_systems(
        self, *systems: Callable[[Any], Any]
    ) -> "ControlPanel":
        """
        Schedules drop of a given systems
        Add system to drop queue and call _run_scheduled_drop_systems
        at the end of a tick

        Args:
            *systems: used as hash to drop system from storage

        Returns:
            self

        """
        for system in systems:
            self._systems_to_drop[system] = None
        return self

    def _run_scheduled_drop_systems(self) -> "ControlPanel":
        """
        Runs drop on a system drop queue and clear it

        Returns:
            self

        """
        self._remove_system(*self._systems_to_drop.keys())
        self._systems_to_drop = {}
        return self

    def pause(self) -> "ControlPanel":
        """
        Set a pause for a tick function (stop = True). Stop works as a gate
        in tick function

        Returns:
            self

        """
        self._stop = True
        return self

    def resume(self) -> "ControlPanel":
        """
        Set a resume for a tick function (stop = False).
        stop works as a gate in tick function

        Returns:
            self

        """
        self._stop = False
        return self

    def _extract_system_input(
        self, system_config: SystemConfig
    ) -> dict[str, Any]:
        """
        Extracts input values for given system and returns basic kwargs
        If any of the resources does not exist or isn't registered - KeyError

        Args:
            system_config: to connects storages with systems using defined class

        Returns:
            key word arguments or kwargs
        """
        key_word_arguments: dict[str, Any] = {}
        system_config = self.system_storage.get(system_config.callable)
        for command, name in system_config.commands.items():
            key_word_arguments[name] = self._commands
        for resource, name in system_config.resources.items():
            key_word_arguments[name] = self.resource_storage.get(resource)
        for component_types, name in system_config.components.items():
            key_word_arguments[name] = self.entity_storage.get(
                *component_types
            )
        return key_word_arguments

    def _function_generator(self) -> Generator:
        """
        Generator for runner

        Returns:
            generator of functions

        """
        for system_config in self.system_storage.get_all():
            if system_config.callable in self._systems_stop:
                continue
            yield lambda: system_config.callable(
                **self._extract_system_input(system_config)
            )

    def tick(self) -> bool:
        """
        By default, equivalent to one step where each system
        in a given order (register_system(1->2->3->...) executes
        with a requested params [Any, Commands, Entities(list[tuple[Any]]])
        If requested resource does not exist then KeyError raised

        Returns:
            False if stopped and True if not

        """
        if self._stop:
            return False
        self.runner.run(self._function_generator())
        self._run_scheduled_drop_systems()
        return True

    def run(self) -> "ControlPanel":
        """
        Simple loop for executing ticks until commands.pause()
        called within any system then after current tick new won't start

        Returns:
            self

        """
        self.resume()
        while self.tick():
            pass
        return self

    def __repr__(self):
        return "Control Panel"
