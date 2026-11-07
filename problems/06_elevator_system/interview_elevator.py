"""Reduced interview scope: complete rides, FIFO per car, step-driven movement.

No passenger/weight model, doors, intermediate pickup batching or background
threads. The original broader exercise remains in elevator_system.py.
"""

from collections import deque
from dataclasses import dataclass, field, replace
from enum import Enum
from itertools import count
from threading import Lock


class RequestStatus(Enum):
    WAITING = "waiting"
    BOARDED = "boarded"
    REACHED = "reached"


@dataclass
class RideRequest:
    request_id: int
    source: int
    destination: int
    status: RequestStatus = RequestStatus.WAITING


@dataclass
class Elevator:
    elevator_id: int
    current_floor: int = 0
    requests: deque[RideRequest] = field(default_factory=deque)

    @property
    def direction(self) -> int:
        """-1 is DOWN, 0 is stopped, +1 is UP."""
        if not self.requests:
            return 0
        ride = self.requests[0]
        target = ride.source if ride.status is RequestStatus.WAITING else ride.destination
        if target > self.current_floor:
            return 1
        if target < self.current_floor:
            return -1
        return 0

    def step(self) -> None:
        if not self.requests:
            return
        ride = self.requests[0]
        target = ride.source if ride.status is RequestStatus.WAITING else ride.destination
        self.current_floor += self.direction
        if self.current_floor != target:
            return
        if ride.status is RequestStatus.WAITING:
            ride.status = RequestStatus.BOARDED
        else:
            ride.status = RequestStatus.REACHED
            self.requests.popleft()


class ElevatorSystem:
    def __init__(self, floor_count: int, elevator_count: int) -> None:
        if floor_count < 2 or elevator_count < 1:
            raise ValueError("Need at least two floors and one elevator")
        self._floor_count = floor_count
        self._elevators = [Elevator(i) for i in range(1, elevator_count + 1)]
        self._requests: dict[int, RideRequest] = {}
        self._request_ids = count(1)
        self._lock = Lock()

    def request(self, source: int, destination: int) -> int:
        if not 0 <= source < self._floor_count or not 0 <= destination < self._floor_count:
            raise ValueError("Floor is outside this building")
        if source == destination:
            raise ValueError("Source and destination must differ")
        with self._lock:
            elevator = self._choose_elevator(source, destination)
            request_id = next(self._request_ids)
            ride = RideRequest(request_id, source, destination)
            self._requests[request_id] = ride
            elevator.requests.append(ride)
            return request_id

    def step(self) -> None:
        # One lock makes a whole simulation tick atomic to callers.
        with self._lock:
            for elevator in self._elevators:
                elevator.step()

    def check(self, request_id: int) -> RideRequest:
        with self._lock:
            # Copy the record so callers cannot change scheduler-owned state.
            return replace(self._requests[request_id])

    def snapshot(self) -> dict[int, dict[str, int]]:
        with self._lock:
            return {
                e.elevator_id: {
                    "floor": e.current_floor,
                    "direction": e.direction,
                    "pending_rides": len(e.requests),
                }
                for e in self._elevators
            }

    def _choose_elevator(self, source: int, destination: int) -> Elevator:
        requested_direction = 1 if destination > source else -1

        def score(elevator: Elevator) -> tuple[int, int, int]:
            ahead = (source - elevator.current_floor) * requested_direction >= 0
            compatible = elevator.direction == requested_direction and ahead
            # Prefer idle cars, then compatible moving cars, then other cars.
            rank = 0 if not elevator.requests else 1 if compatible else 2
            return rank, abs(elevator.current_floor - source), elevator.elevator_id

        return min(self._elevators, key=score)
