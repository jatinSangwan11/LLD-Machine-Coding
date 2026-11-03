from concurrent.futures import ThreadPoolExecutor
from datetime import UTC
from threading import Barrier
from time import sleep

import pytest

from parking_lot import ParkingFloor, ParkingLot, ParkingSpot, TicketStatus, VehicleType


def make_lot():
    # Deliberately unsorted, with repeated spot IDs on different levels.
    return ParkingLot([
        ParkingFloor(2, [ParkingSpot(1, VehicleType.CAR)]),
        ParkingFloor(1, [
            ParkingSpot(5, VehicleType.CAR),
            ParkingSpot(2, VehicleType.CAR),
            ParkingSpot(1, VehicleType.BIKE),
            ParkingSpot(9, VehicleType.TRUCK),
        ]),
        ParkingFloor(3, []),
    ])


def test_allocation_order_compatibility_and_ticket_lifecycle():
    lot = make_lot()
    cars = [lot.enter(f"CAR-{i}", VehicleType.CAR) for i in range(3)]
    assert [(t.level, t.spot_id) for t in cars] == [(1, 2), (1, 5), (2, 1)]
    assert len({t.id for t in cars}) == 3
    assert all(t.status is TicketStatus.ACTIVE and t.issued_at.tzinfo is UTC for t in cars)
    assert lot.enter("BIKE", VehicleType.BIKE).spot_id == 1
    assert lot.enter("TRUCK", VehicleType.TRUCK).spot_id == 9

    first = cars[0]
    assert lot.exit(first.id) is True
    assert first.status is TicketStatus.CLOSED
    assert first.vehicle_number not in lot.vehicle_no_to_ticket_id
    replacement = lot.enter(first.vehicle_number, VehicleType.CAR)
    assert replacement.id != first.id
    assert (replacement.level, replacement.spot_id) == (1, 2)


def test_failed_operations_leave_state_unchanged():
    lot = make_lot()
    ticket = lot.enter("A", VehicleType.CAR)
    before = lot.availability()
    with pytest.raises(ValueError, match="already parked"):
        lot.enter("A", VehicleType.CAR)
    with pytest.raises(ValueError, match="Unknown ticket"):
        lot.exit(-1)
    assert lot.availability() == before
    assert len(lot.ticket_id_to_ticket) == 1

    lot.exit(ticket.id)
    released = lot.availability()
    with pytest.raises(ValueError, match="already closed"):
        lot.exit(ticket.id)
    assert lot.availability() == released

    # Exhaust one type while other compatible types remain free.
    for i in range(3):
        lot.enter(f"CAR-{i}", VehicleType.CAR)
    before = lot.availability()
    ticket_count = len(lot.ticket_id_to_ticket)
    with pytest.raises(RuntimeError, match="No compatible"):
        lot.enter("EXTRA", VehicleType.CAR)
    assert lot.availability() == before
    assert len(lot.ticket_id_to_ticket) == ticket_count
    assert "EXTRA" not in lot.vehicle_no_to_ticket_id


def test_availability_counts_filters_and_snapshot_independence():
    lot = make_lot()
    before = lot.availability()
    assert before == {
        1: {VehicleType.CAR: 2, VehicleType.BIKE: 1, VehicleType.TRUCK: 1},
        2: {VehicleType.CAR: 1, VehicleType.BIKE: 0, VehicleType.TRUCK: 0},
        3: {VehicleType.CAR: 0, VehicleType.BIKE: 0, VehicleType.TRUCK: 0},
    }
    assert lot.availability(VehicleType.CAR) == {
        1: {VehicleType.CAR: 2}, 2: {VehicleType.CAR: 1}, 3: {VehicleType.CAR: 0},
    }
    ticket = lot.enter("A", VehicleType.CAR)
    assert lot.availability()[1][VehicleType.CAR] == 1
    assert before[1][VehicleType.CAR] == 2  # Earlier snapshot does not change.
    lot.exit(ticket.id)
    assert lot.availability() == before
    before[1][VehicleType.CAR] = 999
    assert lot.availability()[1][VehicleType.CAR] == 2


def test_empty_lot_and_invalid_vehicle_types():
    lot = ParkingLot([])
    assert lot.availability() == {}
    with pytest.raises(RuntimeError, match="No compatible"):
        lot.enter("A", VehicleType.CAR)
    with pytest.raises(TypeError):
        lot.enter("A", "car")
    with pytest.raises(TypeError):
        lot.availability("car")
    assert not lot.ticket_id_to_ticket and not lot.vehicle_no_to_ticket_id


@pytest.mark.parametrize("config", [
    [ParkingFloor(1, []), ParkingFloor(1, [])],
    [ParkingFloor(1, [ParkingSpot(1, VehicleType.CAR), ParkingSpot(1, VehicleType.BIKE)])],
])
def test_duplicate_configuration_is_rejected(config):
    with pytest.raises(ValueError, match="Duplicate"):
        ParkingLot(config)


@pytest.mark.parametrize("same_vehicle", [True, False])
def test_concurrent_entries_cannot_duplicate_vehicle_or_spot(same_vehicle):
    # Multiple spots isolate duplicate-vehicle checks; one spot tests contention.
    capacity = 3 if same_vehicle else 1
    lot = ParkingLot([ParkingFloor(1, [
        ParkingSpot(i, VehicleType.CAR) for i in range(capacity)
    ])])
    workers = 4
    start = Barrier(workers)

    def enter(worker_id):
        start.wait(timeout=5)
        vehicle = "SAME" if same_vehicle else f"CAR-{worker_id}"
        try:
            return lot.enter(vehicle, VehicleType.CAR)
        except ValueError:
            assert same_vehicle
        except RuntimeError:
            assert not same_vehicle
        return None

    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(enter, range(workers)))
    assert sum(ticket is not None for ticket in results) == 1
    assert len(lot.vehicle_no_to_ticket_id) == len(lot.ticket_id_to_ticket) == 1
    assert lot.availability(VehicleType.CAR)[1][VehicleType.CAR] == capacity - 1


def test_concurrent_entry_exit_and_availability_keep_state_consistent():
    lot = make_lot()
    before = lot.availability()
    start = Barrier(4)

    def writer(worker_id):
        start.wait(timeout=5)
        for step in range(100):
            ticket = lot.enter(f"CAR-{worker_id}", VehicleType.CAR)
            if step % 10 == 0:
                sleep(0)
            assert lot.exit(ticket.id) is True

    def reader():
        start.wait(timeout=5)
        for _ in range(300):
            snapshot = lot.availability()
            assert 0 <= snapshot[1][VehicleType.CAR] <= 2
            assert 0 <= snapshot[2][VehicleType.CAR] <= 1
            assert snapshot[1][VehicleType.BIKE] == 1
            assert snapshot[1][VehicleType.TRUCK] == 1
            assert all(count == 0 for count in snapshot[3].values())

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(writer, i) for i in range(3)]
        futures.append(executor.submit(reader))
        for future in futures:
            future.result()  # Propagate worker failures to pytest.

    assert lot.availability() == before
    assert not lot.vehicle_no_to_ticket_id
    assert all(t.status is TicketStatus.CLOSED for t in lot.ticket_id_to_ticket.values())
    free_keys = [key for heap in lot.free_spots_by_type.values() for key in heap]
    assert len(free_keys) == len(set(free_keys)) == len(lot.spot_lookup)
    assert set(free_keys) == set(lot.spot_lookup)
    assert all(spot.is_available for spot in lot.spot_lookup.values())
