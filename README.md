# elevatorpy

### Extensible, Realtime Simplified Simulation of Elevators in Python

This library was created for my group's 1D project in SUTD's 10.009 Digital World (introduction to python). More details about SUTD's unique learning pedagogy can be found [here](https://www.sutd.edu.sg/Education/Unique-Academic-Structure/Freshmore-Subjects/10-009-The-Digital-World).

* * *

This is an **asynchronous** library that allows you to simulate arbitary elevator systems with custom parameters and logic.

Three base classes are defined in the root namespace:

-   `elevator.Elevator`, that can be used on its own
-   `elevator.ElevatorSystem`, cannot be used on its own but instead used as a base class to create custom Elevator Systems with your own logic
-   `elevator.Passenger`, a class representing a passenger common to all Elevator Systems.

## Getting started

### Installation

**Requires Python 3.7+**

This package is not published on pypi or other software repositories. Do use this library, simply clone the repository or download the zip file, then extract the `elevator` folder.

This package uses the `transitions` python package to manage the Elevator FSM. Install with:
`pip install transitions`

### Usage of single elevators

#### Opening and closing doors:

```python
import asyncio
from elevator import Elevator
e = Elevator(name="My First Elevator")

async def test():
    await e.open_doors()
    await e.close_doors()
    

asyncio.run(test())
```

Output:

    My First Elevator doors opening
    My First Elevator doors closing

#### Loading passengers

```python
from elevator import Elevator
from elevator import Passenger

e = Elevator(name="My First Elevator")

passengers = [
    Passenger(destination=2),
    Passenger(destination=5)
]

async def test():
    await e.open_doors()
    await e.load_passengers(passengers)

asyncio.run(test())
```

Output:

    My First Elevator doors opening
    Elevator My First Elevator loaded 2 passengers at floor 1, currently has 2 passengers

Notes:

-   By default, the elevator doors are closed. Attempting to load passengers while the doors are closed will result in an error.

#### Picking up passengers and transporting them to different floors

```python
import asyncio
from elevator import Elevator
from elevator import Passenger

e = Elevator(name="My First Elevator")
passengers = [
    Passenger(destination=2),
    Passenger(destination=2),
    Passenger(destination=3)
]

async def test():
    await e.open_doors()
    await e.load_passengers(passengers)
    await e.goto_floor(2)
    await e.unload_passengers()

asyncio.run(test())
print(len(e.passengers))
```

Output

    My First Elevator doors opening
    Elevator My First Elevator loaded 3 passengers at floor 1, currently has 3 passengers
    My First Elevator doors closing
    My First Elevator going up towards floor 2
    My First Elevator arrived at floor 2
    My First Elevator doors opening
    Elevator My First Elevator alighted 2 passengers at floor 2, currently has 1 passengers
    1

Notes:

-   `load_passengers` takes in a list of `Passenger` objects. Elevators have both a pax and weight capacity (configurable). The function will automatically reject passengers when the elevator is full, and return a list of rejected passengers.
-   `unload_passengers` will automatically detect which passengers are able to alight (i.e. the elevator is at their destination), and remove them without further effort.
-   `open_doors`, `close_doors`, `goto_floor` will pass time, and their speeds can be configured on a per-elevator basis.

### Changing model parameters

There exists the following instance variables that can be used to customise the behaviour of each individual elevator:

-   `passenger_pax_capacity` represents the maximum number of passengers the elevator can take
-   `passenger_weight_capacity` represents the maximum weight capacity of the elevator. Each passenger has a default weight of 60 (specified by the `weight` kwarg).
-   `door_action_duration` represents the time it takes in seconds to open/close the doors
-   `floor_movement_duration` represents the time it takes in seconds for the elevator to travel one floor

### Changing simulation parameters

There are also the following instance variables that can change the behaviour of the simulation:

-   `time_scale` Speeds up (&lt;1) or slows down (>1) every artificial blocking calls.
-   `stream` Any IOStream object that is capable with `print`, in order to redirect messages from stdout.

## Extending the simulations

### Event listeners / Callbacks

This library was designed with extensibility in mind. You can pass references to your own functions that will be called when the elevator changes state, so you can make your own realtime visualisations of the elevator (e.g. creating a GUI). 

Event listeners are stored in a dictionary of lists. All callbacks attached here will be passed keyword arguments when be called. You should thus design your callbacks to accept `**kwargs`. You can add event listeners to the following events via these instance attributes:

-   `close_doors_callbacks["before"|"after"]` contains a list of functions that will be called before/after doors are closed. Passes the following arguments on invocation:
    -   `elevator` a reference to the elevator object itself
-   `open_doors_callbacks["before"|"after"]` contains a list of functions that will be called before/after doors are opened. Passes the following arguments on invocation:
    -   `elevator` a reference to the elevator object itself
-   `move_to_callbacks`
    -   `["start_moving"]` contains a list of functions that will be called when the elevator starts moving. Passes the following arguments on invocation:
        -   `elevator` a reference to the elevator object itself
        -   `dest` an int representing the destination floor as passed into `Elevator.move_to`
    -   `["enter_floor"]` contains a list of functions that will be called when the elevator enters a new (intermediate) floor. This will be called multiple times if there multiple floors between the elevator's original position and the destination floor. Passes the following arguments on invocation:
        -   `elevator` a reference to the elevator object itself
        -   `floor` the new floor the elevator is about to enter (i.e. `Elevator.floor` has not been updated)
    -   `["exit_floor"]` contains a list of functions that will be called when the elevator exits an intermediate floor. This will be called multiple times if there are multiple floors between the elevator's original position and destination floor. Passes the following arguments on invocation:
        -   `elevator` a reference to the elevator object itself
        -   `floor` the intermediate floor the elevator is about to exit (i.e. `Elevator.floor` has been updated)
    -   `["stop_moving"]` contains a list of functions that will be called when the elevator reaches its intended destination. Passes the following arguments on invocation:
        -   `elevator` a reference to the elevator object itself
        -   `dest` an int representing the destination floor as passed into `Elevator.move_to`
-   `loading_passengers_callbacks["before|after"]` contains a list of functions that will be called before/after the elevator loads passengers. Passes the following arguments on invocation:
    -   `elevator` a reference to the elevator object itself
    -   (before only) `boarding_passengers` a list of `Passenger` objects as passed into `Elevator.load_passengers`
    -   (after only) `boarded_passengers` a list of newly boarded passengers who managed to board
-   `unloading_passengers_callback["before"|"after"]` contains a list of functions that will be called before/after the elevator unloads (alights) passengers. Passes the following arguments on invocation:
    -   `elevator` a reference to the elevator object itself
    -   (after only) `alighted_passengers` a list of `Passenger` objects confirmed to alight

The amount of callbacks might seem overkill, but the reason for this is so that this library/module can be "hot plugged" into other projects who just want to monitor the changes in state of each elevator while running a simulation real-time in the background. For instance, if you were making a GUI visualisation of an elevator system, you can use the `open_doors` callback to start an animation in your frontend to show an elevator sprite opening its doors. **In fact, all the output you see in the examples above are actually the result of functions registered in the list of event listeners!** (You can thus disable them by deleting their references in the lists above.)

### Accessing the Elevator State

While it uses the concepts of finite state machines, the Elevator model is not strictly one as it has multiple state variables that persist outside the normal state transmutations. The elevator has the following "FSM" states, accessible by `Elevator.state`:

-   `closing_doors` when the elevator doors are closing. `asyncio.sleep` is called once in this state to simulate time taken for door actions.
-   `closed_doors` the state where doors have been closed. The elevator may idle in this state, or proceed to `moving`
-   `moving` represents an elevator in transit. `asyncio.sleep` is called repeatedly in this state to simulate travel time.
-   `opening_doors` when the elevator doors are opening. `asyncio.sleep` is called once to simulate time taken for door actions.

The list of `Passenger` objects currently in the elevator's carriage is stored in a list in the `passengers` instance variable.

The current floor the elevator is at can be retrieved with the `floor` instance variable. The immediate destination (used by `goto_floor`) is stored in the `next` instance variable.
