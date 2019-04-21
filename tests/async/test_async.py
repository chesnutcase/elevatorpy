from elevator import Elevator
from ..utils import check_stdout
import pytest
import asyncio
import time


def test_async(capsys):
    async def open_and_close_doors(ele):
        await ele.open_doors()
        await ele.close_doors()

    elevator_1 = Elevator(name="Elevator 1")
    elevator_2 = Elevator(name="Elevator 2")
    expected_messages_order = [
        Elevator.MESSAGE_TEMPLATES["doors_opening"].format(elevator_1.name),
        Elevator.MESSAGE_TEMPLATES["doors_opening"].format(elevator_2.name),
        Elevator.MESSAGE_TEMPLATES["doors_closing"].format(elevator_1.name),
        Elevator.MESSAGE_TEMPLATES["doors_closing"].format(elevator_2.name)
    ]

    async def main():
        await asyncio.gather(open_and_close_doors(elevator_1), open_and_close_doors(elevator_2))

    time_1 = time.time()
    asyncio.run(main())

    stdout = capsys.readouterr().out.split("\n")
    delta_time = time.time() - time_1
    # assuming door_action duration is the same
    assert delta_time > elevator_1.door_action_duration * 2 and delta_time < elevator_2.door_action_duration * 4
    check_stdout(expected_messages_order, stdout)
