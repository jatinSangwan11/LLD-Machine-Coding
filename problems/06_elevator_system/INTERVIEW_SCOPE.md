# Compact Elevator Machine-Coding Exercise

The learner requested this reduced version after the detailed simulation became
too large. Use `interview_elevator.py` as the main implementation for this
attempt. Keep `elevator_system.py` as the earlier detailed reference.

## Agreed scope for this reduced attempt

- Multiple elevators, configurable floor count, all initially at floor 0.
- Submit a complete ride: source and destination together; return request ID.
- Assign using idle preference, then compatible movement direction and pickup
  ahead, then fallback. Distance and elevator ID break ties within a category.
- Each elevator completes assigned rides in FIFO order. It reaches the source
  before moving to the destination; no en-route pickup batching or reassignment.
- Caller advances simulation with `step()`. Each elevator moves at most one
  floor per call. Pickup/drop-off occurs upon reaching the relevant floor.
- Report WAITING, BOARDED and REACHED, plus elevator snapshots.
- One system lock synchronizes submission, a whole simulation tick and reads.
- Reject invalid floors/same-floor journeys; unknown IDs raise KeyError.

Capacity in kg, passenger identity, separate hall/cabin requests, explicit door
ticks, and route batching from the original expanded scope are omitted here.
This is a negotiated reduced exercise, not completion of the original full
reference requirements. Adding these later requires revisiting the model.

## Architecture

`ElevatorSystem` owns dispatch, request lookup and the synchronization boundary.
`Elevator` owns its current floor and FIFO ride queue. `RideRequest` owns journey
state. Direction is derived from the active ride's next target rather than
stored separately. A thread-safe system API does not imply background movement.

## Example

```python
from interview_elevator import ElevatorSystem

system = ElevatorSystem(floor_count=10, elevator_count=2)
ride_id = system.request(source=2, destination=5)
for _ in range(5):
    system.step()
print(system.check(ride_id).status.value)  # reached
print(system.snapshot())
```

## Verification and complexity

Run: `venv/bin/python -m pytest problems/06_elevator_system/test_interview_elevator.py -q`.

Six tests cover a complete ride, per-tick movement, FIFO and pickup-before-exit,
dispatch policy, input failures, snapshot isolation, and concurrent submissions.
For E elevators: dispatch is O(E), a system tick and snapshot are O(E), and
request lookup is O(1) average. Deque append/popleft are O(1). Records retain
completed history, so storage grows with total accepted requests.
