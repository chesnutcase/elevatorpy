from ... import Passenger
import random


def generate_n_passengers_with_random_destinations(n, *, max_floor=8):
    passengers = []
    for i in range(n):
        passengers.append(Passenger(destination=random.randint(1, max_floor)))
    return passengers


def load_nine_am():
    return {
        1: generate_n_passengers_with_random_destinations(11),
        2: generate_n_passengers_with_random_destinations(42),
        3: generate_n_passengers_with_random_destinations(9),
        4: generate_n_passengers_with_random_destinations(30),
        5: generate_n_passengers_with_random_destinations(10),
        6: generate_n_passengers_with_random_destinations(10),
        7: generate_n_passengers_with_random_destinations(10),
        7: generate_n_passengers_with_random_destinations(8),
    }


def load_twelve_pm():
    return {
        1: generate_n_passengers_with_random_destinations(9),
        2: generate_n_passengers_with_random_destinations(10),
        3: generate_n_passengers_with_random_destinations(18),
        4: generate_n_passengers_with_random_destinations(17),
        5: generate_n_passengers_with_random_destinations(13),
        6: generate_n_passengers_with_random_destinations(39),
        7: generate_n_passengers_with_random_destinations(10),
        8: generate_n_passengers_with_random_destinations(7)
    }


def load_five_pm():
    return {
        1: generate_n_passengers_with_random_destinations(12),
        2: generate_n_passengers_with_random_destinations(10),
        3: generate_n_passengers_with_random_destinations(14),
        4: generate_n_passengers_with_random_destinations(39),
        5: generate_n_passengers_with_random_destinations(9),
        6: generate_n_passengers_with_random_destinations(40),
        7: generate_n_passengers_with_random_destinations(17),
        8: generate_n_passengers_with_random_destinations(12)
    }
