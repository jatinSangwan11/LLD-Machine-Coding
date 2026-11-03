import heapq
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from threading import Lock


class VehicleType(Enum):
    CAR = "car"
    BIKE = "bike"
    TRUCK = "truck"


class TicketStatus(Enum):
    ACTIVE = "active"
    CLOSED = "closed"


@dataclass
class ParkingSpot:
    id: int
    vehicle_type: VehicleType
    is_available: bool = True


@dataclass
class ParkingFloor:
    id: int
    spots: list[ParkingSpot]


@dataclass
class Ticket:
    id: int
    vehicle_number: str
    issued_at: datetime
    spot_id: int
    level: int
    # Default fields follow required fields. Status can change on exit.
    status: TicketStatus = TicketStatus.ACTIVE


class ParkingLot:
    """Use public operations; do not externally mutate spots, tickets or indexes."""

    def __init__(self, parking_config: list[ParkingFloor]) -> None:
        self.car_allocation_list: list[tuple[int, int]] = []
        self.bike_allocation_list: list[tuple[int, int]] = []
        self.truck_allocation_list: list[tuple[int, int]] = []
        self.parking_lot: dict[int, list[ParkingSpot]] = {}
        self.spot_lookup: dict[tuple[int, int], ParkingSpot] = {}
        self.ticket_id_to_ticket: dict[int, Ticket] = {}
        self.vehicle_no_to_ticket_id: dict[str, int] = {}
        self.free_spots_by_type = {
            VehicleType.CAR: self.car_allocation_list,
            VehicleType.BIKE: self.bike_allocation_list,
            VehicleType.TRUCK: self.truck_allocation_list,
        }
        self.lock = Lock()
        self._next_ticket_id = 1

        for floor in parking_config:
            if floor.id in self.parking_lot:
                raise ValueError(f"Duplicate level ID: {floor.id}")
            self.parking_lot[floor.id] = list(floor.spots)
            for spot in floor.spots:
                key = (floor.id, spot.id)
                if key in self.spot_lookup:
                    raise ValueError(f"Duplicate spot on level: {key}")
                self.spot_lookup[key] = spot

        self._allocation_setup()

    def enter(self, vehicle_number: str, vehicle_type: VehicleType) -> Ticket:
        # One critical section prevents two gates passing the same checks.
        with self.lock:
            if vehicle_number in self.vehicle_no_to_ticket_id:
                raise ValueError("Vehicle already parked")
            if vehicle_type not in self.free_spots_by_type:
                raise TypeError("vehicle_type must be a VehicleType member")

            vehicle_heap = self.free_spots_by_type[vehicle_type]
            if not vehicle_heap:
                raise RuntimeError("No compatible parking spot available")

            # Peek and prepare the ticket before modifying allocation state.
            level, spot_id = vehicle_heap[0]
            spot = self.spot_lookup[(level, spot_id)]
            ticket = Ticket(
                id=self._next_ticket_id,
                vehicle_number=vehicle_number,
                issued_at=datetime.now(UTC),
                spot_id=spot_id,
                level=level,
            )

            heapq.heappop(vehicle_heap)
            spot.is_available = False
            self.ticket_id_to_ticket[ticket.id] = ticket
            self.vehicle_no_to_ticket_id[vehicle_number] = ticket.id
            self._next_ticket_id += 1
            return ticket

    def exit(self, ticket_id: int) -> bool:
        # Validation and release use the same lock as entry.
        with self.lock:
            ticket = self.ticket_id_to_ticket.get(ticket_id)
            if ticket is None:
                raise ValueError("Unknown ticket")
            if ticket.status != TicketStatus.ACTIVE:
                raise ValueError("Ticket is already closed")

            key = (ticket.level, ticket.spot_id)
            spot = self.spot_lookup[key]
            heapq.heappush(self.free_spots_by_type[spot.vehicle_type], key)
            spot.is_available = True
            ticket.status = TicketStatus.CLOSED
            del self.vehicle_no_to_ticket_id[ticket.vehicle_number]
            # Retain the closed ticket so repeated exits can be rejected.
            return True

    def availability(
        self, vehicle_type: VehicleType | None = None
    ) -> dict[int, dict[VehicleType, int]]:
        """Return a consistent snapshot of free counts by level and type."""
        if vehicle_type is not None and vehicle_type not in self.free_spots_by_type:
            raise TypeError("vehicle_type must be a VehicleType member")

        with self.lock:
            types = list(VehicleType) if vehicle_type is None else [vehicle_type]
            # Include configured levels and types even when their count is zero.
            counts = {
                level: {kind: 0 for kind in types}
                for level in self.parking_lot
            }
            for (level, _), spot in self.spot_lookup.items():
                if spot.is_available and spot.vehicle_type in counts[level]:
                    counts[level][spot.vehicle_type] += 1
            # New dictionaries are returned: callers cannot mutate lot state.
            return counts

    def _allocation_setup(self) -> None:
        """Build per-type free-spot heaps from the startup configuration."""
        heaps = self.free_spots_by_type
        # Clearing makes rebuilding safe from duplicate heap entries.
        for heap in heaps.values():
            heap.clear()

        for key, spot in self.spot_lookup.items():
            if spot.is_available:
                heaps[spot.vehicle_type].append(key)

        # Tuples prioritize level first, then spot ID. No sorting is needed.
        for heap in heaps.values():
            heapq.heapify(heap)
