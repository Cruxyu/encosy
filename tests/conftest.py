import pytest
from dataclasses import dataclass
from encosy import Entities, Entity, Commands, ControlPanel


@dataclass
class MyComponent:
    integer: int
    string: str


@dataclass
class MyOtherComponent:
    integer: int
    string: str


@dataclass
class MyResource:
    count: int


@dataclass
class Ticker:
    tick: int


class PermanentResource(int):
    pass


@pytest.fixture
def my_component():
    integer = 10
    string = "row"
    return MyComponent(integer, string)


@pytest.fixture
def my_entity():
    integer = 10
    string = "row"
    return Entity(MyComponent(integer, string))


@pytest.fixture
def my_entity_multiple():
    integer = 10
    string = "row"
    return Entity(
        MyComponent(integer, string), MyOtherComponent(integer, string)
    )


@pytest.fixture
def my_other_component():
    integer = 10
    string = "row"
    return MyOtherComponent(integer, string)


@pytest.fixture
def my_resource():
    return MyResource(1)


@pytest.fixture
def my_ticker():
    return Ticker(0)


@pytest.fixture
def my_control_panel():
    control_panel = ControlPanel()
    return control_panel


@pytest.fixture
def system_with_commands():
    def system(
        commands: Commands,
    ):
        assert isinstance(commands, Commands)

    return system


@pytest.fixture
def system_with_entities():
    def system(entities: Entities[Entity[MyComponent]]):
        assert isinstance(entities, Entities)

    return system


@pytest.fixture
def system_with_resource():
    def system(
        resource: MyResource,
    ):
        assert isinstance(resource, MyResource)

    return system


@pytest.fixture
def system_with_pause():
    def system(
        commands: Commands,
    ):
        commands.pause_control_panel()

    return system


@pytest.fixture
def system_with_resume():
    def system(
        commands: Commands,
    ):
        commands.resume_control_panel()

    return system