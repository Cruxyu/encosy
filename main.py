from dataclasses import dataclass
from pyecs.distributor import Distributor, Entities, Commands
from pyecs.entity import Entity


class Name(str):
    pass


@dataclass
class Position:
    x: float
    y: float


Human = (Name, Position)


@dataclass
class Resolution:
    width: int
    height: int


def my_system(
        commands: Commands,
        resolution: Resolution,
        names_at: Entities(Human),
):
    print("My Resolution: {}".format(resolution))
    new_entity = Entity(
        Name("Human №{}".format(len(names_at))),
        Position(2 + len(names_at), 2 + len(names_at))
    )
    print("Adding an Entity: {}".format(new_entity))
    commands.register_entity(new_entity)
    for name_at in names_at:
        name = name_at[0]
        position = name_at[1]
        print(f'Hi, {name}, you at {position}')
        position.x += 1
        position.y += 1


def my_plugin(distributor: Distributor):
    human_artyom: Human = (
        Name("Artyom"),
        Position(0.0, 0.0),
    )
    distributor.register_entity(Entity(*human_artyom))
    distributor.register_systems(my_system)
    distributor.register_resources(Resolution(1920, 1080))

def main():
    print("Starting Distributor Example\n")
    distributor = Distributor()
    distributor.register_plugins(my_plugin)
    print(distributor, end="\n\n")
    ticks = 3
    for i in range(ticks):
        print("Tick: {}".format(i))
        distributor.dispense()
        print()
    print(distributor, end="\n\n")


if __name__ == '__main__':
    main()
