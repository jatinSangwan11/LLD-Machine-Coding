# LLD Learning Progress

Last updated: 2026-09-09

## Current Readiness

Problem 01 is in progress. The parking-entry flow now handles compatible-spot
selection, unavailable parking, duplicate entry, multiple floors, stable
floor/spot ordering, typed vehicle categories, ticket creation time, and active
ticket storage. Codex wrote the initial happy flow and corrected mechanical
issues in the new ticket contract; the learner identified the need for the
ticket object, enum, entry time, and ticket lookup. Scores use a 1–5 scale and
require observable learner work.

Immediate target: practical interview readiness by Friday, 2026-09-11 at
12:00 PM IST. Preparation is temporarily fast-tracked; breadth that does not
materially improve Friday's performance remains on the post-interview roadmap.
After the Friday interview, resume the original long-term learning pace and full
coverage goals. The temporary deadline changes prioritization only; it does not
replace or narrow the repository's overall objective.

Full-roadmap target: 2026-09-30. By that date, aim to complete practical,
problem-driven coverage of all five SOLID principles and all listed design and
engineering patterns. Completion requires implementation/refactoring, tests,
and trade-off discussion rather than name recognition alone.

| Skill | Score | Evidence |
| --- | ---: | --- |
| Requirements and clarification | 3/5 | Asked relevant questions with a Level 1 scaffold and summarized the core lifecycle; missed several rules and scope boundaries |
| Responsibility splitting | 3/5 | Explained that `park()` controls the entry workflow while `_find_available_spot()` owns spot selection; still needs practice making these splits independently |
| Design and interfaces | Not assessed | No attempt yet |
| Python implementation | 2/5 | Extended the solution with guided changes and independently recognized that exit requires a ticket contract, entry time, enum, and stored tickets; still needs help converting the design into correct Python |
| Testing | 2/5 | Added tests for earlier behaviors and used a failure to expose spot-order dependence; ticket-time and ticket-storage tests were added by Codex; 8 tests pass |
| Extensibility and refactoring | Not assessed | No attempt yet |
| Design explanation and defense | 2/5 | Can explain the current parking workflow and why floors/spots are separate, but still needs prompts to identify the next bottleneck |

## Completed Problems

None.

## Attempted Problems

### Problem 01: Parking Lot — in progress

- Current stage: parking-entry behavior and active-ticket storage complete; exit
  flow has been sketched but is not implemented
- Requirements/clarification: 3/5 (provisional)
- Responsibility splitting: 3/5 (provisional)
- Implementation: the minimal `park()` flow supports multiple floors, compatible
  spot types, duplicate-entry rejection, occupancy updates, ticket creation, and
  deterministic lowest-floor/lowest-spot-ID selection. It now returns an
  `EntryTicket` containing an enum category and entry time, and stores that
  ticket by ID for later exit lookup
- Tests: 8 pytest tests pass
- SOLID: SRP has been introduced through the `park()` and
  `_find_available_spot()` responsibility split, but it has not yet earned
  completed coverage through a pressure-driven refactor
- Patterns: none encountered yet
- Next behavior: implement the simplest successful exit flow for a valid active
  ticket and make its parking spot available again

## Reusable Interview Framework

Planned after completing the Parking Lot iterations. It will capture the method
we actually practiced: clarify the behavior, trace one happy flow, write a
failing test, implement the smallest change, find the next real bottleneck,
split responsibilities when the code demands it, and explain trade-offs. The
framework should be usable as a timed checklist during later mock interviews.

## Pattern Coverage

No patterns have been encountered yet.

### Creational

- [ ] Factory Method
- [ ] Abstract Factory
- [ ] Builder
- [ ] Prototype
- [ ] Singleton

### Structural

- [ ] Adapter
- [ ] Bridge
- [ ] Composite
- [ ] Decorator
- [ ] Facade
- [ ] Flyweight
- [ ] Proxy

### Behavioral

- [ ] Strategy
- [ ] Observer
- [ ] Command
- [ ] State
- [ ] Chain of Responsibility
- [ ] Template Method
- [ ] Iterator
- [ ] Mediator
- [ ] Memento
- [ ] Visitor
- [ ] Interpreter

### Practical Engineering

- [ ] Dependency Injection
- [ ] Repository
- [ ] Service Layer
- [ ] Specification
- [ ] Null Object
- [ ] Unit of Work
- [ ] State Machine
- [ ] Retry
- [ ] Circuit Breaker
- [ ] Event-driven design

Checking an item means the pattern arose in implementation or refactoring and
its benefit and trade-offs were discussed. Merely mentioning it does not count.

## SOLID Coverage

- [ ] Single Responsibility Principle (SRP)
- [ ] Open/Closed Principle (OCP)
- [ ] Liskov Substitution Principle (LSP)
- [ ] Interface Segregation Principle (ISP)
- [ ] Dependency Inversion Principle (DIP)

Checking an item requires an encountered design smell, a learner-led refactor,
and tests of the result.

SRP has been discussed using the current workflow/helper split. It remains
unchecked until a real code bottleneck leads to a tested refactor.

## Repeated Mistakes

None observed.

## Current Weaknesses

Not assessed.

## Hints Used

- Problem 01, Level 1: reusable clarification-question framework; first prompt
  focused on supported vehicle and parking-spot types.
- Problem 01, Level 1: operation-tracing framework for beginning domain modeling.
- Problem 01, Level 2: behavior-first happy-path modeling after the learner
  correctly challenged mechanical noun/verb extraction.
- Problem 01, Level 3: responsibility assignment explained through the
  information-owner rule and parking allocation example.

## Session History

### 2026-09-09 — Parking-entry flow

- Implemented the minimal successful `park()` flow with compatible-spot search,
  occupancy update, and ticket creation.
- Added failure handling for no compatible spot and duplicate active vehicle
  registration.
- Changed configuration to contain floors and their spots, then returned both
  the selected spot and its floor from the search helper.
- Made selection independent of caller-provided order by sorting floors and
  spots once during initialization.
- The learner recognized that exit requires a clearer ticket contract, vehicle
  enum, recorded entry time, and a way to retrieve active tickets by ID.
- Corrected the new contract's mechanical Python issues: dictionary storage,
  tuple-producing comma, missing entry time, enum consistency, and typed ticket
  construction.
- Added tests for successful parking, no compatible spot, duplicate entry,
  floor-based configuration, lowest-floor selection, and lowest-spot-ID
  selection, plus entry-time recording and active-ticket lookup; result: 8
  passed.
- The learner implemented several guided changes and tests. Codex wrote the
  initial happy flow and the final spot-sorting change.

### 2026-09-08 — Repository setup

- Initialized the interview-preparation structure and mentoring guidance.
- Preserved the pre-existing `OOPS/recap.py` file.
- Did not start or score a problem.

## Next Recommended Problem

Continue Problem 01 with the smallest successful exit behavior: give the system
a valid active ticket, close it, and make its occupied spot available again.
Add invalid-ticket, already-closed-ticket, time/fee, and concurrency behavior one
at a time after the happy exit path works.
