from elevator import Elevator
from ..utils import check_stdout
import pytest
import asyncio
import time


@pytest.mark.asyncio
async def test_elevator_can_report_door_status():
    elevator = Elevator(name="Elevator 1")
    if elevator.door_status == "closed":
        time_1 = time.time()
        await elevator.open_doors()
        assert elevator.door_status == "open"
        assert time.time() - time_1 > elevator.door_action_duration
    elif elevator.door_status == "open":
        time_1 = time.time()
        await elevator.close_doors()
        assert elevator.door_status == "closed"
        assert time.time() - time_1 > elevator.door_action_duration
    else:
        assert False, "{} starting door status appears to be neither open or closed".format(elevator.name)


@pytest.mark.asyncio
async def test_elevator_can_open_doors_on_start(capsys):
    elevator = Elevator(name="Elevator 1")
    doors_opening_message = Elevator.MESSAGE_TEMPLATES["doors_opening"].format(elevator.name)
    time_1 = time.time()
    await elevator.open_doors()
    stdout = capsys.readouterr().out.split("\n")
    assert check_stdout([doors_opening_message], stdout)
    assert time.time() - time_1 > elevator.door_action_duration
