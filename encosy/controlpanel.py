from typing import Any
from .storage import EntityStorageMeta, ResourceStorageMeta, SystemStorageMeta
from .storage import DefaultSystemStorage, DefaultResourceStorage, DefaultEntityStorage
from .storage.typings import SystemConfig


class ControlPanel:
    def __init__(
            self,
            system_storage: SystemStorageMeta = DefaultSystemStorage(),
            entity_storage: EntityStorageMeta = DefaultEntityStorage(),
            resource_storage: ResourceStorageMeta = DefaultResourceStorage(),
    ):
        """
        ECS control panel
        """
        self.system_storage = system_storage
        self.entity_storage = entity_storage
        self.resource_storage = resource_storage

        self._systems_to_drop: dict[(), None] = {}
        self._systems_stop: dict[(), None] = {}
        self._stop = False

        self._commands = Commands(self)

    def register_systems(self, *systems: ()):
        """
        Register any ().
        Input params of () can contain:
            commands: Commands (name and type is reserved)
            resource: Any - same as entity, but only one can exist
            entity: Entity[ComponentType1, ComponentType2, ...]
        :param systems: ()
        :return: self | ControlPanel
        """
        for system in systems:
            self.system_storage.add(system)
        return self

    def register_resources(self, *resources: Any):
        """
        Register resources. Each resource should be unique type
        as it is accessed through it
        :param resources: object of eny type
        :return: self | ControlPanel
        """
        for resource in resources:
            self.resource_storage.add(resource)
        return self

    def register_entities(self, *entities):
        """
        Register entity. Each entity assigned a unique integer
        :param entities: Entity with components
        :return: self | ControlPanel
        """
        for entity in entities:
            self.entity_storage.add(entity)
        return self

    def register_plugins(self, *plugins: ('ControlPanel',)):
        """
        Register plugins. Plugin is a simple function that takes ControlPanel
        :param plugins: ()[[ControlPanel]], None]
        :return: self | ControlPanel
        """
        for plugin in plugins:
            plugin(self)
        return self

    def _remove_system(self, *systems: ()):
        """
        Drop given systems
        :param systems: ()
        :return: self | ControlPanel
        """
        for system in systems:
            self.system_storage.remove(system)
        return self

    def remove_entities(self, *component_types: type):
        """
        Drop entities based on its components types
        :param component_types: type that entity should contain
        in order to be dropped
        :return: self | ControlPanel
        """
        entities = self.entity_storage.get(*component_types)
        for entity in entities:
            self.entity_storage.remove(entity)
        return self

    def drop_entities_with_expression(
        self, expression: ()
    ):
        """
        Drops entities based on expression of type (entity: Entity) -> bool
        Ex:
            lambda entity: Entity[Name] == "MyName"
        :param expression: ()[[Entity], bool]
        :return: self | ControlPanel
        """
        entities = self.entity_storage.query_expression(expression)
        for entity in entities:
            self.entity_storage.remove(entity)
        return self

    def stop_systems(self, *systems):
        """
        Add systems to stop dictionary
        :param systems: ()
        :return: self | ControlPanel
        """
        for system in systems:
            self._systems_stop[system] = None
        return self

    def start_systems(self, *systems: ()):
        """
        Remove systems from stop dictionary
        :param systems: ()
        :return: self | ControlPanel
        """
        for system in systems:
            if system in self._systems_stop:
                self._systems_stop.pop(system)
        return self

    def schedule_drop_systems(self, *systems: ()):
        """
        Schedules drop of a given systems
        Add system to drop queue and call _run_scheduled_drop_systems
        at the end of a tick
        :param systems: ()
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
        self._remove_system(*self._systems_to_drop.keys())
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

    def _extract_system_input(self, system_config: SystemConfig) -> dict[str, Any]:
        """
        Extracts input values for given system and returns basic kwargs
        If any of the resources does not exist or isn't registered - KeyError
        :param system_config: system params
        :return: dict[str, Any] - aka kwargs
        """
        key_word_arguments: dict[str, Any] = {}
        system_config = self.system_storage.get(system_config.callable)
        for command, name in system_config.commands.items():
            key_word_arguments[name] = self._commands
        for resource, name in system_config.resources.items():
            key_word_arguments[name] = self.resource_storage.get(resource)
        for component_types, name in system_config.components.items():
            key_word_arguments[name] = self.entity_storage.query(*component_types)
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
        for system_config in self.system_storage.get_all():
            if system_config.callable in self._systems_stop:
                continue
            system_config.callable(**self._extract_system_input(system_config))
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
        return "Control Panel"


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
        self, expression: ()[[Entity], bool]
    ):
        """
        Drop entities using expression of type (entity: Entity) -> bool
        ex:
            lambda entity: entity[Position].x == 17.0
                            and entity[Position].y == 21.0
            where Position is a component of a given entity
        :param expression: ()[[Entity], bool]
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
