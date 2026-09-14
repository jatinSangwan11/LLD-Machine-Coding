from concurrent.futures import ThreadPoolExecutor
import datetime
import threading

import pytest

from parking import (
    HourlyPricing,
    InMemoryTicketStore,
    InvalidTicketError,
    NoCompatibleSpotError,
    ParkingFloor,
    ParkingLot,
    ParkingSpot,
    SmallestSuitableSpotAllocation,
    SpotType,
    Ticket,
    TicketAlreadyClosedError,
    TicketStatus,
    VehicleCategory,
    VehicleAlreadyParkedError,
)


def make_spot(spot_id: str, spot_type: SpotType) -> ParkingSpot:
    return ParkingSpot(
        spot_id=spot_id,
        spot_type=spot_type,
        is_available=True,
    )


def make_floor(floor_number: int, *spots: ParkingSpot) -> ParkingFloor:
    return ParkingFloor(
        floor_number=floor_number,
        spots=list(spots),
    )


class FixedPricing:
    def __init__(self, charge: float) -> None:
        self.charge = charge

    def calculate(
        self,
        entry_time: datetime.datetime,
        exit_time: datetime.datetime,
        vehicle_category: VehicleCategory,
    ) -> float:
        return self.charge


class FixedSpotAllocator:
    def __init__(self, spot: ParkingSpot, floor_number: int) -> None:
        self.spot = spot
        self.floor_number = floor_number

    def find_spot(
        self,
        floors: list[ParkingFloor],
        vehicle_category: VehicleCategory,
    ) -> tuple[ParkingSpot, int]:
        return self.spot, self.floor_number


def test_ticket_store_keeps_history_when_ticket_becomes_inactive() -> None:
    ticket_store = InMemoryTicketStore()
    ticket = Ticket(
        ticket_id=ticket_store.generate_ticket_id(),
        registration_number="DL-01-1234",
        vehicle_category=VehicleCategory.CAR,
        spot_id="C-1",
        floor_number=1,
        enter_time=datetime.datetime(2026, 9, 10, 10, 0),
    )
    ticket_store.save(ticket)

    assert ticket_store.get("T-1") is ticket
    assert ticket_store.has_active_ticket("DL-01-1234") is True

    ticket.status = TicketStatus.CLOSED
    ticket_store.save(ticket)

    assert ticket_store.get("T-1") is ticket
    assert ticket_store.has_active_ticket("DL-01-1234") is False


def test_smallest_suitable_allocator_orders_unordered_input() -> None:
    expected_spot = make_spot("C-1", SpotType.COMPACT)
    floors = [
        make_floor(2, make_spot("C-1", SpotType.COMPACT)),
        make_floor(
            1,
            make_spot("C-2", SpotType.COMPACT),
            expected_spot,
        ),
    ]
    allocator = SmallestSuitableSpotAllocation()

    selection = allocator.find_spot(floors, VehicleCategory.CAR)

    assert selection == (expected_spot, 1)


def test_park_uses_injected_spot_allocator() -> None:
    compact_spot = make_spot("C-1", SpotType.COMPACT)
    selected_large_spot = make_spot("L-1", SpotType.LARGE)
    allocator = FixedSpotAllocator(selected_large_spot, floor_number=1)
    parking_lot = ParkingLot(
        [make_floor(1, compact_spot, selected_large_spot)],
        spot_allocator=allocator,
    )

    ticket = parking_lot.park("DL-01-1234", VehicleCategory.CAR)

    assert ticket.spot_id == "L-1"
    assert compact_spot.is_available is True
    assert selected_large_spot.is_available is False


def test_parks_a_car_in_an_available_compact_spot() -> None:
    compact_spot = make_spot("C-1", SpotType.COMPACT)
    parking_lot = ParkingLot([make_floor(1, compact_spot)])

    ticket = parking_lot.park("DL-01-1234", VehicleCategory.CAR)

    assert isinstance(ticket, Ticket)
    assert ticket.ticket_id == "T-1"
    assert ticket.registration_number == "DL-01-1234"
    assert ticket.vehicle_category is VehicleCategory.CAR
    assert ticket.spot_id == "C-1"
    assert ticket.floor_number == 1
    assert compact_spot.is_available is False


def test_rejects_parking_when_no_compatible_spot_is_available() -> None:
    motorcycle_spot = make_spot("M-1", SpotType.MOTORCYCLE)
    parking_lot = ParkingLot([make_floor(1, motorcycle_spot)])

    with pytest.raises(
        NoCompatibleSpotError,
        match="No compatible spot is available for 'car'",
    ):
        parking_lot.park("HR-13V-3221", VehicleCategory.CAR)

    assert motorcycle_spot.is_available is True


def test_rejects_second_parking_attempt_for_same_registration() -> None:
    compact_spot = make_spot("C-1", SpotType.COMPACT)
    large_spot = make_spot("L-1", SpotType.LARGE)
    parking_lot = ParkingLot([make_floor(1, compact_spot, large_spot)])

    ticket_1 = parking_lot.park("HR-13V-3422", VehicleCategory.CAR)

    assert ticket_1 is not None
    assert ticket_1.ticket_id == "T-1"
    assert ticket_1.registration_number == "HR-13V-3422"
    assert ticket_1.vehicle_category is VehicleCategory.CAR
    assert ticket_1.spot_id == "C-1"
    assert ticket_1.floor_number == 1
    assert compact_spot.is_available is False

    with pytest.raises(
        VehicleAlreadyParkedError,
        match="Vehicle 'HR-13V-3422' is already parked",
    ):
        parking_lot.park("HR-13V-3422", VehicleCategory.CAR)

    assert large_spot.is_available is True


def test_parks_on_the_lowest_floor() -> None:
    floor_1 = make_floor(
        1,
        make_spot("C-1", SpotType.COMPACT),
        make_spot("L-1", SpotType.LARGE),
    )
    floor_2 = make_floor(2, make_spot("C-2", SpotType.COMPACT))
    parking_lot = ParkingLot([floor_1, floor_2])

    ticket = parking_lot.park("HR-13V-3422", VehicleCategory.CAR)

    assert ticket is not None
    assert ticket.ticket_id == "T-1"
    assert ticket.registration_number == "HR-13V-3422"
    assert ticket.vehicle_category is VehicleCategory.CAR
    assert ticket.spot_id == "C-1"
    assert ticket.floor_number == 1


def test_selects_lowest_floor_when_configuration_is_unordered() -> None:
    floor_2 = make_floor(2, make_spot("C-2", SpotType.COMPACT))
    floor_1 = make_floor(1, make_spot("C-1", SpotType.COMPACT))
    parking_lot = ParkingLot([floor_2, floor_1])

    ticket = parking_lot.park("DL-01-9999", VehicleCategory.CAR)

    assert ticket is not None
    assert ticket.floor_number == 1
    assert ticket.spot_id == "C-1"


def test_selects_lowest_spot_id() -> None:
    floor = make_floor(
        1,
        make_spot("C-2", SpotType.COMPACT),
        make_spot("C-1", SpotType.COMPACT),
    )
    parking_lot = ParkingLot([floor])

    ticket = parking_lot.park("DL-01-9999", VehicleCategory.CAR)

    assert ticket is not None
    assert ticket.floor_number == 1
    assert ticket.spot_id == "C-1"


def test_ticket_records_the_entry_time() -> None:
    parking_lot = ParkingLot(
        [make_floor(1, make_spot("C-1", SpotType.COMPACT))]
    )
    before_parking = datetime.datetime.now()

    ticket = parking_lot.park("DL-01-1234", VehicleCategory.CAR)

    after_parking = datetime.datetime.now()
    assert ticket is not None
    assert before_parking <= ticket.enter_time <= after_parking


def test_stores_ticket_so_it_can_be_found_during_exit() -> None:
    ticket_store = InMemoryTicketStore()
    parking_lot = ParkingLot(
        [make_floor(1, make_spot("C-1", SpotType.COMPACT))],
        ticket_store=ticket_store,
    )

    ticket = parking_lot.park("DL-01-1234", VehicleCategory.CAR)

    assert ticket is not None
    assert ticket_store.get(ticket.ticket_id) is ticket


def test_exit_happy_flow() -> None:
    parking_lot = ParkingLot(
        [make_floor(1, make_spot("C-1", SpotType.COMPACT))]
    )
    ticket = parking_lot.park("DL-01-1234", VehicleCategory.CAR)
    assert ticket is not None
    before_exit = datetime.datetime.now()

    closed_ticket = parking_lot.exit(ticket.ticket_id)

    after_exit = datetime.datetime.now()
    assert closed_ticket is ticket
    assert closed_ticket.status is TicketStatus.CLOSED
    assert closed_ticket.exit_time is not None
    assert before_exit <= closed_ticket.exit_time <= after_exit
    assert closed_ticket.final_charge == 40


def test_exit_uses_injected_pricing() -> None:
    parking_lot = ParkingLot(
        [make_floor(1, make_spot("C-1", SpotType.COMPACT))],
        pricing=FixedPricing(charge=125),
    )
    ticket = parking_lot.park("DL-01-1234", VehicleCategory.CAR)

    closed_ticket = parking_lot.exit(ticket.ticket_id)

    assert closed_ticket is ticket
    assert closed_ticket.final_charge == 125


def test_exit_releases_active_state_but_keeps_ticket_history() -> None:
    compact_spot = make_spot("C-1", SpotType.COMPACT)
    ticket_store = InMemoryTicketStore()
    parking_lot = ParkingLot(
        [make_floor(1, compact_spot)],
        ticket_store=ticket_store,
    )
    entry_ticket = parking_lot.park("DL-01-1234", VehicleCategory.CAR)
    assert entry_ticket is not None

    parking_lot.exit(entry_ticket.ticket_id)

    assert compact_spot.is_available is True
    assert ticket_store.has_active_ticket(entry_ticket.registration_number) is False
    assert ticket_store.get(entry_ticket.ticket_id) is entry_ticket


def test_rounds_partial_hour_upward() -> None:
    pricing = HourlyPricing()
    entry_time = datetime.datetime(2026, 9, 9, 10, 0)
    exit_time = datetime.datetime(2026, 9, 9, 11, 10)

    charges = pricing.calculate(
        entry_time,
        exit_time,
        VehicleCategory.CAR,
    )

    assert charges == 80


def test_charges_for_at_least_one_hour() -> None:
    pricing = HourlyPricing()
    entry_time = datetime.datetime(2026, 9, 9, 10, 0)
    exit_time = datetime.datetime(2026, 9, 9, 10, 10)

    charges = pricing.calculate(
        entry_time,
        exit_time,
        VehicleCategory.CAR,
    )

    assert charges == 40


def test_does_not_round_an_exact_hour_upward() -> None:
    pricing = HourlyPricing()
    entry_time = datetime.datetime(2026, 9, 9, 10, 0)
    exit_time = datetime.datetime(2026, 9, 9, 11, 0)

    charges = pricing.calculate(
        entry_time,
        exit_time,
        VehicleCategory.CAR,
    )

    assert charges == 40


def test_rejects_unknown_ticket_id() -> None:
    compact_spot = make_spot("C-1", SpotType.COMPACT)
    ticket_store = InMemoryTicketStore()
    parking_lot = ParkingLot(
        [make_floor(1, compact_spot)],
        ticket_store=ticket_store,
    )
    active_ticket = parking_lot.park("DL-01-1234", VehicleCategory.CAR)
    assert active_ticket is not None

    with pytest.raises(InvalidTicketError):
        parking_lot.exit("UNKNOWN-TICKET")

    assert compact_spot.is_available is False
    assert active_ticket.status is TicketStatus.ACTIVE
    assert ticket_store.has_active_ticket(active_ticket.registration_number) is True


def test_rejects_ticket_that_is_already_closed() -> None:
    parking_lot = ParkingLot(
        [make_floor(1, make_spot("C-1", SpotType.COMPACT))]
    )
    ticket = parking_lot.park("DL-01-1234", VehicleCategory.CAR)
    assert ticket is not None
    closed_ticket = parking_lot.exit(ticket.ticket_id)
    exit_time = closed_ticket.exit_time
    final_charge = closed_ticket.final_charge

    with pytest.raises(TicketAlreadyClosedError):
        parking_lot.exit(ticket.ticket_id)

    assert ticket.status is TicketStatus.CLOSED
    assert ticket.exit_time == exit_time
    assert ticket.final_charge == final_charge
    assert parking_lot.get_availability()["total"]["compact"] == 1


def test_reports_availability_after_parking_and_exit() -> None:
    floor_1 = make_floor(
        1,
        make_spot("C-1", SpotType.COMPACT),
        make_spot("L-1", SpotType.LARGE),
    )
    floor_2 = make_floor(
        2,
        make_spot("M-1", SpotType.MOTORCYCLE),
        make_spot("C-2", SpotType.COMPACT),
    )
    parking_lot = ParkingLot([floor_1, floor_2])

    ticket = parking_lot.park("DL-01-1234", VehicleCategory.CAR)
    assert ticket is not None

    assert parking_lot.get_availability() == {
        "floors": {
            1: {"motorcycle": 0, "compact": 0, "large": 1},
            2: {"motorcycle": 1, "compact": 1, "large": 0},
        },
        "total": {"motorcycle": 1, "compact": 1, "large": 1},
    }

    parking_lot.exit(ticket.ticket_id)

    assert parking_lot.get_availability() == {
        "floors": {
            1: {"motorcycle": 0, "compact": 1, "large": 1},
            2: {"motorcycle": 1, "compact": 1, "large": 0},
        },
        "total": {"motorcycle": 1, "compact": 2, "large": 1},
    }

def test_motorcycle_prefers_motorcycle_spot() -> None:
    parking_lot = ParkingLot(
        [
            make_floor(
                1,
                make_spot("C-1", SpotType.COMPACT),
                make_spot("M-1", SpotType.MOTORCYCLE),
            )
        ]
    )

    ticket = parking_lot.park(
        "DL-01-BIKE",
        VehicleCategory.MOTORCYCLE,
    )

    assert ticket is not None
    assert ticket.spot_id == "M-1"

def test_motorcycle_prefers_compact_spot_when_no_motorcycle_spot() -> None:
    parking_lot = ParkingLot(
        [
            make_floor(
                1,
                make_spot("C-1", SpotType.COMPACT)
            )
        ]
    )

    ticket = parking_lot.park(
        "DL-01-BIKE",
        VehicleCategory.MOTORCYCLE,
    )

    assert ticket is not None
    assert ticket.spot_id == "C-1"


def test_motorcycle_uses_large_spot_when_no_smaller_spot_is_available() -> None:
    large_spot = make_spot("L-1", SpotType.LARGE)
    parking_lot = ParkingLot([make_floor(1, large_spot)])

    ticket = parking_lot.park(
        "DL-01-BIKE",
        VehicleCategory.MOTORCYCLE,
    )

    assert ticket is not None
    assert ticket.spot_id == "L-1"
    assert large_spot.is_available is False


def test_car_uses_large_spot_when_no_compact_spot_is_available() -> None:
    large_spot = make_spot("L-1", SpotType.LARGE)
    parking_lot = ParkingLot([make_floor(1, large_spot)])

    ticket = parking_lot.park(
        "DL-01-CAR",
        VehicleCategory.CAR,
    )

    assert ticket is not None
    assert ticket.spot_id == "L-1"
    assert large_spot.is_available is False


def test_truck_uses_only_large_spot() -> None:
    compact_spot = make_spot("C-1", SpotType.COMPACT)
    large_spot = make_spot("L-1", SpotType.LARGE)
    parking_lot = ParkingLot(
        [make_floor(1, compact_spot, large_spot)]
    )

    ticket = parking_lot.park(
        "DL-01-TRUCK",
        VehicleCategory.TRUCK,
    )

    assert ticket is not None
    assert ticket.spot_id == "L-1"
    assert compact_spot.is_available is True
    assert large_spot.is_available is False


def test_truck_is_rejected_when_no_large_spot_is_available() -> None:
    motorcycle_spot = make_spot("M-1", SpotType.MOTORCYCLE)
    compact_spot = make_spot("C-1", SpotType.COMPACT)
    parking_lot = ParkingLot(
        [make_floor(1, motorcycle_spot, compact_spot)]
    )

    with pytest.raises(NoCompatibleSpotError):
        parking_lot.park(
            "DL-01-TRUCK",
            VehicleCategory.TRUCK,
        )

    assert motorcycle_spot.is_available is True
    assert compact_spot.is_available is True


@pytest.mark.parametrize(
    ("category", "expected_charge"),
    [
        (VehicleCategory.MOTORCYCLE, 20),
        (VehicleCategory.TRUCK, 60),
    ],
)
def test_uses_vehicle_specific_hourly_rate(
    category: VehicleCategory,
    expected_charge: int,
) -> None:
    pricing = HourlyPricing()
    entry_time = datetime.datetime(2026, 9, 9, 10, 0)
    exit_time = datetime.datetime(2026, 9, 9, 11, 0)

    charges = pricing.calculate(
        entry_time,
        exit_time,
        category,
    )

    assert charges == expected_charge


def test_prefers_smallest_compatible_spot_type_before_lowest_floor() -> None:
    floor_1 = make_floor(1, make_spot("L-1", SpotType.LARGE))
    floor_2 = make_floor(2, make_spot("C-1", SpotType.COMPACT))
    parking_lot = ParkingLot([floor_1, floor_2])

    ticket = parking_lot.park("DL-01-1234", VehicleCategory.CAR)

    assert ticket is not None
    assert ticket.floor_number == 2
    assert ticket.spot_id == "C-1"


def test_vehicle_can_park_again_after_its_previous_ticket_is_closed() -> None:
    compact_spot = make_spot("C-1", SpotType.COMPACT)
    parking_lot = ParkingLot([make_floor(1, compact_spot)])
    first_ticket = parking_lot.park("DL-01-1234", VehicleCategory.CAR)
    assert first_ticket is not None
    parking_lot.exit(first_ticket.ticket_id)

    second_ticket = parking_lot.park("DL-01-1234", VehicleCategory.CAR)

    assert second_ticket is not None
    assert second_ticket.ticket_id == "T-2"
    assert second_ticket.status is TicketStatus.ACTIVE
    assert compact_spot.is_available is False


def test_concurrent_vehicles_cannot_take_the_same_last_spot() -> None:
    compact_spot = make_spot("C-1", SpotType.COMPACT)
    parking_lot = ParkingLot([make_floor(1, compact_spot)])
    start_together = threading.Barrier(2)

    def attempt_to_park(registration_number: str):
        start_together.wait()
        try:
            return parking_lot.park(
                registration_number,
                VehicleCategory.CAR,
            )
        except NoCompatibleSpotError as error:
            return error

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(
            executor.map(
                attempt_to_park,
                ["DL-01-CAR-1", "DL-01-CAR-2"],
            )
        )

    tickets = [result for result in results if isinstance(result, Ticket)]
    errors = [
        result
        for result in results
        if isinstance(result, NoCompatibleSpotError)
    ]

    assert len(tickets) == 1
    assert len(errors) == 1
    assert compact_spot.is_available is False


def test_same_registration_cannot_park_concurrently() -> None:
    parking_lot = ParkingLot(
        [
            make_floor(
                1,
                make_spot("C-1", SpotType.COMPACT),
                make_spot("C-2", SpotType.COMPACT),
            )
        ]
    )
    start_together = threading.Barrier(2)

    def attempt_to_park():
        start_together.wait()
        try:
            return parking_lot.park(
                "DL-01-SAME-CAR",
                VehicleCategory.CAR,
            )
        except VehicleAlreadyParkedError as error:
            return error

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = [executor.submit(attempt_to_park) for _ in range(2)]
        outcomes = [future.result() for future in results]

    tickets = [outcome for outcome in outcomes if isinstance(outcome, Ticket)]
    errors = [
        outcome
        for outcome in outcomes
        if isinstance(outcome, VehicleAlreadyParkedError)
    ]

    assert len(tickets) == 1
    assert len(errors) == 1
    assert parking_lot.get_availability()["total"]["compact"] == 1


def test_concurrent_parking_generates_unique_ticket_ids() -> None:
    parking_lot = ParkingLot(
        [
            make_floor(
                1,
                make_spot("C-1", SpotType.COMPACT),
                make_spot("C-2", SpotType.COMPACT),
            )
        ]
    )
    start_together = threading.Barrier(2)

    def park_vehicle(registration_number: str) -> Ticket:
        start_together.wait()
        return parking_lot.park(registration_number, VehicleCategory.CAR)

    with ThreadPoolExecutor(max_workers=2) as executor:
        tickets = list(
            executor.map(
                park_vehicle,
                ["DL-01-CAR-1", "DL-01-CAR-2"],
            )
        )

    assert {ticket.ticket_id for ticket in tickets} == {"T-1", "T-2"}


def test_same_ticket_cannot_exit_concurrently() -> None:
    compact_spot = make_spot("C-1", SpotType.COMPACT)
    ticket_store = InMemoryTicketStore()
    parking_lot = ParkingLot(
        [make_floor(1, compact_spot)],
        ticket_store=ticket_store,
    )
    ticket = parking_lot.park("DL-01-1234", VehicleCategory.CAR)
    start_together = threading.Barrier(2)

    def attempt_to_exit():
        start_together.wait()
        try:
            return parking_lot.exit(ticket.ticket_id)
        except TicketAlreadyClosedError as error:
            return error

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = [executor.submit(attempt_to_exit) for _ in range(2)]
        outcomes = [future.result() for future in results]

    closed_tickets = [
        outcome for outcome in outcomes if isinstance(outcome, Ticket)
    ]
    errors = [
        outcome
        for outcome in outcomes
        if isinstance(outcome, TicketAlreadyClosedError)
    ]

    assert len(closed_tickets) == 1
    assert len(errors) == 1
    assert ticket.status is TicketStatus.CLOSED
    assert compact_spot.is_available is True
    assert ticket_store.has_active_ticket(ticket.registration_number) is False
