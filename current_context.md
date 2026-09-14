# Current Engineering Context

Last updated: 2026-09-08

## Current Problem

Problem 01: Parking Lot. Design and implement the in-memory core of a parking
lot that handles entry, suitable-spot allocation, ticket issuance, exit, spot
release, and availability inspection.

## Immediate Interview Goal

Reach practical machine-coding and LLD interview readiness by Friday,
2026-09-11 at 12:00 PM IST. The learner will provide company and interviewer
context on Thursday so the final preparation can be tailored. This accelerated
pace is temporary. After the Friday interview, return to the original long-term,
problem-driven learning plan and full pattern/SOLID coverage without treating
the interview deadline as an ongoing constraint.

## Full Roadmap Goal

Target completion of the original LLD preparation roadmap by 2026-09-30. After
the Friday interview, resume the normal problem-driven approach and work toward
practical coverage of all five SOLID principles and all listed design and
engineering patterns by the end of September. Coverage must remain evidence
based; superficial pattern mentions do not count as completion.

## Current Stage

Behavior-first implementation preparation. The main entry and exit flows have
been traced. The next task is one complete successful parking behavior, starting
from a test.

## Requirements

- A vehicle can enter the parking lot.
- The system allocates a suitable available parking spot.
- Entry produces a parking ticket.
- A vehicle can exit and its spot becomes available again.
- Current parking availability can be inspected.
- The first version is implemented in Python and stores state in memory.
- No UI, HTTP API, or database integration is required.
- Supported vehicle categories: motorcycle, car, and truck.
- Supported parking-spot categories: motorcycle, compact, and large.
- A motorcycle may use a motorcycle, compact, or large spot.
- A car may use a compact or large spot.
- A truck may use only a large spot.
- Allocation prefers the smallest compatible available spot; an incompatible
  smaller spot must never be assigned.
- Allocation is deterministic across the lot: choose the smallest compatible
  spot category available anywhere, then the lowest-numbered floor containing
  that category, then the lowest spot ID on that floor.
- The parking lot supports multiple floors configured when the lot is created.
- Every parking spot belongs to exactly one floor.
- Availability must report free-spot counts grouped by spot category for each
  floor and for the entire parking lot.
- A parking ticket has a unique ticket ID, vehicle registration number, vehicle
  category, floor ID, assigned spot ID, entry timestamp, and status.
- A newly issued ticket is active. When exit completes, it records the exit
  timestamp and final charge and becomes closed.
- Parking uses vehicle-category hourly rates: motorcycle ₹20/hour, car ₹40/hour,
  and truck ₹60/hour.
- Chargeable duration has a one-hour minimum and every started hour is charged
  as a complete hour. There is no grace period in the first version.
- The final charge is `chargeable_hours × the vehicle category's hourly rate`.
- If no compatible spot is available, reject entry with an explicit
  no-spot-available error, issue no ticket, and leave state unchanged.
- An invalid ticket ID is one the system has never issued or cannot find. Reject
  exit with an explicit invalid-ticket error and leave state unchanged.
- A closed ticket is a real ticket already used for a successful exit. Reject a
  repeated exit with an explicit ticket-already-closed error and leave state
  unchanged. Closed tickets remain available as historical records.
- The first version models one logical entry and one logical exit flow; gate
  entities and gate IDs are out of scope.
- A vehicle registration number may have at most one active ticket. Reject a
  duplicate entry with an explicit vehicle-already-parked error and leave state
  unchanged.
- The first implementation may process operations sequentially. A required
  second iteration will add multiple physical entry/exit gates and concurrent
  operations, including race-condition analysis, thread safety, locking scope,
  and concurrent tests.
- The system calculates the parking charge but does not collect or process a
  payment.
- Advance reservations are out of scope.
- Runtime administrative operations such as adding/removing floors or spots and
  changing rates are out of scope; lot layout is supplied during initialization.
- The system captures entry and exit timestamps automatically when the
  corresponding operation succeeds; callers do not supply business timestamps.
- Tests must be able to control time deterministically. The concrete mechanism
  will be chosen during domain modeling and interface design.
- Initialization validation and other low-level details will be resolved during
  modeling and implementation.

## Current Architecture

No architecture has been chosen. Domain modeling is in progress.

Preliminary vocabulary identified during a noun-extraction exercise:

- `ParkingSpot`
- `ParkingTicket`

These are hypotheses, not accepted classes. Restart modeling from the entry
happy path and justify collaborators from behavior, state, and responsibility.

Open modeling decision: a floor may become a distinct entity responsible for its
spot collection and floor-level availability, or it may remain a `floor_id` on
spots grouped by the lot. Choose based on useful behavior and invariants, not the
fact that "floor" is a noun.

Current entry-flow draft:

1. Receive vehicle category and registration information.
2. Search for a compatible available spot.
3. If found, issue a ticket containing the required information.
4. If none exists, issue no ticket and report failure without changing state.

Still to add explicitly: duplicate-active-vehicle validation, deterministic spot
selection, automatic time capture, and the successful occupancy/ticket state
changes as one consistent operation.

Agreed exit flow after review:

1. Receive a ticket ID and find the stored ticket.
2. Reject an unknown ticket without changing state.
3. Reject an already-closed ticket without changing state.
4. Capture exit time once and calculate the rounded charge from the stored entry
   time and vehicle category.
5. As one consistent successful transition, record exit time/charge, close the
   ticket, release its assigned spot, and remove the vehicle from active parking.
6. Return the closed ticket and calculated charge; do not process payment.

## Implementation Status

Only the interview brief exists in `problems/01_parking_lot/README.md`. No design,
implementation, or tests exist yet.

## Current Implementation Assignment

Use the behavior-first approach. Write one test for a successful car entry, then
implement only enough code for this complete flow:

1. Initialize a lot with configured floors and spots.
2. Submit a car registration and category to `park`.
3. Select the compact spot required by the test.
4. Mark it occupied.
5. Return an active ticket with the vehicle and assigned-location information.
6. Confirm that compact availability decreased by one.

Do not yet implement exit, pricing, failure cases, concurrency, separate policy
objects, or design patterns. Do not replace this assignment with isolated
bottom-up object exercises.

## Current Blocker

None. The next work is the successful-entry test and the minimum implementation
needed to pass it.

## Mistakes

- The requirements summary omitted availability reporting, deterministic spot
  ordering, duplicate active-entry and no-spot failures, automatic timestamps,
  pricing boundaries, excluded features, and the planned concurrency iteration.
  These omissions were corrected before modeling.
- The mentor introduced domain modeling too mechanically as noun extraction and
  started treating vocabulary as classes before tracing behavior. The learner
  correctly challenged this; modeling is being restarted behavior-first.
- The mentor then assigned an isolated `ParkingSpot` exercise, which switched to
  bottom-up implementation and conflicted with the agreed behavior-first path.
  That assignment has been withdrawn and replaced by one complete entry flow.
- The first exit-flow draft accidentally added a request for payment even though
  payment processing was explicitly excluded, and omitted releasing the spot and
  removing the vehicle from active parking. Corrected before interface design.

## Incorrect Assumptions

- Initially interpreted "smallest available spot" as potentially allowing a
  large vehicle to occupy a physically smaller, incompatible spot. Corrected to
  "smallest compatible available spot": compatibility is a hard constraint and
  size preference is applied only after compatibility filtering.
- Initially relied on the physical fact that one vehicle cannot occupy two spots
  to prevent duplicate entry. Software can still receive duplicated, retried, or
  concurrent entry commands, so the invariant must be enforced explicitly.
- Described initialization mainly as counts of spots for vehicle types. The
  configuration actually supplies floors and individually identified spots with
  spot categories; vehicle categories use them according to compatibility rules.

## Concepts Encountered

- Requirement clarification using five buckets: scope, actors/actions, business
  rules, failure cases, and system constraints.
- Entity lifecycle data: distinguish information known at ticket issuance from
  information added when the parking session closes.
- Turning pricing language into testable boundary rules, including minimum
  duration and partial-hour rounding.
- Failure taxonomy and atomic behavior: distinguish resource exhaustion, unknown
  identity, and invalid lifecycle transitions; failed operations must not partly
  mutate state.
- Concurrency and race conditions: overlapping operations can observe and mutate
  shared state inconsistently even when each operation works correctly alone.
- Domain invariants must be protected at the software boundary even when the
  corresponding real-world violation seems physically impossible.
- Scope control: distinguish the core workflow from adjacent payment,
  reservation, and administration capabilities.
- A domain is the real-world problem area, vocabulary, behavior, and business
  rules the software represents. A domain model is a deliberately simplified
  representation of its important concepts, state, relationships, behavior, and
  invariants.
- Deriving clarification questions by tracing each operation through input,
  decisions, state changes, output, and failures rather than memorizing a fixed
  question list.
- Initialization configuration versus runtime state: the caller supplies the
  lot's fixed floor/spot layout at startup, while parking operations change only
  occupancy and ticket state during the first version.
- Behavior-first, responsibility-driven modeling: scenarios, decisions, state
  transitions, and invariants justify objects; grammar does not.
- Distinguishing the external caller/actor that requests an operation from a
  domain entity such as a vehicle; real vehicles do not invoke software methods.
- Classifying model elements by semantics: entities have stable identity and a
  lifecycle; value objects are defined by their values; services own behavior
  that does not naturally belong to one entity; some concepts remain plain
  collections or configuration.
- Evaluating candidate objects by identity, state ownership, required knowledge,
  invariants, cohesion, and expected change rather than assuming every domain
  noun deserves a class.
- Real interview design is iterative: clarify the highest-impact ambiguities,
  trace a core scenario, form provisional responsibilities/objects, implement a
  thin working path, test it, and revise the model as failures or changes expose
  missing boundaries.

## Patterns Encountered

None.

## SOLID Principles Encountered

None.

## Hints Used

- Level 1 — Clarification: provided a reusable question framework and a guiding
  question without supplying the parking-lot requirements or design.
- Level 1 — Domain modeling: provided an operation-tracing framework and asked
  the learner to identify one stateful real-world concept before proposing a
  full model.
- Level 2 — Domain modeling: replaced noun extraction with a concrete
  happy-path and responsibility-assignment workflow.
- Level 3 — Responsibility assignment: illustrated the information-owner rule
  and showed how individual-spot, floor-level, and lot-wide knowledge differ.

## Tests Written

None; there is no implementation to test yet.

## Codex Feedback

The learner is new to requirement clarification and currently needs a structured
mental checklist. Prompt one category at a time, then gradually remove the
scaffold in later problems.

The learner successfully asked the first clarification question about supported
vehicle and spot categories. The next step is to distinguish categories from
the compatibility policy between them.

The learner challenged an ambiguous phrase instead of accepting it. This is good
clarification behavior: separate hard validity rules from optimization or
preference rules.

Clarification is approaching diminishing returns. Ask two final scope questions,
then have the learner summarize the agreed requirements and move to domain
modeling.

The first summary captured the core entry-ticket-exit lifecycle and failure
atomicity. It needed reminders for several allocation, reporting, boundary, and
scope details. Requirements/clarification is provisionally 3/5 with a Level 1
scaffold.

During domain modeling, the learner initially grouped spot occupancy (state), a
parking ticket (domain concept), and exit (operation). Continue teaching the
distinction between an entity, its state, and a use case.

The learner explicitly asked for the reasoning system behind the clarification
questions. Continue teaching question generation from workflow and ambiguity,
then gradually remove the framework rather than asking them to memorize a list.

The learner's first behavior-first entry flow correctly separated success from
no-capacity failure. It still needs the duplicate-entry invariant, deterministic
selection, time capture, and explicit atomic state changes.

The exit-flow draft correctly included ticket lookup, distinct invalid/closed
failures, time-based charge calculation, and ticket closure. It omitted two
coupled state changes and crossed the agreed payment boundary.

## Questions For ChatGPT

- What do "domain" and "domain modeling" mean in practical LLD work?
- How do engineers systematically derive the important clarification questions
  in a real interview without memorizing a problem-specific checklist?
- Do real LLD and machine-coding interviews generally progress through
  clarification, scenario modeling, responsibility assignment, implementation,
  tests, and requirement-driven revision, and where should object identification
  occur in that loop?

## ChatGPT Discussion

None.

## Next Action

Keep one stable assignment: write a successful-entry test, then implement the
minimum complete `park` behavior needed to pass it. Explain unfamiliar words in
plain language. Introduce SOLID or patterns only after the current code exposes a
specific problem that the principle solves.
