from .. import ElevatorSystem
from .. import Elevator
import random
import asyncio
import time


class NCElevator(Elevator):
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
            # print(system.floors)
            await self.goto_floor(random.randint(1, system.num_floors))
        print("elevator {} done for the day".format(self.name))


class NCElevatorSystem(ElevatorSystem):
    def __init__(self, name, *, num_floors=5, num_lifts=3):
        super().__init__(name, num_floors=num_floors, num_lifts=num_lifts)
        for i in range(num_lifts):
            new_elevator = NCElevator(name="NCElevator {}".format(i))
            new_elevator.time_scale = self.time_scale
            new_elevator.loading_passengers_callbacks["after"].append(self.record_passenger_wait_times)
            new_elevator.unloading_passengers_callbacks["after"].append(self.record_passenger_travel_times)
            self.elevators.append(new_elevator)

    def gather_calls(self):
        for floor, passengers in self.floors.items():
            self.floor_calls[floor] = {
                "up": any([passenger for passenger in passengers if passenger.destination > floor]),
                "down": any([passenger for passenger in passengers if passenger.destination < floor]),
            }
        return sum([len([True for v in calls.values if v]) for floor, calls in self.floor_calls])

    def evaluate_fs(self, elevator, call_floor, call_direction):
        if elevator.state == "moving":
            same_direction_up = elevator.next > elevator.floor and call_floor > elevator.floor
            same_direction_down = elevator.next < elevator.floor and call_floor < elevator.floor
            if same_direction_up or same_direction_down:
                elevator_direction = "up" if elevator.next > elevator.floor else "down"
                if elevator_direction == call_direction:
                    return self.num_floors + 2 - (call_floor - elevator.floor)
                else:
                    return self.num_floors + 1 - (call_floor - elevator.floor)
            else:
                return 1
        else:
            return 0

    def run_until_system_empty(self):
        time_start = time.time()

        while self.gather_calls() > 0:
            for floor, calls in self.floor_calls.items():
                for direction in calls:
                    elevator_scores = [self.evaluate_fs(elevator, floor, direction) for elevator in self.elevators]
                    max_score = max(elevator_scores)

        async def start_all_elevators():
            await asyncio.gather(*[elevator.step(self) for elevator in self.elevators])
        asyncio.run(start_all_elevators())
        print("Average wait time: {}".format(sum(self.wait_times) / len(self.wait_times) / self.time_scale))
        print("Average travel time: {}".format(sum(self.travel_times) / len(self.travel_times) / self.time_scale))
