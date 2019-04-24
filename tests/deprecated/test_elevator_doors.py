from elevator import Elevator
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


def test_elevator_can_open_doors_on_start(capsys):
    elevator = Elevator(name="Elevator 1")
    doors_opening_message = Elevator.MESSAGE_TEMPLATES["doors_opening"].format(elevator.name)
    elevator.open_doors()
    stdout = capsys.readouterr().out.split("\n")
    assert check_stdout([doors_opening_message], stdout)
