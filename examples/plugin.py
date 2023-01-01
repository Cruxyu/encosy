from dataclasses import dataclass
from encosy import ControlPanel, Entities, Commands, Entity


class Name(str):
    def __repr__(self):
        return "Name({})".format(self)


@dataclass
class Position:
    x: float
    y: float


Human = (
    Name,
    Position
)


class Junk(int):
    pass


@dataclass
class Resolution:
    width: int
    height: int


def my_system(
        commands: Commands,
        resolution: Resolution,
        names_at: Entities(Human),
        junks: Entities(Junk),
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
    for junk in junks:
        print("Some junk: {}".format(junk[0]))
    commands.drop_entities(Junk)
    commands.drop_entities_with_expression(lambda entity: entity[Name] == Name("Artyom"))


def my_plugin(distributor: ControlPanel):
    human_artyom: Human = (
        Name("Artyom"),
        Position(0.0, 0.0),
    )
    human_ilya: Human = (
        Name("Ilya"),
        Position(2.0, 2.0),
    )
    distributor.register_entity(
        Entity(*human_artyom),
        Entity(*human_ilya),
        Entity(Junk(0)),
    )
    distributor.register_systems(my_system)
    distributor.register_resources(Resolution(1920, 1080))


def main():
    print("Starting Distributor Example\n")
    distributor = ControlPanel()
    distributor.register_plugins(my_plugin)
    print(distributor, end="\n\n")
    ticks = 3
    for i in range(ticks):
        print("Tick: {}".format(i))
        distributor.tick()
        print()
    print(distributor, end="\n\n")


if __name__ == '__main__':
    main()
