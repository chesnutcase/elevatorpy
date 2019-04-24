from elevator import Elevator
from elevator import Passenger


def test_elevator_can_only_carry_passengers_when_door_is_open():
    elevator = Elevator(name="Elevator 1")
    assert elevator.door_status == "closed"
    passenger_1 = Passenger(destination=2)
    try:
        elevator.load_passengers([passenger_1])
        assert False, "No Exception was thrown"
    except Exception as ex:
        assert str(ex) == "You tried to load passengers into {} while it was in state {}!".format(elevator.name, elevator.state)


def test_elevator_can_carry_passengers_to_one_floor(capsys):
    elevator = Elevator(name="Elevator 1")
    passenger_1 = Passenger(destination=2)
    passenger_2 = Passenger(destination=2)
    elevator.open_doors()
    elevator.load_passengers([passenger_1, passenger_2])
    assert passenger_1 in elevator.passengers
    assert passenger_2 in elevator.passengers
    elevator.goto_floor(2)
    elevator.unload_passengers()
    assert len(elevator.passengers) == 0


def test_elevator_will_not_alight_passengers_at_wrong_floor():
    elevator = Elevator(name="Elevator 1")
    passenger_1 = Passenger(destination=2)
    passenger_2 = Passenger(destination=2)
    elevator.open_doors()
    elevator.load_passengers([passenger_1, passenger_2])
    elevator.goto_floor(3)
    elevator.unload_passengers()
    assert len(elevator.passengers) == 2


def test_elevator_can_alight_different_passengers_at_different_floors():
    elevator = Elevator(name="Elevator 1")
    passenger_1 = Passenger(destination=2)
    passenger_2 = Passenger(destination=3)
    elevator.open_doors()
    elevator.load_passengers([passenger_1, passenger_2])
    elevator.goto_floor(2)
    elevator.unload_passengers()
    assert passenger_1 not in elevator.passengers
    assert passenger_2 in elevator.passengers
    assert len(elevator.passengers) == 1
    elevator.goto_floor(3)
    elevator.unload_passengers()
    assert passenger_1 not in elevator.passengers
    assert passenger_2 not in elevator.passengers
    assert len(elevator.passengers) == 0
