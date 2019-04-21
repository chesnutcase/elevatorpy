from elevator import Elevator
from ..utils import check_stdout
import pytest
import asyncio
import time


@pytest.mark.asyncio
async def test_elevator_can_go_up(capsys):
    elevator = Elevator(name="Elevator 1")
    time_1 = time.time()
    await elevator.goto_floor(10)
    delta_t = time.time() - time_1
    assert delta_t > (elevator.floor_movement_duration * (10 - 1))
    stdout = capsys.readouterr().out.split("\n")
    going_up_message = Elevator.MESSAGE_TEMPLATES["departure"].format(elevator.name, "up", 10)
    arrival_message = Elevator.MESSAGE_TEMPLATES["arrival"].format(elevator.name, 10)
    assert check_stdout([going_up_message, arrival_message], stdout)


@pytest.mark.asyncio
async def test_elevator_can_go_down(capsys):
    elevator = Elevator(name="Elevator 1", starting_floor=10)
    time_1 = time.time()
    await elevator.goto_floor(1)
    delta_t = time.time() - time_1
    assert delta_t > (elevator.floor_movement_duration * (10 - 1))
    stdout = capsys.readouterr().out.split("\n")
    going_down_message = Elevator.MESSAGE_TEMPLATES["departure"].format(elevator.name, "down", 1)
    arrival_message = Elevator.MESSAGE_TEMPLATES["arrival"].format(elevator.name, 1)
    assert check_stdout([going_down_message, arrival_message], stdout)


@pytest.mark.asyncio
async def test_elevator_can_return_home(capsys):
    elevator = Elevator(name="Elevator 1")
    assert elevator.floor == elevator.home_floor
    await elevator.goto_floor(10)
    captured = capsys.readouterr().out.split("\n")
    going_up_message = Elevator.MESSAGE_TEMPLATES["departure"].format(elevator.name, "up", 10)
    arrival_message = Elevator.MESSAGE_TEMPLATES["arrival"].format(elevator.name, 10)
    assert check_stdout([going_up_message, arrival_message], captured)
    assert elevator.floor == 10
    await elevator.goto_home()
    doors_closing_message = Elevator.MESSAGE_TEMPLATES["doors_closing"].format(elevator.name)
    going_down_message = Elevator.MESSAGE_TEMPLATES["departure"].format(elevator.name, "down", elevator.home_floor)
    arrival_message = Elevator.MESSAGE_TEMPLATES["arrival"].format(elevator.name, elevator.home_floor)
    captured = capsys.readouterr().out.split("\n")
    assert check_stdout([doors_closing_message, going_down_message, arrival_message], captured)
    assert elevator.floor == elevator.home_floor
