from encosy import Commands


class TestCommands:
    def test_register_entities(
        self, my_control_panel, my_entity, my_entity_multiple
    ):
        def system(commands: Commands):
            commands.register_entities(my_entity_multiple)

        my_control_panel.register_entities(my_entity).register_systems(system)
        assert len(my_control_panel.entity_storage) == 1
        my_control_panel.tick()
        assert len(my_control_panel.entity_storage) == 2

    def test_drop_entities(
        self,
        my_control_panel,
        my_entity,
        my_entity_multiple,
        my_other_component,
    ):
        def system(commands: Commands):
            commands.drop_entities(type(my_other_component))

        my_control_panel.register_entities(
            my_entity, my_entity_multiple
        ).register_systems(system)
        assert len(my_control_panel.entity_storage) == 2
        my_control_panel.tick()
        assert len(my_control_panel.entity_storage) == 1

    def test_drop_entities_expression(
        self,
        my_control_panel,
        my_entity,
        my_entity_multiple,
        my_other_component,
    ):
        def system(commands: Commands):
            commands.drop_entities_with_expression(
                lambda entity: type(my_other_component) in entity
            )

        my_control_panel.register_entities(
            my_entity, my_entity_multiple
        ).register_systems(system)
        assert len(my_control_panel.entity_storage) == 2
        my_control_panel.tick()
        assert len(my_control_panel.entity_storage) == 1

    def test_stop_and_start_systems(
        self,
        my_control_panel,
        my_entity,
        my_entity_multiple,
        system_with_entities,
    ):
        def system_stop(commands: Commands):
            commands.stop_systems(system_with_entities)

        def system_start(commands: Commands):
            commands.start_systems(system_with_entities)

        my_control_panel.register_entities(my_entity).register_systems(
            system_stop, system_with_entities
        )
        assert len(my_control_panel._systems_stop) == 0
        my_control_panel.tick()
        assert len(my_control_panel._systems_stop) == 1

        my_control_panel._remove_system(system_stop)
        my_control_panel.register_systems(system_start)
        my_control_panel.tick()
        assert len(my_control_panel._systems_stop) == 0

    def test_drop_systems(
        self,
        my_control_panel,
        my_entity,
        my_entity_multiple,
        system_with_entities,
    ):
        def system(commands: Commands):
            commands.schedule_drop_systems(system_with_entities)

        my_control_panel.register_entities(my_entity).register_systems(
            system, system_with_entities
        )
        assert len(my_control_panel.system_storage) == 2
        my_control_panel.tick()
        assert len(my_control_panel.system_storage) == 1

    def test_stop_and_resume_cp(self, my_control_panel, my_ticker):
        def system(resource: type(my_ticker)):
            resource.tick += 1

        def pause_sp_system(commands: Commands):
            commands.pause_control_panel()

        def resume_sp_system(commands: Commands):
            commands.resume_control_panel()

        my_control_panel.register_resources(my_ticker)
        my_control_panel.register_systems(system, pause_sp_system)
        assert my_control_panel._stop is False
        my_control_panel.tick()
        assert my_control_panel._stop is True
        assert my_ticker.tick == 1
        my_control_panel.tick()
        assert my_ticker.tick == 1
        my_control_panel.register_systems(resume_sp_system)
        my_control_panel._stop = False
        my_control_panel.tick()
        assert my_control_panel._stop is False
        assert my_ticker.tick == 2
        my_control_panel.tick()
        assert my_control_panel._stop is False
        assert my_ticker.tick == 3
