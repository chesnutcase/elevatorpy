from ... import Passenger
import random


def generate_n_passengers_with_random_destinations(n, *, source=1, max_floor=8):
    passengers = []

    def generate_destination(source, max):
        destination = source
        while destination == source:
            destination = random.randint(1, max)
        return destination
    for i in range(n):
        passengers.append(Passenger(destination=generate_destination(source, max_floor)))
    return passengers


def load_nine_am():
    return {
        1: generate_n_passengers_with_random_destinations(11, source=1),
        2: generate_n_passengers_with_random_destinations(42, source=2),
        3: generate_n_passengers_with_random_destinations(9, source=3),
        4: generate_n_passengers_with_random_destinations(30, source=4),
        5: generate_n_passengers_with_random_destinations(10, source=5),
        6: generate_n_passengers_with_random_destinations(10, source=6),
        7: generate_n_passengers_with_random_destinations(10, source=7),
        8: generate_n_passengers_with_random_destinations(8, source=8),
    }


def load_twelve_pm():
    return {
        1: generate_n_passengers_with_random_destinations(9, source=1),
        2: generate_n_passengers_with_random_destinations(10, source=2),
        3: generate_n_passengers_with_random_destinations(18, source=3),
        4: generate_n_passengers_with_random_destinations(17, source=4),
        5: generate_n_passengers_with_random_destinations(13, source=5),
        6: generate_n_passengers_with_random_destinations(39, source=6),
        7: generate_n_passengers_with_random_destinations(10, source=7),
        8: generate_n_passengers_with_random_destinations(7, source=8)
    }


def load_five_pm():
    return {
        1: generate_n_passengers_with_random_destinations(12, source=1),
        2: generate_n_passengers_with_random_destinations(10, source=2),
        3: generate_n_passengers_with_random_destinations(14, source=3),
        4: generate_n_passengers_with_random_destinations(39, source=4),
        5: generate_n_passengers_with_random_destinations(9, source=5),
        6: generate_n_passengers_with_random_destinations(40, source=6),
        7: generate_n_passengers_with_random_destinations(17, source=7),
        8: generate_n_passengers_with_random_destinations(12, source=8)
    }
