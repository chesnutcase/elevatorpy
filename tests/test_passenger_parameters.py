from elevator import Passenger


def test_passenger_weight_cannot_be_negative():
    try:
        Passenger(destination=2, weight=-9001)
        assert False, "No exception was thrown"
    except ValueError as ex:
        assert str(ex) == "You tried to assign weight of passenger to a non-positive number: {}".format(-9001)
