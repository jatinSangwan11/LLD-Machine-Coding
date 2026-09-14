from dataclasses import dataclass
import datetime
from enum import Enum
import math
import threading
from typing import Protocol


class VehicleCategory(Enum):
    MOTORCYCLE = "motorcycle"
    CAR = "car"
    TRUCK = "truck"

class TicketStatus(Enum):
    CLOSED = "closed"
    ACTIVE = "active"

class SpotType(Enum):
    MOTORCYCLE = "motorcycle"
    COMPACT = "compact"
    LARGE = "large"

@dataclass
class Ticket:
    ticket_id: str
    registration_number: str
    vehicle_category: VehicleCategory
    spot_id: str
    floor_number: int
    enter_time: datetime.datetime
    status: TicketStatus = TicketStatus.ACTIVE
    exit_time: datetime.datetime | None = None
    final_charge: float | None = None

@dataclass
class ParkingSpot:
    spot_id: str
    spot_type: SpotType
    is_available: bool

@dataclass
class ParkingFloor:
    floor_number: int
    spots: list[ParkingSpot]

class ParkingLotError(Exception):
    pass


class InvalidTicketError(ParkingLotError):
    pass


class TicketAlreadyClosedError(ParkingLotError):
    pass 

class VehicleAlreadyParkedError(ParkingLotError):
    def __init__(self, registration_number: str) -> None:
        super().__init__(
            f"Vehicle '{registration_number}' is already parked"
        )


class NoCompatibleSpotError(ParkingLotError):
    def __init__(self, vehicle_category: VehicleCategory) -> None:
        super().__init__(
            "No compatible spot is available for "
            f"'{vehicle_category.value}'"
        )

class PricingStrategy(Protocol):
    def calculate(
        self,
        entry_time: datetime.datetime,
        exit_time: datetime.datetime,
        vehicle_category: VehicleCategory,
    ) -> float:
        ...


class HourlyPricing:
    def calculate(
        self,
        entry_time: datetime.datetime,
        exit_time: datetime.datetime,
        vehicle_category: VehicleCategory,
    ) -> float:
        rates = {
            VehicleCategory.MOTORCYCLE: 20,
            VehicleCategory.CAR: 40,
            VehicleCategory.TRUCK: 60,
        }

        duration = exit_time - entry_time
        hours = max(
            1,
            math.ceil(duration.total_seconds() / 3600),
        )

        return rates[vehicle_category] * hours   

class SpotAllocationStrategy(Protocol):
    def find_spot(
        self,
        floors: list[ParkingFloor],
        vehicle_category: VehicleCategory
    ) -> tuple[ParkingSpot, int] | None:
        ...

class SmallestSuitableSpotAllocation:
    def find_spot(
        self,
        floors: list[ParkingFloor],
        vehicle_category: VehicleCategory,
    ) -> tuple[ParkingSpot, int] | None:
        compatible_spot_types = {
            VehicleCategory.MOTORCYCLE: [
                SpotType.MOTORCYCLE,
                SpotType.COMPACT,
                SpotType.LARGE,
            ],
            VehicleCategory.CAR: [SpotType.COMPACT, SpotType.LARGE],
            VehicleCategory.TRUCK: [SpotType.LARGE],
        }
       
        for spot_type in compatible_spot_types[vehicle_category]:
            for floor in sorted(
                floors,
                key=lambda parking_floor: parking_floor.floor_number,
            ):
                for spot in sorted(
                    floor.spots,
                    key=lambda parking_spot: parking_spot.spot_id,
                ):
                    if spot.spot_type == spot_type and spot.is_available:
                        return spot, floor.floor_number

        return None

class TicketStore(Protocol):
    def generate_ticket_id(self) -> str:
        ...

    def save(self, ticket: Ticket) -> None:
        ...

    def get(self, ticket_id: str) -> Ticket | None:
        ...

    def has_active_ticket(self, registration_number: str) -> bool:
        ...


class InMemoryTicketStore:
    def __init__(self) -> None:
        self.ticket_number = 1
        self.tickets: dict[str, Ticket] = {}
        self.active_registrations: set[str] = set()

    def generate_ticket_id(self) -> str:
        ticket_id = f"T-{self.ticket_number}"
        self.ticket_number += 1
        return ticket_id

    def save(self, ticket: Ticket) -> None:
        self.tickets[ticket.ticket_id] = ticket

        if ticket.status is TicketStatus.ACTIVE:
            self.active_registrations.add(ticket.registration_number)
        else:
            self.active_registrations.discard(ticket.registration_number)

    def get(self, ticket_id: str) -> Ticket | None:
        return self.tickets.get(ticket_id)

    def has_active_ticket(self, registration_number: str) -> bool:
        return registration_number in self.active_registrations

class ParkingLot:
    def __init__(
        self,
        configuration: list[ParkingFloor],
        pricing: PricingStrategy | None = None,
        spot_allocator: SpotAllocationStrategy | None = None,
        ticket_store: TicketStore | None = None,
    ) -> None:
        self.parking_floors = list(configuration)
        self.pricing = pricing if pricing is not None else HourlyPricing()
        self.spot_allocator = (
            spot_allocator
            if spot_allocator is not None
            else SmallestSuitableSpotAllocation()
        )
        self.ticket_store = (
            ticket_store
            if ticket_store is not None
            else InMemoryTicketStore()
        )
        self._lock = threading.Lock()

    def park(
        self,
        registration_number: str,
        vehicle_category: VehicleCategory,
    ) -> Ticket:
        with self._lock:
            if self.ticket_store.has_active_ticket(registration_number):
                raise VehicleAlreadyParkedError(registration_number)

            selection = self.spot_allocator.find_spot(
                floors=self.parking_floors,
                vehicle_category=vehicle_category,
            )
            if selection is None:
                raise NoCompatibleSpotError(vehicle_category)

            spot, floor_number = selection
            spot.is_available = False
            ticket_id = self.ticket_store.generate_ticket_id()
            ticket = Ticket(
                ticket_id=ticket_id,
                registration_number=registration_number,
                vehicle_category=vehicle_category,
                spot_id=spot.spot_id,
                floor_number=int(floor_number),
                enter_time=datetime.datetime.now(),
            )
            self.ticket_store.save(ticket)
            return ticket

    def get_availability(self) -> dict[str, object]:
        with self._lock:
            spot_types = tuple(SpotType)
            availability_by_floor: dict[int, dict[str, int]] = {}
            total_availability = {
                spot_type.value: 0 for spot_type in spot_types
            }

            for floor in self.parking_floors:
                floor_availability = {
                    spot_type.value: 0 for spot_type in spot_types
                }

                for spot in floor.spots:
                    if spot.is_available:
                        spot_type = spot.spot_type.value
                        floor_availability[spot_type] += 1
                        total_availability[spot_type] += 1

                availability_by_floor[floor.floor_number] = floor_availability

            return {
                "floors": availability_by_floor,
                "total": total_availability,
            }

    def restore_parking_spot(
        self,
        spot_id: str,
        floor_number: int,) -> bool:
        
        for floor in self.parking_floors:
            if floor.floor_number == floor_number:
                for spot in floor.spots:
                    if spot.spot_id == spot_id and spot.is_available is False:
                        spot.is_available = True
                        return True

        return False

    def exit(self, ticket_id: str) -> Ticket | None:
        with self._lock:
            ticket = self.ticket_store.get(ticket_id)
            if ticket is None:
                raise InvalidTicketError(ticket_id)

            if ticket.status is TicketStatus.CLOSED:
                raise TicketAlreadyClosedError(ticket_id)

            exit_time = datetime.datetime.now()
            fee = self.pricing.calculate(
                ticket.enter_time,
                exit_time,
                ticket.vehicle_category,
            )

            restoration = self.restore_parking_spot(
                ticket.spot_id,
                ticket.floor_number,
            )

            if restoration:
                ticket.exit_time = exit_time
                ticket.status = TicketStatus.CLOSED
                ticket.final_charge = fee
                self.ticket_store.save(ticket)
                return ticket

            return None
