from concurrent.futures import ThreadPoolExecutor

import pytest

from interview_elevator import ElevatorSystem, RequestStatus


def test_complete_ride_moves_one_floor_per_tick():
    system = ElevatorSystem(10, 1)
    ride = system.request(2, 5)
    assert system.snapshot()[1]["floor"] == 0  # Submission never moves it.
    system.step()
    assert system.snapshot()[1]["floor"] == 1
    assert system.check(ride).status is RequestStatus.WAITING
    system.step()
    assert system.check(ride).status is RequestStatus.BOARDED
    for floor in (3, 4, 5):
        system.step()
        assert system.snapshot()[1]["floor"] == floor
    assert system.check(ride).status is RequestStatus.REACHED
    system.step()
    assert system.snapshot()[1] == {"floor": 5, "direction": 0, "pending_rides": 0}


def test_fifo_rides_do_not_drop_off_before_pickup():
    system = ElevatorSystem(10, 1)
    first = system.request(0, 5)
    second = system.request(7, 3)
    for _ in range(6):
        system.step()
    assert system.check(first).status is RequestStatus.REACHED
    assert system.check(second).status is RequestStatus.WAITING
    system.step()
    system.step()  # Move 5 -> 6 -> 7, then board.
    assert system.check(second).status is RequestStatus.BOARDED
    for _ in range(4):
        system.step()
    assert system.check(second).status is RequestStatus.REACHED
    assert system.snapshot()[1]["floor"] == 3


def test_assignment_prefers_idle_then_distance_and_id():
    system = ElevatorSystem(10, 2)
    system.request(0, 4)  # Initial tie goes to elevator 1.
    system.step()
    system.request(2, 3)  # Elevator 2 is idle; elevator 1 has an active ride.
    assert system.snapshot()[1]["pending_rides"] == 1
    assert system.snapshot()[2]["pending_rides"] == 1
    for _ in range(4):
        system.step()
    assert system.snapshot()[1]["floor"] == 4
    assert system.snapshot()[2]["floor"] == 3
    system.request(2, 0)  # Both idle: elevator 2 is nearer.
    assert system.snapshot()[2]["pending_rides"] == 1


def test_assignment_prefers_compatible_direction_when_both_busy():
    system = ElevatorSystem(10, 2)
    system.request(0, 9)
    system.step()
    system.request(6, 0)
    for _ in range(6):
        system.step()
    # Both are at 6: E1 heads UP to 9, E2 heads DOWN to 0.
    system.request(5, 2)
    assert system.snapshot()[1]["pending_rides"] == 1
    assert system.snapshot()[2]["pending_rides"] == 2


def test_invalid_requests_and_detached_status_records():
    with pytest.raises(ValueError):
        ElevatorSystem(1, 1)
    with pytest.raises(ValueError):
        ElevatorSystem(10, 0)
    system = ElevatorSystem(10, 1)
    for source, destination in ((-1, 3), (2, 10), (3, 3)):
        with pytest.raises(ValueError):
            system.request(source, destination)
    with pytest.raises(KeyError):
        system.check(99)
    ride = system.request(0, 2)
    result = system.check(ride)
    result.status = RequestStatus.REACHED
    assert system.check(ride).status is RequestStatus.WAITING


def test_concurrent_submissions_have_unique_ids_and_all_finish():
    system = ElevatorSystem(10, 3)
    with ThreadPoolExecutor(max_workers=4) as pool:
        rides = list(pool.map(lambda _: system.request(0, 3), range(12)))
    assert len(set(rides)) == 12
    assert sum(e["pending_rides"] for e in system.snapshot().values()) == 12
    for _ in range(100):
        system.step()
    assert all(system.check(ride).status is RequestStatus.REACHED for ride in rides)
