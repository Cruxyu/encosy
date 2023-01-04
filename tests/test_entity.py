import pytest

from encosy import Entity


class TestEntity:
    def test_simple_single(self, my_component):
        entity = Entity(my_component)
        assert type(my_component) in entity, "Component have not been found"
        assert len(entity) == 1, "Length is not equal 1"
        assert entity[type(my_component)], "Can't get component from entity"

    def test_simple_multiple(self, my_component, my_other_component):

        entity = Entity(my_component, my_other_component)

        assert (
            type(my_component) in entity and type(my_other_component) in entity
        ), "Not all components in entity"
        assert len(entity) == 2, "Length of entity is not equal 2"
        assert (
            entity[type(my_component)] and entity[type(my_other_component)]
        ), "Can't get some of the required components"

    def test_with_error(self, my_component):
        entity = Entity(my_component)

        with pytest.raises(KeyError):
            _ = entity[int]
