from elevator.examples.simplecars import SimpleElevator
from elevator import Passenger
from ..utils import check_stdout
import pytest
import asyncio


@pytest.mark.asyncio
async def test_will_only_take_passengers_in_the_same_direction(capsys):
    elevator = SimpleElevator(name="test", starting_floor=5)
    elevator.intended_direction = "up"
    print(elevator.floor)
    await elevator.open_doors()
    passengers = [
        Passenger(destination=1),
        Passenger(destination=2),
        Passenger(destination=3),
        Passenger(destination=4),
        Passenger(destination=6),
        Passenger(destination=7)
    ]
    rejected_passengers = await elevator.load_passengers(passengers)
    assert len(rejected_passengers) == 4
    for passenger in rejected_passengers:
        assert passenger.destination < 5
