from .. import ElevatorSystem
from .. import Elevator
from .. import Passenger
import random
import asyncio
import time


class SimpleElevator(Elevator):
    def __init__(self, *, name="Main Elevator", starting_floor=1, home_floor=1, passenger_pax_capacity=10):
        super().__init__(name=name, starting_floor=starting_floor, home_floor=home_floor, passenger_pax_capacity=passenger_pax_capacity)
        self.intended_direction = "up" if random.randint(0, 1) == 1 else "down"
        # in this elevator type, we assume the starting floor __is__ the home floor
        self.starting_floor = home_floor
        self.floor = home_floor

    # override load_passengers
    async def load_passengers(self, passengers):
        if self.state != "doors_open":
            raise ValueError("You tried to load passengers into {} while it was in state {}!".format(self.name, self.state))
        # passengers = passengers.copy()
        for passenger in passengers:
            if type(passenger) is not Passenger:
                raise ValueError("You tried to load something into {} that is not a passenger!".format(self.name))
            if passenger.destination == self.floor:
                raise ValueError("You tried to load a passenger into {} whose destination is the same floor ({})".format(self.name, passenger.destination))
        passengers_added = 0
        boarding_passengers = []
        passengers_in_same_direction = []
        for passenger in passengers:
            passenger_direction = "up" if passenger.destination > self.floor else "down"
            if passenger_direction == self.intended_direction:
                passengers_in_same_direction.append(passenger)
        passengers_in_same_direction_copy = passengers_in_same_direction.copy()
        while True:
            if len(passengers_in_same_direction) == 0:
                break
            next_passenger = passengers_in_same_direction.pop(0)
            pax_capacity_exceeded = len(self.passengers) >= self.passenger_pax_capacity
            weight_capacity_exceeded = sum([p.weight for p in self.passengers]) > self.passenger_weight_capacity - next_passenger.weight
            if pax_capacity_exceeded or weight_capacity_exceeded:
                passengers_in_same_direction.insert(0, next_passenger)
                break
            else:
                passengers_added += 1
                self.passengers.append(next_passenger)
                boarding_passengers.append(next_passenger)
        for callback in self.loading_passengers_callbacks["after"]:
            callback(elevator=self, boarded_passengers=boarding_passengers)
        rejected = [passenger for passenger in passengers if passenger not in passengers_in_same_direction_copy]
        return rejected

    def is_en_route_to(self, passenger):
        if self.intended_direction == "up":
            return passenger.destination >= self.floor
        elif self.intended_direction == "down":
            return passenger.destination <= self.floor
        else:
            return None

    """extend goto_floor to automatically mark calls as served"""
    async def goto_floor(self, floor, *, system=None):
        system.floors[floor].served_by[self.intended_direction] = self.name
        await super().goto_floor(floor)

    async def step(self, system):
        # start - waiting at home floor
        # open doors
        # unload passengers
        # do i have any passengers i can pick up on this floor?
        #   # yes
        #       # find the closest destination in the direction i am moving
        #       # can i take more passengers?
        #           # yes
        #               # are there any passenger calls in the system waiting inbetween the current floor and the cloest destination travelling in the same direction?
        #                   # yes
        #                       # go to that floor and load/unload more pasengers
        #                       # END
        #                   # no
        #                       # go to closest destination floor
        #                       # END
        #           # no
        #               # go to closest destination floor
        #   # no
        #        # are there other unserved calls in the system?
        #           # yes
        #               # choose a random direction to serve calls

        # while system.count_total_passengers() > 0 or len(self.passengers) != 0:
        for passenger in self.passengers:
            for elevator in system.elevators:
                if elevator is not self:
                    assert passenger not in elevator.passengers
        if self.state == "doors_closed":
            await self.open_doors()
        await self.unload_passengers()
        if self.intended_direction != "up" and self.intended_direction != "down":
            raise ValueError("{} direction is set to {}".format(self.name, self.intended_direction))

        if len(system.floors.passengers[self.intended_direction]) != 0:
            unboarded_passengers = await self.load_passengers(system.floors.passengers[self.intended_direction])
            closest_destination = min([passenger.destination for passenger in self.passengers if self.is_en_route_to(passenger)])
            for intermediate_floor in range(self.floor + 1, closest_destination):
                if len(system.floors.passengers[self.intended_direction]) != 0:
                    closest_destination = intermediate_floor
                    break
            await self.goto_floor(closest_destination)
        else:
            pass

class SimpleFloor():
    def __init__(self):
        self.passengers = {
            "up": [],
            "down": []
        }
        self.served_by = {
            "up": [],
            "down": []
        }


class SimpleElevatorSystem(ElevatorSystem):
    def __init__(self, name, *, num_floors=5, num_lifts=3):
        super().__init__(name, num_floors=num_floors, num_lifts=num_lifts)
        for i in range(1, num_floors + 1):
            self.floors[i] = SimpleFloor()
        for i in range(num_lifts):
            new_elevator = SimpleElevator(name="SimpleElevator {}".format(i))
            new_elevator.time_scale = self.time_scale
            new_elevator.loading_passengers_callbacks["after"].append(self.record_passenger_wait_times)
            new_elevator.unloading_passengers_callbacks["after"].append(self.record_passenger_travel_times)
            self.elevators.append(new_elevator)
        self.calls = []

    def seed_floors(self, **kwargs):
        max_passengers_per_floor = kwargs.get("max_passengers_per_floor", 5)

        def generate_destination(source, max):
            destination = source
            while destination == source:
                destination = random.randint(1, max)
            return destination
        for floor_number in range(1, self.num_floors + 1):
            n_passengers = random.randint(0, max_passengers_per_floor)
            for i in range(n_passengers):
                self.floors[floor_number].passengers["up"].append(Passenger(destination=generate_destination(floor_number, self.num_floors)))
            n_passengers = random.randint(0, max_passengers_per_floor)
            for i in range(n_passengers):
                self.floors[floor_number].passengers["down"].append(Passenger(destination=generate_destination(floor_number, self.num_floors)))

    def run_until_system_empty(self):
        time_start = time.time()
        for floor in self.floors.values():
            for passenger in floor:
                passenger.start_time = time_start

        async def step(self):
            # get unserved calls
            up_unserved = [(k, floor) for (k, floor) in self.floor.items() if floor.served_by["up"] is None]
            
        async def start_all_elevators():
            # assign calls
            for floor_no, floor in self.floors.items():
                pass
            
            await asyncio.gather(*[elevator.step(self) for elevator in self.elevators])
        while self.count_total_passengers() > 0:
            asyncio.run(start_all_elevators())

        print("Average wait time: {}".format(sum(self.wait_times) / len(self.wait_times) / self.time_scale))
        print("Average travel time: {}".format(sum(self.travel_times) / len(self.travel_times) / self.time_scale))
