from transitions import Machine


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

    def __init__(self, *, name="Main Elevator", starting_floor=1, home_floor=1):

        self.name = name

        # initialise the state machine with its states
        self.machine = Machine(model=self, states=Elevator.STATES, initial="doors_closed", send_event=True)

        # initialise state variables
        self.passengers = 0
        self.home_floor = home_floor
        self.floor = starting_floor
        self.next = None

        # add transitions
        self.machine.add_transition("close_doors", "doors_open", "doors_closing", before="on_close_doors", after="after_close_doors")
        self.machine.add_transition("start_moving_to", "doors_closed", "moving", before="on_start_moving_to")
        self.machine.add_transition("stop", "moving", "doors_closed", before="on_stop")
        self.machine.add_transition("open_doors", "doors_closed", "doors_opening", before="on_open_doors", after="after_open_doors")
        self.machine.add_transition("load_passengers", "idle", "")

    def goto_floor(self, floor):
        if self.state == "doors_open":
            self.close_doors()
        self.start_moving_to(floor)
        # pass time...
        self.stop()
        self.open_doors()

    def goto_home(self):
        self.goto_floor(self.home_floor)

    def on_close_doors(self, event):
        print(Elevator.MESSAGE_TEMPLATES["doors_closing"].format(self.name))

    def after_close_doors(self, event):
        self.to_doors_closed()

    def on_start_moving_to(self, event):
        self.next = event.args[0]
        direction = "up" if self.next > self.floor else "down"
        print(Elevator.MESSAGE_TEMPLATES["departure"].format(self.name, direction, self.next))

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

    floor = property(get_floor, set_floor)
    home_floor = property(get_home_floor, set_home_floor)
    next = property(get_next, set_next)


class Passenger():

    def __init__(self, *, destination):
        self.destination = destination
