from transitions import Machine

import asyncio
import time


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
        self.door_action_duration = 0.5  # the time in seconds it takes for the doors to open and close
        self.floor_movement_duration = 0.15  # the time in seconds it takes for the elevator to travel one floor

        # initialise model parameters
        self.passenger_pax_capacity = 10
        self.passenger_weight_capacity = 800
        self.home_floor = home_floor

        # initialise state variables
        self.passengers = []
        self.floor = starting_floor
        self.next = None

        # add transitions
        self.machine.add_transition("close_doors", "doors_open", "doors_closing", before="on_close_doors", after="after_close_doors")
        self.machine.add_transition("start_moving_to", "doors_closed", "moving", before="on_start_moving_to")
        self.machine.add_transition("stop", "moving", "doors_closed", before="on_stop")
        self.machine.add_transition("open_doors", "doors_closed", "doors_opening", before="on_open_doors", after="after_open_doors")

    def goto_floor(self, floor):
        if self.state == "doors_open":
            self.close_doors()
        self.start_moving_to(floor)
        # pass time...
        self.stop()
        self.open_doors()

    def goto_home(self):
        self.goto_floor(self.home_floor)

    def load_passengers(self, passengers):
        if self.state != "doors_open":
            raise ValueError("You tried to load passengers into {} while it was in state {}!".format(self.name, self.state))
        passengers = passengers.copy()
        for passenger in passengers:
            if type(passenger) is not Passenger:
                raise ValueError("You tried to load something into {} that is not a passenger!".format(self.name))
            if passenger.destination == self.floor:
                raise ValueError("You tried to load a passenger into {} whose destination is the same floor ({})".format(self.name, passenger.destination))
        while True:
            if len(passengers) == 0:
                return []
            next_passenger = passengers.pop(0)
            pax_capacity_exceeded = len(self.passengers) >= self.passenger_pax_capacity
            weight_capacity_exceeded = sum([p.weight for p in self.passengers]) > self.passenger_weight_capacity - next_passenger.weight
            if pax_capacity_exceeded or weight_capacity_exceeded:
                passengers.insert(next_passenger, 0)
                return passengers
            else:
                self.passengers.append(next_passenger)
        raise Exception("Somehow, you managed to reach unreachable code")

    def unload_passengers(self):
        if self.state != "doors_open":
            raise ValueError("You tried to unload passengers from {} while it was in state {}!".format(self.name, self.state))
        alighting_passengers = list(filter(lambda p: p.destination == self.floor, self.passengers))
        self.passengers = list(filter(lambda p: p.destination != self.floor, self.passengers))
        return alighting_passengers

    def on_close_doors(self, event):
        print(Elevator.MESSAGE_TEMPLATES["doors_closing"].format(self.name))
        time.sleep(self.door_action_duration)

    def after_close_doors(self, event):
        self.to_doors_closed()

    def on_start_moving_to(self, event):
        self.next = event.args[0]
        direction = "up" if self.next > self.floor else "down"
        print(Elevator.MESSAGE_TEMPLATES["departure"].format(self.name, direction, self.next))
        time.sleep(self.floor_movement_duration * abs(self.next - self.floor))

    def on_stop(self, event):
        print(Elevator.MESSAGE_TEMPLATES["arrival"].format(self.name, self.next))
        self.floor = self.next

    def on_open_doors(self, event):
        print(Elevator.MESSAGE_TEMPLATES["doors_opening"].format(self.name))

    def after_open_doors(self, event):
        self.to_doors_open()

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

    def get_weight(self):
        return self._weight

    def set_weight(self, weight):
        if type(weight) is not int or weight < 0:
            raise ValueError("You tried to assign weight of passenger to a non-positive number: {}".format(weight))
        else:
            self._weight = weight

    weight = property(get_weight, set_weight)
