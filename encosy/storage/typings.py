from dataclasses import dataclass
from typing import Any, Callable, TypeVar

T = TypeVar("T")


@dataclass
class SystemConfig:
    callable: Callable[[Any], Any]
    commands: dict[type, str]
    resources: dict[type, str]
    components: dict[tuple, str]
    types: set[type]


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


class Commands:
    def __init__(self, control_panel):
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
        self._control_panel.remove_entities(*components)
        return self

    def drop_entities_with_expression(self, expression: Callable[[Any], Any]):
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
