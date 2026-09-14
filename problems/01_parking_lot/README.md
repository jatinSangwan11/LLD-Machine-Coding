# Problem 01: Parking Lot

Status: Responsibility and interface design

## Interview Brief

Design and implement the core software for a parking lot.

At a minimum, the system should allow a vehicle to enter, allocate a suitable
parking spot, issue a ticket, and later process the vehicle's exit so the spot
becomes available again. It should also be possible to inspect current parking
availability.

Use Python and keep the first version in memory. No user interface, HTTP API, or
database integration is required.

The remaining behavior is intentionally unspecified. Clarify it with the
interviewer before proposing the domain model or implementation.

## Clarified Scope

- Vehicle categories are motorcycle, car, and truck. Spot categories are
  motorcycle, compact, and large.
- Motorcycles fit all three categories; cars fit compact or large; trucks fit
  only large.
- Choose the smallest compatible category available anywhere, then the
  lowest-numbered floor, then the lowest spot ID.
- The initialized configuration supplies every floor and its individual spots.
- Availability reports free counts by spot category for every floor and for the
  whole lot.
- The system records entry and exit time automatically. Tickets retain vehicle,
  assigned location, timestamps, status, and final charge.
- Rates are ₹20/hour for motorcycles, ₹40/hour for cars, and ₹60/hour for trucks.
  Charge at least one hour and round every partial hour upward.
- Explicitly reject no compatible spot, duplicate active parking for a vehicle,
  unknown ticket IDs, and attempts to close an already-closed ticket. Failed
  operations do not mutate state.
- The first implementation is sequential and in memory. Payment processing,
  reservations, UI/API/database integration, and runtime layout administration
  are out of scope.
- A required later iteration adds multiple physical gates, concurrent operations,
  locking decisions, and concurrent tests.
