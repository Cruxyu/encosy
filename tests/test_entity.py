from encosy import Entity
from dataclasses import dataclass


class TestEntity:
    def test_simple_single(self):
        @dataclass
        class MyComponent:
            integer: int
            string: str

        integer = 10
        string = "row"
        entity = Entity(MyComponent(integer, string))
        assert MyComponent in entity, "Component have not been found"
        assert len(entity) == 1, "Length is not equal 1"
        assert entity[MyComponent], "Can't get component from entity"

    def test_simple_multiple(self):
        @dataclass
        class MyComponent1:
            integer: int
            string: str

        integer = 10
        string = "row"
        component1 = MyComponent1(integer, string)

        @dataclass
        class MyComponent2:
            integer: int
            string: str

        integer = 10
        string = "row"
        component2 = MyComponent2(integer, string)

        entity = Entity(component1, component2)

        assert (
            MyComponent1 in entity and MyComponent2 in entity
        ), "Not all components in entity"
        assert len(entity) == 2, "Length of entity is not equal 2"
        assert (
            entity[MyComponent1] and entity[MyComponent2]
        ), "Can't get some of the required components"
