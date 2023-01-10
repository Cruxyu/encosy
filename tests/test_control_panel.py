import pytest

from encosy import Commands, ControlPanel, Entities, Entity, SystemConfig
from encosy.storage.system_storage import process_system_arguments


class TestControlPanel:
    def test_simple_entity(self, my_component, my_resource, my_control_panel):
        entity = Entity(my_component)
        resource = my_resource

        def my_system(
            entities: Entities[type(my_component)],
            my_resource: type(my_resource),
        ):
            assert len(entities) == 1, "Entities amount is not valid"
            for entity in entities:
                assert len(entity) == 1, "Components amount is not valid"
                assert (
                    entity[type(my_component)].integer == 10
                ), "Entity values are not valid"
                assert (
                    entity[type(my_component)].string == "row"
                ), "Entity values are not valid"

            assert my_resource.count == 1, "Resource values are not valid"

        dist = (
            my_control_panel.register_entities(entity)
            .register_systems(my_system)
            .register_resources(resource)
        )
        assert len(dist.system_storage) == 1, "Systems amount is not valid"
        assert len(dist.entity_storage) == 1, "Entities amount is not valid"
        assert len(dist.resource_storage) == 1, "Resources amount is not valid"
        dist.tick()

    def test_resource(
        self, my_resource, my_control_panel, system_with_resource
    ):
        def system(
            resource: type(my_resource),
        ):
            assert resource.count == 1

        my_control_panel.register_systems(system, system_with_resource)
        my_control_panel.register_resources(my_resource)
        my_control_panel.tick()

    @pytest.mark.timeout(3)
    def test_command_with_pause(self, my_control_panel, system_with_pause):
        my_control_panel.register_systems(system_with_pause)
        my_control_panel.run()

    def test_cp_system_parser(self):
        class MyResource(str):
            pass

        class MyComponent(int):
            pass

        def system(
            commands: Commands,  # noqa
            resource: MyResource,  # noqa
            entities: Entities[MyComponent],
        ):  # noqa
            pass

        system_config = process_system_arguments(system)
        assert system_config.commands == {Commands: 'commands'}
        assert MyResource in system_config.resources
        assert system_config.resources[MyResource] == "resource"
        assert system_config.callable == system
        assert (MyComponent, ) in system_config.components
        assert system_config.components[(MyComponent, )] == "entities"

    def test_system_extraction_commands(
        self, my_control_panel, system_with_commands
    ):
        system_conf = SystemConfig(
            commands={Commands: 'commands'},
            components={},
            callable=system_with_commands,
            resources={},
            types=set()
        )
        my_control_panel.register_systems(system_with_commands)
        kwargs = my_control_panel._extract_system_input(system_conf)
        assert "commands" in kwargs
        assert len(kwargs) == 1
        assert type(kwargs["commands"]) == Commands

    def test_system_deletion(
        self, system_with_entities, system_with_resource, my_control_panel
    ):
        my_control_panel.register_systems(
            system_with_entities, system_with_resource
        )
        assert len(my_control_panel.system_storage) == 2
        my_control_panel._remove_system(system_with_entities)
        assert len(my_control_panel.system_storage) == 1
        assert system_with_resource in my_control_panel.system_storage.systems

    def test_system_deletion_scheduling(
        self, system_with_entities, system_with_resource, my_control_panel
    ):
        my_control_panel.register_systems(
            system_with_entities, system_with_resource
        )
        assert len(my_control_panel.system_storage) == 2
        my_control_panel.schedule_drop_systems(system_with_entities)
        assert len(my_control_panel._systems_to_drop) == 1
        my_control_panel._run_scheduled_drop_systems()
        assert len(my_control_panel._systems_to_drop) == 0
        assert len(my_control_panel.system_storage) == 1

    def test_system_deletion_scheduling_in_app(
        self,
        system_with_entities,
        system_with_resource,
        my_resource,
        my_control_panel,
    ):
        my_control_panel.register_systems(
            system_with_entities, system_with_resource
        )
        my_control_panel.register_resources(my_resource)
        assert len(my_control_panel.system_storage) == 2
        my_control_panel.schedule_drop_systems(system_with_entities)
        assert len(my_control_panel._systems_to_drop) == 1
        my_control_panel.tick()
        assert len(my_control_panel._systems_to_drop) == 0
        assert len(my_control_panel.system_storage) == 1

    def test_resource_deletion(
        self, my_control_panel, my_entity, my_component
    ):
        my_control_panel.register_entities(my_entity)
        assert len(my_control_panel.entity_storage) == 1
        my_control_panel.remove_entities(type(my_component))
        assert len(my_control_panel.entity_storage) == 0

    def test_resource_deletion_expression(
        self,
        my_control_panel,
        my_entity,
        my_entity_multiple,
        my_component,
        my_other_component,
    ):
        my_control_panel.register_entities(my_entity, my_entity_multiple)
        assert len(my_control_panel.entity_storage) == 2
        my_control_panel.drop_entities_with_expression(
            lambda entity: type(my_other_component) in entity
        )
        assert len(my_control_panel.entity_storage) == 1

    def test_request_specific_component(
        self,
        my_control_panel,
        my_entity,
        my_entity_multiple,
        my_other_component,
    ):
        my_control_panel.register_entities(my_entity, my_entity_multiple)
        entities = my_control_panel.entity_storage.get(type(my_other_component))
        assert len(entities) == 1
        assert entities[0] == my_entity_multiple

    def test_plugins_register(
        self, my_control_panel, my_entity, my_resource, system_with_entities
    ):
        def plugin(cp: ControlPanel):
            assert isinstance(cp, ControlPanel)
            cp.register_entities(my_entity)
            cp.register_resources(my_resource)
            cp.register_systems(system_with_entities)

        my_control_panel.register_plugins(plugin)
        assert len(my_control_panel.entity_storage) == 1
        assert len(my_control_panel.resource_storage) == 1
        assert len(my_control_panel.system_storage) == 1

    def test_drop_specific_component(
        self,
        my_control_panel,
        my_entity,
        my_entity_multiple,
        my_other_component,
    ):
        my_control_panel.register_entities(my_entity, my_entity_multiple)
        my_control_panel.remove_entities(type(my_other_component))
        assert len(my_control_panel.entity_storage) == 1

    def test_drop_specific_component_with_expression(
        self,
        my_control_panel,
        my_entity,
        my_entity_multiple,
        my_other_component,
    ):
        my_control_panel.register_entities(my_entity, my_entity_multiple)
        my_control_panel.drop_entities_with_expression(
            lambda entity: entity[type(my_other_component)].integer == 10
        )
        assert len(my_control_panel.entity_storage) == 1

    def test_stop_start_systems(self, my_control_panel, my_ticker):
        def system(resource: type(my_ticker)):
            resource.tick += 1

        my_control_panel.register_resources(my_ticker)
        my_control_panel.register_systems(system)
        assert system not in my_control_panel._systems_stop

        my_control_panel.tick()
        assert my_ticker.tick == 1
        my_control_panel.stop_systems(system)
        assert system in my_control_panel._systems_stop
        my_control_panel.tick()
        assert my_ticker.tick == 1

        my_control_panel.start_systems(system)
        assert system not in my_control_panel._systems_stop
        my_control_panel.tick()
        assert my_ticker.tick == 2

    def test_repr(self, my_control_panel):
        assert (
            str(my_control_panel) == "Control Panel"
        )
