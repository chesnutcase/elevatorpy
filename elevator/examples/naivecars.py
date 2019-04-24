from .. import ElevatorSystem
from .. import Elevator
import random
import asyncio
import time


class NaiveElevator(Elevator):
    def __init__(self, *, name="Main Elevator", starting_floor=1, home_floor=1, passenger_pax_capacity=10):
        super().__init__(name=name, starting_floor=starting_floor, home_floor=home_floor, passenger_pax_capacity=passenger_pax_capacity)

    async def step(self, system):
        while system.count_total_passengers() > 0 or len(self.passengers) != 0:
            for passenger in self.passengers:
                for elevator in system.elevators:
                    if elevator is not self:
                        assert passenger not in elevator.passengers
            if self.state == "doors_closed":
                await self.open_doors()
            await self.unload_passengers()
            system.floors[self.floor] = await self.load_passengers(system.floors.get(self.floor, []))
            if len(self.passengers) != 0:
                closest_destination = min([passenger.destination for passenger in self.passengers], key=(lambda d: abs(self.floor - d)))
            else:
                closest_destination = min([floor for (floor, pasengers) in system.floors.items()], key=(lambda d: abs(self.floor - d)))
            await self.goto_floor(closest_destination)
        print("elevator {} done for the day".format(self.name))


class NaiveElevatorSystem(ElevatorSystem):
    def __init__(self, name, *, num_floors=5, num_lifts=3):
        super().__init__(name, num_floors=num_floors, num_lifts=num_lifts)
        for i in range(num_lifts):
            new_elevator = NaiveElevator(name="NaiveElevator {}".format(i))
            new_elevator.time_scale = self.time_scale
            new_elevator.loading_passengers_callbacks["after"].append(self.record_passenger_wait_times)
            new_elevator.unloading_passengers_callbacks["after"].append(self.record_passenger_travel_times)
            self.elevators.append(new_elevator)

    def run_until_system_empty(self):
        time_start = time.time()
        for floor in self.floors.values():
            for passenger in floor:
                passenger.start_time = time_start

        async def start_all_elevators():
            await asyncio.gather(*[elevator.step(self) for elevator in self.elevators])
        asyncio.run(start_all_elevators())
        print("Average wait time: {}".format(sum(self.wait_times) / len(self.wait_times) / self.time_scale))
        print("Average travel time: {}".format(sum(self.travel_times) / len(self.travel_times) / self.time_scale))
