# Elevator System Progress

Last updated: 2026-11-07

- Stage: Compact interview solution implemented at learner request; walkthrough next
- Mode: Interviewer; no timed mock requested or started
- Source: https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/elevator-system.md
- Accessed: 2026-11-07, main branch; exact commit unavailable from fetched page
- Requirements and reference elevator.py/elevator_state.py inspected on main;
  exact commit unavailable. Reference uses State/Observer and real-time sleeps;
  our agreed deterministic passenger/door/weight model is an adaptation.
- Primary implementation: `interview_elevator.py`, reduced-scope ElevatorSystem;
  six focused pytest tests pass. See INTERVIEW_SCOPE.md for exact contracts.
- Earlier detailed implementation: `elevator_system.py`, individual elevator
  behavior only; retained as a reference with its separate six tests.
- Assistance: Requirement/design guidance and requested data definitions supplied

## Brief

Implement an in-memory Python system for multiple elevators and multiple floors.
Support pickup requests and destination selection, capacity limits, allocation
and stop ordering that consider direction and proximity, and concurrent requests
without race conditions. Demonstrate behavior with tests and explain policies
and trade-offs. Do not promise globally optimal scheduling from the source's
informal efficiency requirement; clarify a concrete policy before implementation.

## Clarification pending

Most baseline behavior has now been clarified in the sections below. Remaining
details include invalid/duplicate requests, impossible passenger weights,
same-floor arrivals, boarding order when capacity is limited, and thread-safe
state transitions. Historical notes below reflect earlier checkpoints.

## Next action

Learner walks through the compact request/dispatch/step/check flow. Use the
reduced scope in INTERVIEW_SCOPE.md, not the full historical passenger/door/weight
model below. Discuss extensions only after the smaller flow is understood.
Earlier next actions and scope discussions below are historical.

## Design reasoning for revision

Derive stored state by asking which operation or invariant needs it; these
structures are choices, not required class-diagram elements.

| Requirement or question | State/structure | Why it exists |
| --- | --- | --- |
| Next ascending stop | `up_heap` with positive floors | Retrieve the lowest pending UP stop without sorting after each request. |
| Next descending stop | `down_heap` with negative floors | A min-heap returns the highest actual floor first when keys are negated. |
| Is this floor already scheduled? | `up_stop_set`, `down_stop_set` | Multiple requests for a floor need one stop; set membership is average O(1), heap membership is O(n). |
| Who is physically onboard? | `onboard_passengers`, passenger ID to object | Validate destination selection, find exiting passenger weight, and update journey state. |
| Where does each passenger exit? | `passenger_destinations`, passenger ID to floor | A stop heap says where to stop, but not which passengers leave there. |
| Are doors open? | `doors_open` | Stopped with open doors differs from idle with closed doors; determines whether a step moves or serves passengers. |

### Heap and set invariants

- Each elevator owns its own collections, initialized per instance.
- Store actual positive floor numbers in duplicate sets; negate only DOWN heap keys.
- Heap and corresponding set describe the same pending floors; update both
  together on stop insertion and service/removal.
- Several passengers can share one stop without losing their individual requests.
- Heap head lookup is O(1); inserting/removing a stop is O(log s) for s stops.
- A sorted list could also work for this small-building scope. Heaps plus sets
  trade additional bookkeeping for efficient dynamic ordering and membership.

### Passenger and destination reasoning

- Boarding adds the passenger to the onboard map and increases current kg.
- Destination selection adds that passenger's destination and schedules the floor.
- At a service floor, identify all passengers whose selected destination matches
  it; remove them from both maps, reduce load and mark them REACHED.
- Current load equals the sum of onboard passenger weights. With float weights,
  implementation/tests must account for numeric precision or choose a precise
  weight representation before relying on exact equality.
- The onboard map can contain a passenger absent from the destination map:
  they have boarded but not selected a destination yet. Hold departure until
  required destinations are supplied, per our agreed baseline.
- Dictionary values reference Passenger objects; they do not copy them.
- Finding everyone exiting at a floor currently scans onboard destinations;
  that is acceptable for small elevator occupancy. Do not add another index yet.

### Door-state reasoning and use

- Status MOVING/STOPPED/IDLE and direction do not tell us whether doors are open.
- Never move with doors open. Do not infer door state merely from being stopped.
- Closed doors plus work: a movement step advances at most one floor and opens
  the doors when it reaches a service stop. Same-floor service needs an explicit
  branch; it must not require moving away and returning.
- Open doors: the next service step unloads arrivals first, then boards eligible
  waiting passengers who fit, updates states/load and closes doors without moving.
- Closed doors and no work: remain idle. No real-time sleep is involved.
- Example: floor 0 -> 1; next step 1 -> 2 and open; following step boards,
  changes load 0 -> 70 kg and closes doors. Arrival alone does not serve pickup;
  actual boarding does. Destination is served when the passenger exits.

## Scope and a 90-minute interview

This version combines dispatch, routing, a movement/door state machine,
two-stage passenger input, capacity and reassignment, status queries and
concurrency. These interacting requirements make it substantial. The original
brief did not prescribe all the extra simulation details we introduced; treat
them as clarified exercise scope, not universal interview requirements.

For this learner, the full version is currently too much to expect independently
in 90 minutes: data definitions/initialization already required mentor assistance.
A smaller agreed scope can be viable; prioritize one complete tested flow over
completing every extension. Do not claim independent interview readiness from
mentor-written code.

A proposed 90-minute scope, only if explicitly agreed with the interviewer:
one elevator first, deterministic step simulation, a fixed routing policy,
capacity handling, and focused happy/edge tests. Add multiple-elevator dispatch
and concurrency after the core works, or retain them and negotiate simpler
boarding/door behavior. Do not silently remove original requirements.

Proposed time budget: 0-10 clarification, 10-20 behavior/design, 20-60 working
implementation, 60-80 tests/debugging, 80-90 limitations/complexity defense. This
is our planning guidance, not an attributed company interview rubric. No timer
is active. Current code is only the model and constructor, not a finished system.

## Clarifying questions

- **What is elevator proximity?** Distance in floors from elevator's current
  floor to the pickup floor. Direction and pending stops also influence service;
  the nearest car is not automatically the best assignment.
- **How many floors and elevators?** Caller supplies fixed startup configuration:
  positive floor count F and elevator count E, floors numbered 0 through F-1.
  Example for discussion: F=10, E=3. Initially all cars idle at floor 0;
  no basements or restricted-access floors in this baseline. This is an
  interviewer refinement, not an exact configuration from the reference.
- **Will we discuss service order?** Yes. Agree observable dispatch and routing
  behavior before implementation; learner proposes policy and trade-offs.
- **What does handling requests during service mean?** New pickup or cabin
  destination requests can arrive while cars move or perform an existing stop.
  Accept and retain them; choose assignment and when to serve them according
  to the agreed policy. No requirement to interrupt an existing door/stop action.

- **Capacity unit:** Learner selected kilograms, not passenger count. Each
  elevator needs a configured maximum weight and a current load. Weight input,
  boarding/exiting behavior, and handling a passenger who cannot fit are still
  to clarify; capacity is not the number of pending requests.

## Latest clarification checkpoint

Clarifications are not complete. Hall UP/DOWN calls with in-car destination
selection were introduced; capacity in kg is the learner's latest decision.
Still settle simulated weight input/boarding, dispatch policy, stop ordering,
simulation progression, duplicate/invalid calls, and full-elevator behavior
before implementation. Earlier behavior prompt was premature.

- **Insufficient capacity at pickup:** Learner confirmed that a passenger who
  cannot board remains waiting for another elevator. Do not add their weight,
  mark them picked up, or discard their outstanding pickup request. Eligibility
  must be checked at actual boarding. Representation of waiting passengers and
  weights remains to derive; simulation timing is the next clarification.

## Step and routing clarification

Learner selected explicit step-based simulation rather than timed background
movement, and identified per-elevator state advancement as elevator-owned.
Public system.step advances each elevator once. Proposed tick contract: at most
one floor of movement per elevator, open at a service stop; a subsequent step
handles exiting/boarding and closes doors without movement. Drop-off precedes
boarding, and passengers who cannot fit remain waiting. No real-time sleeping.
Corrected learner's assumption that elevators always traverse to endpoints:
route toward pending service, reverse when policy requires, idle when no work;
never move outside configured floor range. Detailed dispatch/routing remains
unsettled. No classes or solution code created.

## Accepted dispatch and stop policy

Learner accepted the proposed baseline: prefer an idle elevator or a car moving
in the requested direction with the pickup ahead; choose the nearest eligible
car and break ties by elevator ID. If none is eligible, retain the request.
Continue the current sweep, serving assigned destinations and same-direction
pickups ahead. Do not reverse solely because a new request arrives. When no
assigned work remains ahead, reverse for assigned work behind, otherwise idle.
Treat this as a deterministic interview policy, not globally optimal routing.
Next: trace one complete ride (request, arrival, doors, boarding/load, destination,
exit/load reduction), then derive public operations and responsibilities.

## Learner entity proposal

Learner proposed Elevator, ElevatorSystem and Passenger. Elevator state includes
ID, movement status, direction, current floor, maximum kg and current kg. Learner
correctly noted an idle elevator still has a current floor. System state and
passenger details not yet derived. Corrected interpretation: destination selection
is a public input from an onboard passenger, not private behavior triggered by
pickup; accepting a request does not automatically advance the simulation.
Public step advances all cars separately. Need door state, outstanding stops and
onboard passenger identity/destination association, with load matching onboard
weights. System owns building configuration, elevator collection and unresolved
hall requests/assignments, rather than duplicating each car's mutable state.
No data structures/classes/code prescribed or created. Next: learner identifies
where a hall request lives before assignment and how it links to a passenger.

## Passenger API and boarding checkpoint

Learner proposed Passenger with passenger_id, WAITING/BOARDED/REACHED status and
weight, plus passenger_id -> Passenger lookup; destination input includes
passenger_id and destination_floor. Pickup also needs source floor and UP/DOWN.
Learner confirmed automatic boarding: the service step after doors open unloads
arrivals, boards assigned waiting passengers who fit, updates kg and BOARDED
state, and retains those unable to fit. No public board() needed. Destination
selection remains a caller input after boarding; reject it before boarding.
Need a defined wait-for-destination rule so a boarded passenger can choose
before the elevator departs; this detail remains to settle before coding.
Next: finalize pickup/destination/state-query API and post-boarding behavior,
then choose pending-stop structures. No implementation written.

## Authorized initial data definitions

At learner request, added elevator_system.py containing Direction (UP/DOWN/IDLE),
PassengerStatus (WAITING/BOARDED/REACHED), mutable Passenger with ID/weight_kg
and default WAITING status, and frozen PickupRequest with passenger ID, source
floor, and requested direction. No dispatch, elevator, heap or step code added.
Import/constructor smoke check and git diff --check passed. Weight positivity
and valid hall directions/floors still require validation in later behavior.
Next: learner reviews definitions and proposes Elevator state before implementation.

## First Elevator code review

Learner added ElevatorStatus (IDLE/MOVING/STOPPED) and a plain Elevator class
with annotations/defaults for ID, status, floor, nullable heaps and capacity.
Smoke check: Elevator('E1', 500) raises TypeError (no __init__); Elevator() lacks
ID/capacity attributes because annotations alone do not initialize them. Heap
values are None rather than usable per-instance lists. Remaining required state:
direction, door state, current kg, duplicate sets, onboard passengers and
passenger-to-destination mapping. If choosing a dataclass, required fields must
precede defaults and mutable collections require field(default_factory=...).
No solution edits or permanent tests; learner corrects constructor first.

## Authorized Elevator constructor

At explicit learner request, replaced the plain annotated Elevator shell with
an __init__(elevator_id, max_load_kg). Initializes IDLE status/direction, floor 0,
closed doors, zero load, independent UP/DOWN heaps and duplicate sets, onboard
passenger lookup and passenger-destination lookup. Rejects nonpositive/nonfinite
maximum weight. Constructor smoke checks verified initial state, separate
collections across instances, invalid capacities, and diff formatting. No
movement/dispatch behavior or permanent tests added. Next: review this state,
then derive stop-add/remove helpers before the movement state machine.

Latest learner direction: continue the existing scope; assess essential versus
extra requirements for a 90-minute round at the end, rather than reducing scope
now. Next implementation checkpoint is stop insertion with directional heaps
and duplicate sets, before movement/boarding/system orchestration.

## Authorized Elevator behavior implementation

Learner explicitly requested a full Elevator implementation and research after
bottom-up helper design became confusing. Implemented behavior-first operations:

- assign_pickup(passenger, floor, direction): accepts assigned waiting passenger;
  validates floor/direction, duplicate assignment and feasible positive weight.
- select_destination(passenger_id, floor): requires onboard passenger, one
  destination, and travel consistent with their requested direction.
- step(): opens at an existing same-floor service stop OR moves at most one
  floor/open on arrival OR services already-open doors. No sleeps. Waits when
  an onboard passenger still needs to select a destination.
- snapshot(): immutable view of car state, stop floors and passenger IDs.

StepResult reports boarded/reached/waiting IDs. Capacity-refused passengers stay
WAITING and are removed from this car's assignment; ElevatorSystem must retain
and reassign them from its global passenger/request records. Exiting precedes
boarding, which tries assigned passengers in acceptance order and skips those
who do not fit. Decimal-from-string arithmetic avoids fractional kg boundary
errors; public load is displayed as a float. Local methods share a car lock;
whole-system atomic dispatch is still to implement.

Stop heaps/sets are derived route indexes rebuilt after request/position changes
from authoritative pickup/destination maps. This intentionally favors simple
consistency over incremental O(log s) updates for a small simulated building.
Current-floor service is handled separately from heaps. Direction continues
while stops remain ahead, reverses for work behind, and becomes idle without
work. At a terminal pickup, approach direction can switch to requested direction
before boarding (e.g. DOWN from 7 to collect an UP passenger at 3).

Added six focused tests: seven-step ride and wait-for-destination; downward
approach/upward passenger; shared stops and directional reversal; capacity refusal
and drop-off-before-boarding; fractional load/invalid requests/snapshot stability;
and concurrent duplicate assignment. All six passed; git diff --check passed.
Original unfinished _add_stop draft was replaced by the implemented contract.
This is mentor-written code/tests at explicit request, not independent readiness.

## Top-down versus bottom-up: researched interview guidance

Reviewed these primary sources on 2026-11-07; not an exhaustive internet survey:

- Microsoft technical interviewing: https://careers.microsoft.com/v2/global/en/hiring-tips/technical-interviewing
  Emphasizes clarification, planning before implementation, and testing.
- Amazon SDE II preparation: https://www.amazon.jobs/content/en/how-we-hire/sde-ii-interview-prep
  Emphasizes questions that validate design, practical trade-offs, working code,
  edge cases and tests; does not mandate a top-down/bottom-up label.
- Cornell CS2110 design lecture, slides 29-31:
  https://www.cs.cornell.edu/courses/cs2110/2013sp/L04-Software%20Design%20Principles%20I/L04cs2110sp13.pdf
  Describes big-picture decomposition and bottom-up experimentation; neither
  approach is universally superior and alternating can expose missed details.

Recommendation (our synthesis, not an official company rule): lead an LLD
interview top-down through requirements, happy flows, public contracts and
ownership, then implement/test one vertical slice using small helpers as needed.
Do not equate top-down reasoning with writing an entire abstract architecture
up front, or bottom-up coding with poor design. Our earlier mistake was starting
stop helpers before making the Elevator's caller-facing contract clear. The
research conclusion does not claim all companies use identical LLD formats.

## Learner-requested scope reset: compact interview solution

Learner found the detailed version too heavy for a machine-coding round and
explicitly requested a smaller implemented solution. Added interview_elevator.py
and INTERVIEW_SCOPE.md as the primary path without overwriting the earlier
reference. Public API: request(source,destination), step(), check(request_id),
snapshot(). Per-car FIFO deque of complete RideRequest records; status dictionary
uses the same records, and check returns a detached copy. Idle-first,
direction/proximity-aware dispatch; FIFO complete rides, no intermediate pickup
batching. Derived direction prevents inconsistent direction fields. One system
Lock serializes public operations; no background threads. On arrival, board or
complete the active ride. Single-floor movement per tick, no separate door ticks.
No kg/passenger model, separate hall/cabin calls, or capacity handling in this
explicitly reduced attempt. Full original requirements are not claimed complete.
Six focused pytest tests passed: movement/status, pickup-before-dropoff/FIFO,
idle/distance/ID tie assignment, direction preference, invalid inputs/detached
status, concurrent unique IDs/eventual completion. Diff check passed.
Code and tests were mentor-written at explicit request; no independent readiness
claim. Next: explain the smaller flow before adding extensions.
