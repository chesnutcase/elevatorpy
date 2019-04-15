from elevator import Elevator
from .utils import check_stdout


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
