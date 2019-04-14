from elevator import Elevator
from elevator import Passenger
from .utils import check_stdout


def test_elevator_can_report_door_status():
    elevator = Elevator(name="Elevator 1")
    if elevator.door_status == "closed":
        elevator.open_doors()
        assert elevator.door_status == "open"
    elif elevator.door_status == "open":
        elevator.close_doors()
        assert elevator.door_status == "closed"
    else:
        assert False, "{} starting door status appears to be neither open or closed".format(elevator.name)


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


def test_elevator_can_open_doors_on_start(capsys):
    elevator = Elevator(name="Elevator 1")
    doors_opening_message = Elevator.MESSAGE_TEMPLATES["doors_opening"].format(elevator.name)
    elevator.open_doors()
    stdout = capsys.readouterr().out.split("\n")
    assert check_stdout([doors_opening_message], stdout)


def test_elevator_can_start_at_another_floor(capsys):
    elevator = Elevator(name="Elevator 1", starting_floor=10)
    assert elevator.floor == 10


def test_elevator_can_go_up(capsys):
    elevator = Elevator(name="Elevator 1")
    elevator.goto_floor(10)
    stdout = capsys.readouterr().out.split("\n")
    going_up_message = Elevator.MESSAGE_TEMPLATES["departure"].format(elevator.name, "up", 10)
    arrival_message = Elevator.MESSAGE_TEMPLATES["arrival"].format(elevator.name, 10)
    assert check_stdout([going_up_message, arrival_message], stdout)


def test_elevator_can_go_down(capsys):
    elevator = Elevator(name="Elevator 1", starting_floor=10)
    elevator.goto_floor(1)
    stdout = capsys.readouterr().out.split("\n")
    going_down_message = Elevator.MESSAGE_TEMPLATES["departure"].format(elevator.name, "down", 1)
    arrival_message = Elevator.MESSAGE_TEMPLATES["arrival"].format(elevator.name, 1)
    assert check_stdout([going_down_message, arrival_message], stdout)


def test_elevator_can_return_home(capsys):
    elevator = Elevator(name="Elevator 1")
    assert elevator.floor == elevator.home_floor
    elevator.goto_floor(10)
    captured = capsys.readouterr().out.split("\n")
    going_up_message = Elevator.MESSAGE_TEMPLATES["departure"].format(elevator.name, "up", 10)
    arrival_message = Elevator.MESSAGE_TEMPLATES["arrival"].format(elevator.name, 10)
    assert check_stdout([going_up_message, arrival_message], captured)
    assert elevator.floor == 10
    elevator.goto_home()
    doors_closing_message = Elevator.MESSAGE_TEMPLATES["doors_closing"].format(elevator.name)
    going_down_message = Elevator.MESSAGE_TEMPLATES["departure"].format(elevator.name, "down", elevator.home_floor)
    arrival_message = Elevator.MESSAGE_TEMPLATES["arrival"].format(elevator.name, elevator.home_floor)
    captured = capsys.readouterr().out.split("\n")
    assert check_stdout([doors_closing_message, going_down_message, arrival_message], captured)
    assert elevator.floor == elevator.home_floor
