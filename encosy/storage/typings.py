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

        Args:
            *components: any items
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

        Args:
            control_panel:
        """
        self._control_panel = control_panel

    def register_entities(self, *entities) -> list[Any]:
        """
        Register entities for control panel

        Args:
            *entities: any entities

        Returns:
            self

        """
        return self._control_panel.register_entities(*entities)

    def drop_entities(self, *components) -> 'Commands':
        """
        Drop entities by components

        Args:
            *components: drop entities by components

        Returns:
            self

        """
        self._control_panel.remove_entities(*components)
        return self

    def drop_entities_with_expression(self, expression: Callable[[Any], Any]) -> 'Commands':
        """
        Drop entities using expression of type (entity: Entity) -> bool
        ex:
            lambda entity: entity[Position].x == 17.0
                            and entity[Position].y == 21.0
            where Position is a component of a given entity

        Args:
            expression: (Entity) -> True or False

        Returns:
            self

        """
        self._control_panel.drop_entities_with_expression(expression)
        return self

    def stop_systems(self, *systems) -> 'Commands':
        """
        Prevents systems from executing

        Args:
            *systems: any callable

        Returns:
            self

        """
        self._control_panel.stop_systems(*systems)
        return self

    def start_systems(self, *systems) -> 'Commands':
        """
        Allows systems to be executed

        Args:
            *systems: any callable

        Returns:
            self

        """
        self._control_panel.start_systems(*systems)
        return self

    def schedule_drop_systems(self, *systems) -> 'Commands':
        """
        Completely remove system, but only after current tick

        Args:
            *systems: any callable

        Returns:
            self

        """
        self._control_panel.schedule_drop_systems(*systems)
        return self

    def pause_control_panel(self) -> 'Commands':
        """
        Exits from run at the next tick and prevents tick to be executed
        until resume_control_panel is called

        Returns:
            self

        """
        self._control_panel.pause()
        return self

    def resume_control_panel(self) -> 'Commands':
        """
        Resume run but only after control_panel.run() is called

        Returns:
            self

        """
        self._control_panel.resume()
        return self
