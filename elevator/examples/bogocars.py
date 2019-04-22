from .. import ElevatorSystem
from .. import Elevator
from .. import Passenger
import random
import asyncio
import time


class BogoElevator(Elevator):
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
            #print(system.floors)
            await self.goto_floor(random.randint(1, system.num_floors))
        print("elevator {} done for the day".format(self.name))


class BogoElevatorSystem(ElevatorSystem):
    def __init__(self, name, *, num_floors=5, num_lifts=3):
        super().__init__(name)
        self.num_floors = num_floors
        self.floors = {
            1: [Passenger(destination=5), Passenger(destination=4), Passenger(destination=3)],
            5: [Passenger(destination=4), Passenger(destination=3), Passenger(destination=2), Passenger(destination=2), Passenger(destination=4), Passenger(destination=3), Passenger(destination=2), Passenger(destination=2), Passenger(destination=4), Passenger(destination=3), Passenger(destination=2), Passenger(destination=2), Passenger(destination=4), Passenger(destination=3), Passenger(destination=2), Passenger(destination=2), Passenger(destination=4), Passenger(destination=3), Passenger(destination=2), Passenger(destination=2), Passenger(destination=4), Passenger(destination=3), Passenger(destination=2), Passenger(destination=2), Passenger(destination=4), Passenger(destination=3), Passenger(destination=2), Passenger(destination=2), Passenger(destination=4), Passenger(destination=3), Passenger(destination=2), Passenger(destination=2), Passenger(destination=4), Passenger(destination=3), Passenger(destination=2), Passenger(destination=2), Passenger(destination=4), Passenger(destination=3), Passenger(destination=2), Passenger(destination=2), Passenger(destination=4), Passenger(destination=3), Passenger(destination=2), Passenger(destination=2), Passenger(destination=4), Passenger(destination=3), Passenger(destination=2), Passenger(destination=2), Passenger(destination=4), Passenger(destination=3), Passenger(destination=2), Passenger(destination=2), Passenger(destination=4), Passenger(destination=3), Passenger(destination=2), Passenger(destination=2), Passenger(destination=4), Passenger(destination=3), Passenger(destination=2), Passenger(destination=2), Passenger(destination=4), Passenger(destination=3), Passenger(destination=2), Passenger(destination=2), Passenger(destination=4), Passenger(destination=3), Passenger(destination=2), Passenger(destination=2)]
        }
        self.wait_times = []
        self.travel_times = []
        for i in range(num_lifts):
            new_elevator = BogoElevator(name="BogoElevator {}".format(i))
            new_elevator.loading_passengers_callbacks["after"].append(self.record_passenger_wait_times)
            new_elevator.unloading_passengers_callbacks["after"].append(self.record_passenger_travel_times)
            self.elevators.append(new_elevator)

    def record_passenger_wait_times(self, **kwargs):
        elevator = kwargs["elevator"]
        boarded_passengers = kwargs["boarded_passengers"]
        time_now = time.time()
        for passenger in boarded_passengers:
            self.wait_times.append(time_now - passenger.start_time)

    def record_passenger_travel_times(self, **kwargs):
        elevator = kwargs["elevator"]
        alighted_passengers = kwargs["alighted_passengers"]
        time_now = time.time()
        for passenger in alighted_passengers:
            self.travel_times.append(time_now - passenger.start_time)

    def run_until_system_empty(self):
        async def start_all_elevators():
            await asyncio.gather(*[elevator.step(self) for elevator in self.elevators])
        asyncio.run(start_all_elevators())
        print("Average wait time: {}".format(sum(self.wait_times) / len(self.wait_times)))
        print("Average travel time: {}".format(sum(self.travel_times) / len(self.travel_times)))
