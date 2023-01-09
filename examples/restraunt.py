import random
from dataclasses import dataclass
from time import sleep
from encosy import Commands, ControlPanel, Entities, Entity


# resource
@dataclass
class Tick:
    tick: int
    maxim: int


# component
@dataclass
class Reserved:
    reserved: int


# component
class VIP(int):
    pass


# component
class Name(str):
    pass


# component
class SleepTime(float):
    pass


# "bundle"
Human = Name

# bundle
Chair = Reserved, VIP


def entry_sys(commands: Commands, chairs: Entities[Chair]):
    name = input("Hello, what is your name, sir/madam?: ")
    if not name:
        return
    vip = bool(input("Do you want a chair with high level of comfort?: "))
    human = Entity(Name(name))
    for chair in chairs:
        if chair[Reserved].reserved <= 0 and chair[VIP] == int(vip):
            print("Sure, we can serve a chair for you!")
            commands.register_entities(human)
            chair[Reserved].reserved = 3
            break
    else:
        print("You a looser, bye!")


names_idx = 0


def gen_random(names_idx: int):
    return Entity(Name("Name{}".format(names_idx))), random.randint(0, 9) == 0


def fake_entry_sys(commands: Commands, chairs: Entities[Chair]):
    global names_idx
    new_total = random.randint(1, 3)
    hv = [gen_random(names_idx + i) for i in range(new_total)]
    names_idx += new_total
    for human, vip in hv:
        for chair in chairs:
            if chair[Reserved].reserved <= 0 and chair[VIP] == int(vip):
                # print("Sure, we can serve a chair for you!")
                commands.register_entities(human)
                chair[Reserved].reserved = random.randint(1, 10)
                break
    # else:
    #     print("You a looser, bye!")


def exit_sys(
    commands: Commands, chairs: Entities[Chair], humans: Entities[Human]
):
    human_to_drop = 0
    for chair in chairs:
        chair[Reserved].reserved -= 1
        if chair[Reserved].reserved == 0:
            commands.drop_entities_with_expression(
                lambda entity: entity[Name] == humans[human_to_drop][Name]
            )
            human_to_drop += 1


def tick_sys(commands: Commands, ticks: Tick):
    ticks.tick += 1
    if ticks.tick == ticks.maxim:
        commands.pause_control_panel()


def print_sys(tick: Tick, chairs: Entities[Chair], humans: Entities[Human]):
    print(f"Tick: {tick.tick}")
    print("  # Chairs")
    for k, chair in enumerate(chairs, start=1):
        print(
            "    {}. Chair{} is {}".format(
                k,
                " VIP" if chair[VIP] else "",
                "Reserved for {}".format(chair[Reserved].reserved)
                if chair[Reserved].reserved > 0
                else "Not Reserved",
            )
        )
    print("  # Human")
    for k, human in enumerate(humans, start=1):
        print(f"    {k}. {human[Name]}")


def sleep_system(sleet_time: SleepTime):
    sleep(sleet_time)


def main():
    # print("Starting...")
    ControlPanel().register_resources(
        Tick(0, 100), SleepTime(0.1)
    ).register_systems(
        tick_sys,
        print_sys,
        exit_sys,
        fake_entry_sys,
        sleep_system
    ).register_entities(
        *[Entity(Reserved(0), VIP(0)) for _ in range(10)],
        *[Entity(Reserved(0), VIP(1)) for _ in range(1)],
        Entity(Reserved(2), VIP(1)),
        Entity(Name("Artyom")),
    ).run()
    # print("Stopping...")


if __name__ == "__main__":
    main()
