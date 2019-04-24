from transitions import Machine

import asyncio
import time
import random


class Elevator():

    STATES = ["doors_closed",
              "doors_closing",
              "moving",
              "doors_opening",
              "doors_open"]

    MESSAGE_TEMPLATES = {
        "doors_closing": "{} doors closing",
        "doors_opening": "{} doors opening",
        "departure": "{} going {} towards floor {}",
        "arrival": "{} arrived at floor {}"
    }

    def __init__(self, *, name="Main Elevator", starting_floor=1, home_floor=1, passenger_pax_capacity=10):

        self.name = name

        # initialise the state machine with its states
        self.machine = Machine(model=self, states=Elevator.STATES, initial="doors_closed", send_event=True)

        # initialise simulation parameters
        self.door_action_duration = 1  # the time in seconds it takes for the doors to open and close
        self.floor_movement_duration = 1  # the time in seconds it takes for the elevator to travel one floor
        self.time_scale = 1  # for speeding up / slowing down the simulation

        # initialise simulation callbacks
        self.close_doors_callbacks = {
            "before": [self.print_doors_closing_message],
            "after": []
        }
        self.open_doors_callbacks = {
            "before": [self.print_doors_opening_message],
            "after": []
        }
        self.move_to_callbacks = {
            "start_moving": [self.print_departure_message],
            "enter_floor": [],
            "exit_floor": [],
            "stop_moving": [self.print_arrival_message]
        }
        self.loading_passengers_callbacks = {
            "before": [],
            "after": [self.print_loading_message]
        }
        self.unloading_passengers_callbacks = {
            "before": [],
            "after": [self.print_unloading_message]
        }
        # initialise model parameters
        self.passenger_pax_capacity = 10
        self.passenger_weight_capacity = 800
        self.home_floor = home_floor

        # initialise state variables
        self.passengers = []
        self.floor = starting_floor
        self.next = None

        # add transitions
        self.machine.add_transition("_close_doors", "doors_open", "doors_closing")
        self.machine.add_transition("_start_moving", "doors_closed", "moving")
        self.machine.add_transition("_stop_moving", "moving", "doors_closed")
        self.machine.add_transition("_open_doors", "doors_closed", "doors_opening")

    async def goto_floor(self, floor):
        if self.state == "doors_open":
            await self.close_doors()
        await self.move_to(floor)
        # pass time...
        await self.open_doors()

    async def close_doors(self):
        for callback in self.close_doors_callbacks["before"]:
            callback(None)
        self._close_doors()
        await asyncio.sleep(self.door_action_duration * self.time_scale)
        self.to_doors_closed()
        for callback in self.close_doors_callbacks["after"]:
            callback(None)

    async def open_doors(self):
        for callback in self.open_doors_callbacks["before"]:
            callback(None)
        self._open_doors()
        await asyncio.sleep(self.door_action_duration * self.time_scale)
        self.to_doors_open()
        for callback in self.close_doors_callbacks["after"]:
            callback(None)

    def print_doors_closing_message(self, event):
        print(Elevator.MESSAGE_TEMPLATES["doors_closing"].format(self.name))

    def print_doors_opening_message(self, event):
        print(Elevator.MESSAGE_TEMPLATES["doors_opening"].format(self.name))

    async def move_to(self, floor):
        starting_floor = self.floor
        self.next = floor
        dir = -1 if starting_floor > floor else 1
        floor_range = range(starting_floor + dir, floor + dir, dir)
        self._start_moving()
        # handle custom event callbacks
        for callback in self.move_to_callbacks["start_moving"]:
            callback()
        for i in floor_range:
            # handle custom event callbacks
            for callback in self.move_to_callbacks["exit_floor"]:
                callback()
            await asyncio.sleep(self.floor_movement_duration * self.time_scale)
            self.floor = i
            for callback in self.move_to_callbacks["enter_floor"]:
                callback()
            # handle custom event callbacks
        self._stop_moving()
        # handle custom event callbacks
        for callback in self.move_to_callbacks["stop_moving"]:
            callback()

    async def goto_home(self):
        await self.goto_floor(self.home_floor)

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
        while True:
            if len(passengers) == 0:
                break
            next_passenger = passengers.pop(0)
            pax_capacity_exceeded = len(self.passengers) >= self.passenger_pax_capacity
            weight_capacity_exceeded = sum([p.weight for p in self.passengers]) > self.passenger_weight_capacity - next_passenger.weight
            if pax_capacity_exceeded or weight_capacity_exceeded:
                passengers.insert(0, next_passenger)
                break
            else:
                passengers_added += 1
                self.passengers.append(next_passenger)
                boarding_passengers.append(next_passenger)
        for callback in self.loading_passengers_callbacks["after"]:
            callback(elevator=self, boarded_passengers=boarding_passengers)
        return passengers

    async def unload_passengers(self):
        if self.state != "doors_open":
            raise ValueError("You tried to unload passengers from {} while it was in state {}!".format(self.name, self.state))
        for callback in self.unloading_passengers_callbacks["before"]:
            callback(elevator=self)
        alighting_passengers = list(filter(lambda p: p.destination == self.floor, self.passengers))
        self.passengers = list(filter(lambda p: p.destination != self.floor, self.passengers))
        for callback in self.unloading_passengers_callbacks["after"]:
            callback(elevator=self, alighted_passengers=alighting_passengers)

        return alighting_passengers

    def print_departure_message(self):
        direction = "up" if self.next > self.floor else "down"
        print(Elevator.MESSAGE_TEMPLATES["departure"].format(self.name, direction, self.next))

    def print_arrival_message(self):
        print(Elevator.MESSAGE_TEMPLATES["arrival"].format(self.name, self.next))
        self.floor = self.next

    def print_loading_message(self, **kwargs):
        elevator = kwargs["elevator"]
        boarded_passengers = kwargs["boarded_passengers"]
        print("Elevator {} loaded {} passengers at floor {}, currently has {} passengers".format(elevator.name, len(boarded_passengers), elevator.floor, len(elevator.passengers)))

    def print_unloading_message(self, **kwargs):
        elevator = kwargs["elevator"]
        alighted_passengers = kwargs["alighted_passengers"]
        print("Elevator {} alighted {} passengers at floor {}, currently has {} passengers".format(elevator.name, len(alighted_passengers), elevator.floor, len(elevator.passengers)))

    def set_floor(self, floor):
        if type(floor) is not int:
            raise ValueError("You tried to set floor of {} to a non-numerical floor {}".format(self.name, floor))
        else:
            self._floor = floor

    def get_floor(self):
        return self._floor

    def set_home_floor(self, floor):
        if type(floor) is not int:
            raise ValueError("You tried to set home floor of {} to a non-numerical floor {}".format(self.name, floor))
        else:
            self._home_floor = floor

    def get_home_floor(self):
        return self._home_floor

    def set_next(self, floor):
        if self.state == "moving":
            raise Exception("You tried to change the destination of {} while it was already moving".format(self.name))
        if type(floor) is not int and floor is not None:
            raise ValueError("You tried to set next floor of {} to a non-numerical floor {}".format(self.name, floor))
        else:
            self._next = floor

    def get_next(self):
        return self._next

    def get_door_status(self):
        if self.state == "doors_closed" or self.state == "moving":
            return "closed"
        elif self.state == "doors_closing":
            return "closing"
        elif self.state == "doors_opening":
            return "opening"
        elif self.state == "doors_open":
            return "open"

    floor = property(get_floor, set_floor)
    home_floor = property(get_home_floor, set_home_floor)
    next = property(get_next, set_next)
    door_status = property(get_door_status)


class Passenger():

    def __init__(self, *, destination=1, weight=60):
        self.destination = destination
        self.weight = weight
        self.start_time = time.time()
        self.board_time = time.time()

    def get_relative_direction(self, floor):
        if self.destination > floor:
            return "up"
        elif self.destination < floor:
            return "down"
        else:
            raise ValueError("Passenger floor same as destination")

    def get_weight(self):
        return self._weight

    def set_weight(self, weight):
        if type(weight) is not int or weight < 0:
            raise ValueError("You tried to assign weight of passenger to a non-positive number: {}".format(weight))
        else:
            self._weight = weight

    weight = property(get_weight, set_weight)


class ElevatorSystem():
    def __init__(self, name, *, num_floors=5, num_lifts=3):
        self.name = name
        self.elevators = []
        self.floors = {}

        self.num_floors = num_floors
        self.wait_times = []
        self.travel_times = []
        self.time_scale = 0.2

    def count_total_passengers(self):
        return sum([len(v) for k, v in self.floors.items()])

    def add_passengers_at_floor(self, passengers, floor):
        if self.floors.get(floor) is None:
            self.floors[floor] = []
        self.floors[floor].append(passengers)

    def seed_floors(self, **kwargs):
        max_passengers_per_floor = kwargs.get("max_passengers_per_floor", 5)

        def generate_destination(source, max):
            destination = source
            while destination == source:
                destination = random.randint(1, max)
            return destination
        for floor_number in range(1, self.num_floors + 1):
            n_passengers = random.randint(0, max_passengers_per_floor)
            self.floors[floor_number] = []
            for i in range(n_passengers):
                self.floors[floor_number].append(Passenger(destination=generate_destination(floor_number, self.num_floors)))

    def record_passenger_wait_times(self, **kwargs):
        boarded_passengers = kwargs["boarded_passengers"]
        time_now = time.time()
        for passenger in boarded_passengers:
            self.wait_times.append(time_now - passenger.start_time)

    def record_passenger_travel_times(self, **kwargs):
        alighted_passengers = kwargs["alighted_passengers"]
        time_now = time.time()
        for passenger in alighted_passengers:
            self.travel_times.append(time_now - passenger.start_time)

    # extend this method yourself

    def run_until_system_empty(self):
        raise Exception("You should not call the base implementation of this function!")
