from time import sleep

from encosy import Distributor, Commands, Entity, Entities
from dataclasses import dataclass
from faker import Faker
import random
fake = Faker()


# resource
@dataclass
class Tick:
    tick: int


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
Chair = (Reserved, VIP)


def entry_sys(commands: Commands, chairs: Entities(Chair)):
    name = input("Hello, what is your name, sir/madam?: ")
    if not name:
        return
    vip = bool(input("Do you want a chair with high level of comfort?: "))
    human = Entity(Name(name))
    for chair in chairs:
        if chair[0].reserved <= 0 and chair[1] == int(vip):
            print("Sure, we can serve a chair for you!")
            commands.register_entity(human)
            chair[0].reserved = 3
            break
    else:
        print("You a looser, bye!")


def fake_entry_sys(commands: Commands, chairs: Entities(Chair)):
    name = fake.name()
    if not name:
        return
    vip = random.randint(0, 9) == 0
    # print("New guest: {} is {}".format(name, 'VIP' if vip else "Broke"))
    human = Entity(Name(name))
    for chair in chairs:
        if chair[0].reserved <= 0 and chair[1] == int(vip):
            # print("Sure, we can serve a chair for you!")
            commands.register_entity(human)
            chair[0].reserved = random.randint(1, 1250)
            break
    # else:
    #     print("You a looser, bye!")


def exit_sys(commands: Commands, chairs: Entities(Chair), humans: Entities(Human)):
    human_to_drop = 0
    for chair in chairs:
        chair[0].reserved -= 1
        if chair[0].reserved == 0:
            commands.drop_entities_with_expression(
                lambda entity: entity[Name] == humans[human_to_drop][0]
            )
            human_to_drop += 1


def tick_sys(commands: Commands, ticks: Tick):
    ticks.tick += 1
    if ticks.tick == 5000:
        commands.pause_distributor()


def print_sys(tick: Tick, chairs: Entities(Chair), humans: Entities(Human)):
    print(f"Tick: {tick.tick}")
    print("  # Chairs")
    for k, chair in enumerate(chairs, start=1):
        print("    {}. Chair{} is {}".format(
            k,
            ' VIP' if chair[1] else '',
            'Reserved for {}'.format(chair[0].reserved) if chair[0].reserved > 0 else 'Not Reserved',
        ))
    print("  # Human")
    for k, human in enumerate(humans, start=1):
        print(f"    {k}. {human[0]}")


def sleep_system(sleet_time: SleepTime):
    sleep(sleet_time)


def main():
    # print("Starting...")
    Distributor().register_resources(
        Tick(0),
        SleepTime(1.0)
    ).register_systems(
        tick_sys,
        # print_sys,
        exit_sys,
        fake_entry_sys,
        # sleep_system
    ).register_entity(
        *[Entity(Reserved(0), VIP(0)) for _ in range(1000)],
        Entity(Reserved(0), VIP(1)),

        Entity(Reserved(2), VIP(1)),
        Entity(Name("Artyom"))
    ).run()
    # print("Stopping...")


if __name__ == "__main__":
    main()
