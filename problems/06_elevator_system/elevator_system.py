import heapq
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from math import isfinite
from threading import Lock


class Direction(Enum):
    UP = "up"
    DOWN = "down"
    IDLE = "idle"


class PassengerStatus(Enum):
    WAITING = "waiting"
    BOARDED = "boarded"
    REACHED = "reached"


class ElevatorStatus(Enum):
    IDLE = "idle"
    MOVING = "moving"
    STOPPED = "stopped"


@dataclass
class Passenger:
    passenger_id: str
    weight_kg: float
    # The simulation owns status changes during boarding and exiting.
    status: PassengerStatus = PassengerStatus.WAITING


@dataclass(frozen=True)
class PickupRequest:
    passenger_id: str
    pickup_floor: int
    # Passenger's intended direction, independent of the elevator's approach.
    requested_direction: Direction


@dataclass(frozen=True)
class StepResult:
    boarded: tuple[str, ...] = ()
    reached: tuple[str, ...] = ()
    waiting: tuple[str, ...] = ()


@dataclass(frozen=True)
class ElevatorSnapshot:
    elevator_id: str
    current_floor: int
    status: ElevatorStatus
    direction: Direction
    doors_open: bool
    current_load_kg: float
    max_load_kg: float
    onboard: tuple[str, ...]
    destinations: tuple[tuple[str, int], ...]
    assigned_pickups: tuple[str, ...]
    up_stops: tuple[int, ...]
    down_stops: tuple[int, ...]


class Elevator:
    """One step-driven car; the system chooses which pickups to assign to it.

    Public methods synchronize this car's state. Do not externally mutate its
    collections or a registered Passenger. Cross-car coordination belongs to
    ElevatorSystem, which is not implemented here.
    """

    def __init__(self, elevator_id: str, max_load_kg: float, floor_count: int = 10) -> None:
        if not isfinite(max_load_kg) or max_load_kg <= 0:
            raise ValueError("Maximum load must be a positive, finite weight")
        if floor_count < 2:
            raise ValueError("A building needs at least two floors")
        self.elevator_id = elevator_id
        self.floor_count = floor_count
        self.current_status = ElevatorStatus.IDLE
        self.current_direction = Direction.IDLE
        self.current_floor = 0
        self.doors_open = False
        self.max_load_kg = max_load_kg
        self.current_load_kg = 0.0
        self.up_heap: list[int] = []
        self.down_heap: list[int] = []
        self.up_stop_set: set[int] = set()
        self.down_stop_set: set[int] = set()
        self.onboard_passengers: dict[str, Passenger] = {}
        self.passenger_destinations: dict[str, int] = {}
        self._assigned_pickups: dict[str, tuple[Passenger, PickupRequest]] = {}
        self._boarding_directions: dict[str, Direction] = {}
        self._lock = Lock()

    def assign_pickup(self, passenger: Passenger, pickup_floor: int, direction: Direction) -> None:
        """Retain an assigned pickup. This accepts work; it does not move the car."""
        self._validate_floor(pickup_floor)
        if direction not in (Direction.UP, Direction.DOWN):
            raise ValueError("A pickup needs UP or DOWN")

        if (pickup_floor == 0 and direction is Direction.DOWN) or (
            pickup_floor == self.floor_count - 1 and direction is Direction.UP
        ):
            raise ValueError("Requested direction leaves the building")

        if not isfinite(passenger.weight_kg) or passenger.weight_kg <= 0:
            raise ValueError("Passenger weight must be positive and finite")
        if passenger.weight_kg > self.max_load_kg:
            raise ValueError("Passenger exceeds this elevator's maximum load")

        with self._lock:
            passenger_id = passenger.passenger_id
            if passenger_id in self._assigned_pickups or passenger_id in self.onboard_passengers:
                raise ValueError("Passenger is already assigned to this elevator")
            if passenger.status is not PassengerStatus.WAITING:
                raise ValueError("Only a waiting passenger can request pickup")
            request = PickupRequest(passenger_id, pickup_floor, direction)
            self._assigned_pickups[passenger_id] = (passenger, request)
            self._refresh_stops()

    def select_destination(self, passenger_id: str, destination_floor: int) -> None:
        """Record an onboard passenger's destination; never advance the simulation."""
        self._validate_floor(destination_floor)
        with self._lock:
            if passenger_id not in self.onboard_passengers:
                raise ValueError("Passenger is not onboard this elevator")
            if passenger_id in self.passenger_destinations:
                raise ValueError("Passenger already selected a destination")
            direction = self._boarding_directions[passenger_id]
            if (direction is Direction.UP and destination_floor <= self.current_floor) or (
                direction is Direction.DOWN and destination_floor >= self.current_floor
            ):
                raise ValueError("Destination must follow the passenger's requested direction")
            self.passenger_destinations[passenger_id] = destination_floor
            self._refresh_stops()

    def step(self) -> StepResult:
        """Move at most one floor OR service open doors, never both in one tick."""
        with self._lock:
            if self.doors_open:
                return self._service_floor()

            # The caller selects destinations between ticks after boarding.
            if any(p not in self.passenger_destinations for p in self.onboard_passengers):
                self.current_status = ElevatorStatus.STOPPED
                return StepResult()

            # A pickup at the current floor must not require moving away first.
            if self._open_at_service_floor():
                return StepResult()
            self._choose_direction()
            if self.current_direction is Direction.IDLE:
                self.current_status = ElevatorStatus.IDLE
                return StepResult()

            self.current_floor += 1 if self.current_direction is Direction.UP else -1
            self.current_status = ElevatorStatus.MOVING
            self._refresh_stops()
            self._open_at_service_floor()
            return StepResult()

    def snapshot(self) -> ElevatorSnapshot:
        """Expose a stable view instead of returning mutable internal maps."""
        with self._lock:
            return ElevatorSnapshot(
                self.elevator_id, self.current_floor, self.current_status,
                self.current_direction, self.doors_open, self.current_load_kg,
                self.max_load_kg, tuple(self.onboard_passengers),
                tuple(self.passenger_destinations.items()), tuple(self._assigned_pickups),
                tuple(sorted(self.up_stop_set)), tuple(sorted(self.down_stop_set, reverse=True)),
            )

    def _refresh_stops(self) -> None:
        # Passenger/request records are authoritative. Rebuild the small route
        # indexes after changes so shared stops cannot become stale or duplicated.
        floors = set(self.passenger_destinations.values())
        floors.update(request.pickup_floor for _, request in self._assigned_pickups.values())
        self.up_stop_set = {floor for floor in floors if floor > self.current_floor}
        self.down_stop_set = {floor for floor in floors if floor < self.current_floor}
        self.up_heap = list(self.up_stop_set)
        self.down_heap = [-floor for floor in self.down_stop_set]
        heapq.heapify(self.up_heap)
        heapq.heapify(self.down_heap)

    def _choose_direction(self) -> None:
        if self.current_direction is Direction.UP and self.up_heap:
            return
        if self.current_direction is Direction.DOWN and self.down_heap:
            return
        if self.current_direction is Direction.UP and self.down_heap:
            self.current_direction = Direction.DOWN
        elif self.current_direction is Direction.DOWN and self.up_heap:
            self.current_direction = Direction.UP
        elif self.up_heap and self.down_heap:
            up_distance = self.up_heap[0] - self.current_floor
            down_distance = self.current_floor + self.down_heap[0]
            self.current_direction = Direction.UP if up_distance <= down_distance else Direction.DOWN
        elif self.up_heap:
            self.current_direction = Direction.UP
        elif self.down_heap:
            self.current_direction = Direction.DOWN
        else:
            self.current_direction = Direction.IDLE

    def _open_at_service_floor(self) -> bool:
        pickups = [ request 
                    for _, request in self._assigned_pickups.values()
                    if request.pickup_floor == self.current_floor]
        if self.current_direction is Direction.IDLE and pickups:
            self.current_direction = pickups[0].requested_direction
        ahead = self.up_heap if self.current_direction is Direction.UP else self.down_heap
        matching = any(r.requested_direction is self.current_direction for r in pickups)
        if pickups and not matching and not ahead:
            # Arrival direction and passenger direction may differ: approach
            # floor 3 going DOWN, then turn UP before boarding its UP passengers.
            self.current_direction = pickups[0].requested_direction
            matching = True
        dropping_off = self.current_floor in self.passenger_destinations.values()
        if dropping_off or matching:
            self.doors_open = True
            self.current_status = ElevatorStatus.STOPPED
            return True
        return False

    def _service_floor(self) -> StepResult:
        reached, boarded, waiting = [], [], []
        for passenger_id, floor in list(self.passenger_destinations.items()):
            if floor == self.current_floor:
                passenger = self.onboard_passengers.pop(passenger_id)
                passenger.status = PassengerStatus.REACHED
                del self.passenger_destinations[passenger_id]
                del self._boarding_directions[passenger_id]
                reached.append(passenger_id)
        load = self._refresh_load()

        # Drop off first. Try assigned passengers in acceptance order; those
        # who cannot fit remain WAITING and are returned for system reassignment.
        for passenger_id, (passenger, request) in list(self._assigned_pickups.items()):
            if request.pickup_floor != self.current_floor or request.requested_direction is not self.current_direction:
                continue
            new_load = load + Decimal(str(passenger.weight_kg))
            if new_load > Decimal(str(self.max_load_kg)):
                waiting.append(passenger_id)
            else:
                self.onboard_passengers[passenger_id] = passenger
                self._boarding_directions[passenger_id] = request.requested_direction
                passenger.status = PassengerStatus.BOARDED
                load = new_load
                boarded.append(passenger_id)
            del self._assigned_pickups[passenger_id]

        self.current_load_kg = float(load)
        self.doors_open = False
        self.current_status = ElevatorStatus.STOPPED
        self._refresh_stops()
        if not self.onboard_passengers and not self._assigned_pickups:
            self.current_direction = Direction.IDLE
            self.current_status = ElevatorStatus.IDLE
        return StepResult(tuple(boarded), tuple(reached), tuple(waiting))

    def _refresh_load(self) -> Decimal:
        # Decimal-from-string avoids 0.1 + 0.2 accidentally exceeding a 0.3 limit.
        total = sum((Decimal(str(p.weight_kg)) for p in self.onboard_passengers.values()), Decimal(0))
        self.current_load_kg = float(total)
        return total

    def _validate_floor(self, floor: int) -> None:
        if not 0 <= floor < self.floor_count:
            raise ValueError("Floor is outside this building")
