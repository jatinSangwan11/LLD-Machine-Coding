# Parking Lot Progress

Last updated: 2026-11-03

## Status

- Stage: Entry, exit, availability implemented with authorized mentor assistance
- Mode: Interviewer presentation; learner drives requirements and design
- Timer: No timed mock requested or started for this problem
- Source: https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/parking-lot.md
- Accessed: 2026-11-03, main branch; exact commit unavailable from fetched page
- Source requirements inspected; linked implementation not yet reviewed
- Design: Entities, ticket/vehicle maps, direct spot lookup and per-type heaps
- Implementation: Startup, entry, exit, availability implemented; manual checks pass
- Tests: Nine pytest cases pass, including three concurrent cases
- Hints used: Ticket-to-spot and lifecycle lookup, numeric ordering versus UUID,
  duplicate request examples, free-spot index prompt; learner proposed heaps

## Brief and scope

Implement an in-memory Python parking management system with multiple levels,
car/motorcycle/truck support, compatible spots, entry allocation, exit release,
and current availability. Multiple entry/exit points may operate concurrently;
prevent duplicate spot allocation and inconsistent availability. Core scope
comes from the reference requirements. Specific allocation policy, identity,
compatibility rules, failure behavior, and whether billing is needed remain
clarification questions. Do not prescribe classes, patterns, or data structures.

## Next action

Learner implements vehicle/ticket enums and ParkingSpot, ParkingFloor, Ticket
data classes first, then ParkingLot initialization and operations. Review in
small checkpoints; do not supply a full solution. Availability implementation
and concrete failure representation remain to choose during API implementation.

## Learner design and review checkpoint

- Learner proposed spot, floor, ticket and ParkingLot orchestrator with entry,
  exit and availability. Revised UUID level/spot IDs to numeric ordering.
- Spot: numeric spot ID, compatible vehicle type, availability. Floor: numeric
  level number and spots. Ticket: unique ID, vehicle registration, assigned
  level/spot, datetime issued_at, active/closed status.
- ticket_id -> Ticket supports lifecycle checks and assigned spot lookup.
- Learner proposed parked-vehicle set, then selected vehicle_number -> active
  ticket_id dictionary after retry/duplicate-request examples.
- Learner identified scan cost and proposed three min-heaps containing
  (level_number, spot_id), one per vehicle type. Clarified heaps hold only free
  compatible spots. Add direct (level_number, spot_id) -> spot lookup.
- Invariant: each free spot occurs once in its type heap; occupied spots occur
  zero times. Entry/exit must atomically update heaps, spots, tickets and vehicle
  mapping; availability must read a consistent state.
- Learner traced entry/exit happy flow; needed reminder to filter compatibility
  before selecting numeric minimum and close the ticket on exit.
- No solution code generated or reviewed; independent coding evidence pending.

## Interviewer clarification contract

Learner asked for functional requirements, configuration source, compatibility,
allocation policy/algorithm, tickets, fees, and availability inputs.

- One parking lot, multiple levels. Caller supplies level/spot configuration at
  startup through code; configuration fixed during operation, no interactive
  configuration interface or runtime reconfiguration required.
- Vehicle types: motorcycle, car, truck. Each spot holds exactly one vehicle and
  accepts exactly one configured type; no larger-spot fallback.
- Allocation policy: lowest numbered level with a compatible free spot, then
  lowest spot ID (numeric order). Learner chooses algorithm/data structures and
  explains complexity; no prescribed O(1) requirement.
- Entry takes vehicle identifier/license plate and vehicle type. Allocate and
  create a unique active ticket as one atomic operation; ticket identifies the
  vehicle, level/spot and entry time. Return it after successful allocation only.
- Same vehicle cannot have multiple active tickets. Full compatible capacity
  means explicit failure with no ticket or state change.
- Exit takes ticket ID, validates an active ticket, closes it and releases its
  spot atomically. Unknown/already-closed ticket fails without state change.
- Availability is free-spot counts by level and vehicle type, optionally filtered
  by vehicle type; no plate/ticket needed. An occupied spot cannot count as free.
- Multiple gates may call concurrently; protect allocation, ticket lifecycle and
  consistent availability reads.
- No fees/payment in baseline: source does not require billing, so no tariff or
  collection policy. Billing may be a later extension. Tickets, deterministic
  allocation and fixed configuration are interviewer refinements of source scope.
- In-memory APIs and tests; no UI, database, physical gate integration or real
  payment provider required. No solution design or code provided.

## First implementation review

Learner created parking_lot.py and asked about startup configuration and numeric
ordering. Import reproduced TypeError: required vechicle_type follows default
is_available; Ticket similarly puts required spot_id/level after default status.
Ticket issued_at annotates datetime module rather than datetime.datetime.
Methods enter/exit/availability/_allocation_setup are nested inside __init__,
so they are local functions rather than instance methods. sorted(parkingConfig)
returns a list, not the annotated dict; config contract must be explicit.
Proposed existing ParkingFloor/ParkingSpot objects as startup list config;
per-type free heaps use (level,spot) tuple keys and heapify rather than a fully
sorted list. Frozen Ticket requires replacement on close or removal of frozen;
ACTIVE/CLOSED and consistent snake_case fields recommended. No code edited.

Latest authorized correction: at learner request, fixed dataclass field ordering,
vehicle_type/vehicle_number spellings, concrete datetime type, uppercase enums,
mutable ACTIVE/CLOSED ticket status, typed list-of-floors constructor, dictionaries,
and method bodies/indentation. Implemented direct spot lookup and per-type heap
startup setup (free spots only, clear before rebuilding), plus duplicate level
and within-level spot rejection. Entry/exit/availability intentionally raise
NotImplementedError pending learner implementation; no locking added yet.
Manual checks passed unsorted configuration allocation order across levels/spots,
all vehicle heaps, direct lookup identity, repeat setup without duplicates,
invalid duplicate rejection, mutable ticket status, empty configuration, and a
separate sorted-copy configuration example preserving original list order.
git diff --check passed; no permanent tests added. Discussed sorted(key=...)
for both levels and spots as an off-record Python learning question.

## Authorized entry/exit implementation

Learner explicitly requested enter and exit implementation. Mentor implemented
both with one per-lot Lock spanning validation, heap, spot, ticket and vehicle
map updates. Entry uses shared free_spots_by_type (replacing erroneous self.heaps),
rejects duplicate vehicle (ValueError), invalid vehicle type (ValueError), and
no compatible capacity (RuntimeError). Creates per-lot monotonic integer ticket
IDs and timezone-aware UTC timestamps; prepares ticket before modifying state.
Exit rejects unknown/closed IDs (ValueError), releases spot to its type heap,
marks spot free/ticket closed and deletes active vehicle mapping; returns True.
Closed tickets retained for repeated-exit detection. Setup now reuses instance
heap mapping; public internal mutation is outside the contract. Availability
remains NotImplementedError; setup is startup-only, not synchronized runtime API.
Manual checks passed allocation ordering, compatibility, full/duplicate failures,
unknown/double exit, closure and re-entry, concurrent entry/exit stress and final
heap/spot/ticket/vehicle invariants, plus simultaneous duplicate registration
(exactly one succeeds). No permanent tests added; stress does not prove all
interleavings. git diff --check passed. Independent coding not demonstrated.
Next: learner reviews entry/exit and implements lock-protected availability.

## Authorized availability implementation

Learner requested availability and minor-error fixes. Implemented availability
with optional VehicleType filter, same per-lot lock, zero counts for every
configured level/type (including empty floors), and fresh nested dictionaries.
Counts are computed from spot records in O(total spots + levels * selected types)
time, without adding maintained counters. Restored explicit invalid vehicle-type
ValueError in enter (guard was absent in current file), and tidied class spacing
and misleading comment. No other redesign or permanent tests added.
Manual assertions passed initial/all-type/filtered counts, counts after entry
and exit, empty floors/lot, detached result dictionaries, invalid type failures,
and concurrent reads alongside entry/exit with final counts restored.
git diff --check passed. Next: learner reviews availability, adds focused tests,
and explains invariants/complexity; no independent-readiness claim.

Static diagnostic fix at learner request: basedpyright reported unreachable
wrong-type branch under VehicleType annotation, Ruff TRY004 preferred TypeError,
and UP017 preferred UTC alias. Replaced redundant isinstance checks in enter
and availability with supported-type-map membership checks and TypeError;
changed import to datetime.UTC alias via from datetime import UTC, datetime and
used datetime.now(UTC). Environment Python 3.13.3 supports alias (requires 3.11+).
Manual UTC, entry/exit/count and invalid-type checks passed; diff check passed.
Ruff and basedpyright executables unavailable, so diagnostics not rerun directly.
Invalid type now raises TypeError rather than previously documented ValueError.

## Authorized permanent tests

Learner requested tests. Added test_parking_lot.py: nine pytest cases (including
parameterized cases) cover numeric allocation order/type compatibility, unique
active tickets and UTC timestamps, exit/closed-ticket/re-entry lifecycle,
duplicate/full/unknown/closed failures without state changes, availability
filtering/zero counts/snapshot isolation, empty lot and invalid vehicle types,
and duplicate configuration. Concurrent cases isolate duplicate-vehicle and
single-spot contention, plus mixed entry/exit/availability stress with final
heap/spot/ticket/vehicle invariants. Barrier starts and future.result propagate
worker failures; stress is not proof of every interleaving.
Ran venv/bin/python -m pytest problems/04_parking_lot/test_parking_lot.py -q:
9 passed. git diff --check passed. Implementation unchanged in this step.
Tests are mentor-written at explicit request. Next: learner reviews behavior,
complexity and lock scope before end-of-problem assessment.
