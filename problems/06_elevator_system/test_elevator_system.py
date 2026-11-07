from concurrent.futures import ThreadPoolExecutor

import pytest

from elevator_system import Direction, Elevator, ElevatorStatus, Passenger, PassengerStatus


def advance_until(elevator, predicate, limit=40):
    for _ in range(limit):
        if predicate(elevator.snapshot()):
            return
        elevator.step()
    raise AssertionError(f"Condition not reached: {elevator.snapshot()}")


def test_complete_ride_and_separate_door_service_ticks():
    car = Elevator("E1", 500)
    passenger = Passenger("P1", 70)
    car.assign_pickup(passenger, 2, Direction.UP)
    assert car.snapshot().current_floor == 0  # Requests do not move the car.
    car.step()
    assert car.snapshot().current_floor == 1
    car.step()
    assert car.snapshot().current_floor == 2 and car.snapshot().doors_open
    assert passenger.status is PassengerStatus.WAITING
    assert car.step().boarded == ("P1",)
    assert car.snapshot().current_load_kg == 70 and not car.snapshot().doors_open
    car.step()  # Wait for destination input without departing.
    assert car.snapshot().current_floor == 2
    car.select_destination("P1", 5)
    for floor in (3, 4, 5):
        car.step()
        assert car.snapshot().current_floor == floor
    assert passenger.status is PassengerStatus.BOARDED
    assert car.step().reached == ("P1",)
    assert passenger.status is PassengerStatus.REACHED
    state = car.snapshot()
    assert state.current_load_kg == 0 and not state.onboard
    assert state.status is ElevatorStatus.IDLE and state.direction is Direction.IDLE
    car.step()
    assert car.snapshot().current_floor == 5  # No trip to the top floor.


def test_downward_approach_can_collect_upward_passenger():
    car = Elevator("E1", 500)
    first = Passenger("P1", 60)
    car.assign_pickup(first, 0, Direction.UP)
    car.step()  # Open at the current floor without moving.
    car.step()
    car.select_destination("P1", 7)
    advance_until(car, lambda s: s.current_floor == 7 and s.doors_open)
    car.step()
    second = Passenger("P2", 70)
    car.assign_pickup(second, 3, Direction.UP)
    advance_until(car, lambda s: s.current_floor == 3 and s.doors_open)
    assert car.snapshot().direction is Direction.UP
    assert car.step().boarded == ("P2",)
    car.select_destination("P2", 6)
    advance_until(car, lambda s: s.current_floor == 6 and s.doors_open)
    assert car.step().reached == ("P2",)


def test_shared_stops_and_opposite_pickup_wait_for_reversal():
    car = Elevator("E1", 500)
    for passenger_id in ("P1", "P2"):
        car.assign_pickup(Passenger(passenger_id, 70), 0, Direction.UP)
    car.step()
    assert car.step().boarded == ("P1", "P2")
    car.select_destination("P1", 7)
    car.select_destination("P2", 7)
    assert car.snapshot().up_stops == (7,)
    later = Passenger("P3", 80)
    car.assign_pickup(later, 6, Direction.DOWN)
    advance_until(car, lambda s: s.current_floor == 6)
    assert not car.snapshot().doors_open  # Keep travelling UP to 7.
    car.step()
    assert car.step().reached == ("P1", "P2")
    car.step()  # Reverse and move 7 -> 6.
    assert car.snapshot().current_floor == 6 and car.snapshot().doors_open
    assert car.step().boarded == ("P3",)
    car.select_destination("P3", 1)
    advance_until(car, lambda s: s.current_floor == 1 and s.doors_open)
    assert car.step().reached == ("P3",)


def test_capacity_refusal_remains_waiting_and_dropoff_precedes_boarding():
    car = Elevator("E1", 100)
    first, second = Passenger("P1", 70), Passenger("P2", 50)
    car.assign_pickup(first, 0, Direction.UP)
    car.assign_pickup(second, 0, Direction.UP)
    car.step()
    event = car.step()
    assert event.boarded == ("P1",) and event.waiting == ("P2",)
    assert second.status is PassengerStatus.WAITING
    assert car.snapshot().current_load_kg == 70
    assert "P2" not in car.snapshot().assigned_pickups  # Caller must reassign it.
    car.select_destination("P1", 3)
    third = Passenger("P3", 100)
    car.assign_pickup(third, 3, Direction.UP)
    advance_until(car, lambda s: s.current_floor == 3 and s.doors_open)
    event = car.step()
    assert event.reached == ("P1",) and event.boarded == ("P3",)
    assert car.snapshot().current_load_kg == 100


def test_fractional_weights_and_request_validation():
    car = Elevator("E1", 0.3)
    p1, p2 = Passenger("P1", 0.1), Passenger("P2", 0.2)
    car.assign_pickup(p1, 0, Direction.UP)
    with pytest.raises(ValueError):
        car.assign_pickup(p1, 0, Direction.UP)
    with pytest.raises(ValueError):
        car.select_destination("P1", 2)  # Not boarded yet.
    for passenger, floor, direction in [
        (Passenger("BAD", -1), 0, Direction.UP),
        (Passenger("BAD", 1), 0, Direction.UP),  # Too heavy.
        (p2, 10, Direction.DOWN),
        (p2, 0, Direction.DOWN),
        (p2, 9, Direction.UP),
        (p2, 0, Direction.IDLE),
    ]:
        with pytest.raises(ValueError):
            car.assign_pickup(passenger, floor, direction)
    car.assign_pickup(p2, 0, Direction.UP)
    car.step()
    assert car.step().boarded == ("P1", "P2")
    assert car.snapshot().current_load_kg == 0.3
    with pytest.raises(ValueError):
        car.select_destination("P1", 0)
    car.select_destination("P1", 1)
    with pytest.raises(ValueError):
        car.select_destination("P1", 2)
    old_snapshot = car.snapshot()
    car.select_destination("P2", 2)
    assert old_snapshot.destinations == (("P1", 1),)


def test_concurrent_duplicate_assignment_is_rejected():
    car = Elevator("E1", 500)
    passenger = Passenger("P1", 70)

    def assign(_):
        try:
            car.assign_pickup(passenger, 2, Direction.UP)
            return True
        except ValueError:
            return False

    with ThreadPoolExecutor(max_workers=4) as pool:
        assert sum(pool.map(assign, range(8))) == 1
    assert car.snapshot().assigned_pickups == ("P1",)
