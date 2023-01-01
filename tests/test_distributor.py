from encosy import Distributor, Entity, Entities
from dataclasses import dataclass


class TestDistributor:
    def test_simple_entity(self):
        @dataclass
        class MyComponent:
            integer: int
            string: str
        integer = 10
        string = "my"
        entity = Entity(MyComponent(integer, string))
        resource = MyComponent(integer+integer, string+string)

        def my_system(entities: Entities(MyComponent), my_resource: MyComponent):
            assert len(entities) == 1, "Entities amount is not valid"
            for entity in entities:
                assert len(entity) == 1, "Components amount is not valid"
                assert entity[0].integer == integer, "Entity values are not valid"
                assert entity[0].string == string, "Entity values are not valid"

            assert my_resource.integer == integer+integer, "Resource values are not valid"
            assert my_resource.string == string+string, "Resource values are not valid"

        dist = Distributor().register_entity(entity).register_systems(my_system).register_resources(resource)
        assert len(dist.get_systems()) == 1, "Systems amount is not valid"
        assert len(dist.get_entities()) == 1, "Entities amount is not valid"
        assert len(dist.get_resources()) == 1, "Resources amount is not valid"
        dist.tick()