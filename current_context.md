# Current Engineering Context

Last updated: 2026-10-16

## Active Session Note

Resumed after a break on 2026-10-16. The checkpoint is unchanged: vending-
machine requirements and responsibility design are complete, entity skeletons
exist, but no purchase behavior or tests are implemented. Resume with the first
learner-written end-to-end test for a ₹35 product purchased using two ₹20
insertions with ₹5 change. The learner still owns all implementation and test
writing unless they explicitly ask Codex to write code.

After returning, the learner implemented initial VendingSlot,
PurchaseTransaction, selection, and cash-insertion logic and explicitly asked
Codex to implement `CashInventory.find_change`. Codex added a non-mutating,
bounded backtracking search that combines committed and incoming denomination
counts; direct checks cover ordinary change, use of incoming cash, no solution,
zero change, and a case where greedy selection fails. The repository pytest
runner is available, but the vending-machine test module still contains no
tests. Remaining learner-owned correctness fixes include the inverted product
lookup, invalid dictionary operations in `record_cash`, missing `items()` in
the total calculation, stock underflow/return behavior, distinguishing partial
payment from exact payment before dispensing, applying cash and clearing the
transaction after success, and explicit missing-transaction/error handling.

The learner corrected product lookup, slot underflow/product return, cash
recording, and the partial-payment guard. At the learner's explicit request,
Codex then added defensive returned-change validation to `apply_purchase` and
implemented the successful `insert_cash` completion path. Direct checks now
pass for both exact payment and a ₹35 purchase using two ₹20 insertions with ₹5
change: one item is dispensed, cash counts are updated, and the active
transaction is cleared. No-change refund, cancellation, supported-denomination
validation, product listing, construction invariants, explicit result types,
and pytest coverage remain pending.

At the learner's explicit request, Codex added the first behavior-focused
pytest for the ₹35 Coke purchase using two ₹20 insertions and ₹5 change. It
asserts partial-payment progress, the dispensed product, returned change, stock
decrement, final denomination counts, and transaction cleanup. Result: 1 test
passed. Pytest coverage is no longer pending for the happy path; additional
failure-path tests remain pending.

At the learner's explicit request, Codex implemented the unavailable-change
refund branch and its test. When no exact change plan exists, `insert_cash`
returns no product plus a copy of the inserted denominations, clears the active
transaction, and leaves slot quantity and committed CashInventory unchanged.
The full vending-machine suite now has 2 passing tests.

The learner implemented `cancel_transaction`. It rejects cancellation when no
transaction is active, obtains a defensive copy of the inserted denominations,
clears the active transaction, and returns the refund without changing slot
quantity or committed cash. A direct check passed for cancelling after inserting
one ₹20 note. At the learner's request, Codex added focused cancellation
pytest coverage and implemented `view_products`, which returns product ID, name,
price, and an in-stock Boolean without exposing exact quantity. The suite now
has 3 passing tests. Focused pytest coverage for product listing and remaining
validation failures are next.

At the learner's request, Codex also made successful `select_product` return an
explicit dictionary containing the accepted product ID, name, price, and initial
amount due. The existing happy-path test now verifies this public result; the
learner then requested a focused test, so Codex added coverage proving both the
returned selection details and creation of the transaction for the selected
slot. The suite now has 4 passing tests. The core successful purchase flow is
implemented; `view_products` still needs focused test coverage, and the broader
first version still needs validation and failure-path work.

Problem 03: Vending Machine is the active interview exercise. The learner has
clarified product inventory, cash payment, change, refund, failure, transaction,
and concurrency boundaries. Its scaffold lives at
`problems/03_vending_machine`; no design, public API, implementation, or tests
have been chosen yet.

The learner narrated the successful purchase flow and correctly identified
stock validation before payment, denomination-level tracking, exact-change
validation before completion, one-item transactions, rollback on a rejected
purchase, and reset after completion. The answer did not consistently separate
input, decision, state change, and output; it introduced a vague "backend" and
an unnecessary "order," described payment collection as a blocking wait, and
named Unit of Work before persistence or coordination pressure justified it.
The proposed machine states also mix durable states with terminal outcomes:
success and failure are results, while reset is a transition rather than a
state. The next assignment is to rewrite one concrete purchase as a short
stepwise table using input, decision, state change, and output, including one
money insertion and the final commit. Do not design classes or select patterns
yet.

The learner then completed the concrete ₹35 purchase using two ₹20 insertions
in paragraph form. The flow now includes denomination validation, incremental
balance and denomination tracking, detection of overpayment, exact-change
validation, full tender return when change cannot be made, successful inventory
update, and transaction reset. Remaining precision issues: compare the updated
balance only after accepting the denomination; keep inserted tender separate
from the machine's committed cash until success; treat exact-change validation
as a read-only decision before changing inventory or cash; and call the active
concept a transaction rather than an order. The next assignment is to state the
small set of invariants that must hold before and after every operation.

At the learner's explicit request, the interviewer supplied the first-version
invariants: inventory and denomination counts never become negative; the active
balance equals the sum of its inserted denominations; inserted tender remains
separate from committed machine cash until success; a failed or cancelled
transaction leaves committed product and cash state unchanged; a successful
transaction decrements exactly one item and conserves cash across payment and
change; and returning to idle clears all customer-specific transaction state.
This was direct assistance rather than an inferred learner result. The next
step is behavior-based entity and responsibility identification.

On the second day, the learner proposed Product, Machine, an internal Payment
System, and a cash slot/deposit as candidate entities. Product and Machine are
useful candidates, although Machine must coordinate rather than absorb every
rule. "Payment System" is too vague for the clarified cash-only scope: the
design needs to distinguish temporary customer tender from the machine's
committed denomination inventory. A physical cash input slot is outside the
software-only scope; a cash-inventory object is relevant instead. The proposal
also lacks an owner for per-slot product, quantity, and capacity, and an owner
for the active transaction's selected item and inserted denominations.

The learner explicitly requested that the interviewer not provide questions or
hints unless asked. Future turns should give direct evaluation and only the
requested next material; do not append unsolicited Socratic prompts or extra
assignments.

The learner now understands the candidate responsibility split: Product owns
product information, VendingSlot owns capacity and stock, PurchaseTransaction
owns temporary customer selection and tender, CashInventory owns committed
denominations and change availability, and VendingMachine coordinates the use
case. The learner also understands the difference between a read-only decision
and a stored state change. The current stage is public-interface contract
design. The customer-facing operations are `view_products`, `select_product`,
`insert_cash`, and `cancel_transaction`; the next work is to specify each
operation's input, successful result, failures, and state effect before choosing
internal methods or writing code.

The learner drafted all four public contracts. `view_products` is correctly
read-only. In `select_product`, transaction creation belongs under state change,
while the result should report the accepted selection, price, and amount due;
unknown product, sold-out product, and an already-active transaction are the
failure cases. In `insert_cash`, underpayment returns progress, while sufficient
payment may complete the purchase; state changes can affect the active tender,
slot quantity, committed cash inventory, and active-transaction reference.
Unsupported denomination and missing active transaction are explicit failures,
and inability to make change refunds the tender and clears the transaction. In
`cancel_transaction`, no product ID is required because the active transaction
already owns the selection; success returns the recorded tender and clears the
transaction, while no active transaction is the failure. Customer-facing
availability means an in-stock Boolean rather than exposing exact quantity.

The learner asked for a sharper distinction between responsibilities, internal
method steps, and contract-level state changes. A responsibility describes what
an object owns; internal steps describe how one invocation performs its work;
a state change is the remembered before/after effect of that invocation. Each
`insert_cash` call records one accepted denomination and either returns payment
progress, commits a purchase, or refunds and clears the transaction when exact
change is unavailable. Cancellation transitions the machine from an active
transaction to idle, returns the exact uncommitted tender, and leaves slot stock
and committed cash inventory unchanged. Cancelling without an active
transaction is an explicit failure with no state change.

The public contracts are now precise enough to move into object relationships
and ownership. The intended next stage is to model which objects contain or
reference the others, while keeping coordination in VendingMachine: the machine
owns its slot collection, committed CashInventory, and optional active
PurchaseTransaction; each VendingSlot references its Product; the transaction
references the current selection and owns temporary denomination counts. There
is no direct Transaction-to-CashInventory collaboration because the machine
coordinates validation and commit. Internal method design and implementation
remain pending.

The learner requested a more natural pair-programming and mentoring style aimed
at transferable interview intuition rather than receiving a completed model up
front. The interviewer acknowledged that it had drifted into presenting fully
formed entity specifications. From this point, teaching should follow one
concrete behavior at a time: attempt the simplest design, expose a specific
ownership or correctness problem, introduce the smallest useful concept, test
it, and only then name a principle or pattern. Avoid pre-populating UML,
methods, abstractions, or edge cases before behavior creates pressure for them.
The learner still prefers no unsolicited questions or hints. `Product` has been
treated as immutable descriptive information; the current focus is deriving
`VendingSlot` naturally from the need to own and protect quantity and capacity.

The learner further requested that every entity or abstraction be taught by
contrasting it with the simpler design it replaces. For each future concept,
explicitly cover a concrete example, the bottleneck or correctness risk in the
naive design, why the responsibility does not fit an existing object, the
specific pressure relieved by the new object, and the extra complexity or
trade-off introduced. This comparison is part of building transferable
intuition and should precede final class or method shapes.

`VendingSlot` has now been justified by contrasting it with storing quantity on
Product or manipulating inventory directly in VendingMachine. Product owns
stable descriptive data, while a slot owns frequently changing, location-level
quantity and capacity and protects `0 <= quantity <= capacity`. The additional
object is justified by independent slot inventory and capacity. The next entity
being derived is `PurchaseTransaction`, motivated by the separate lifecycle of
one customer's temporary selection and inserted tender versus the long-lived
machine and its committed cash.

The first PurchaseTransaction explanation moved too quickly and was not
understood. Restart this concept from a beginner-level concrete example. First
show a working VendingMachine-only version with current selection and inserted
notes stored directly on the machine. Then expose only the practical problem:
every success, cancellation, or refund must clear several customer-specific
fields, and temporary inserted notes can be confused with the machine's own
cash. Explain extraction as grouping those temporary values behind one
`current_transaction` field that can be discarded as a whole. Do not discuss
transaction methods, formal terminology, or further abstractions until this
single motivation is understood.

The learner now understands that motivation: the VendingMachine-only version is
valid initially, but grouping one customer's selection and inserted notes in a
PurchaseTransaction prevents forgotten cleanup and keeps temporary tender
separate from machine-owned cash. The current step is to derive the
transaction's minimal responsibility, data, and behaviors from the ₹35 Coke
example, without letting it modify slot inventory, permanent cash, or the
overall machine flow.

PurchaseTransaction has now been derived as the temporary owner of the selected
slot and inserted denomination counts. Its balance, remaining amount, and
required change are calculated rather than duplicated as stored fields. It does
not own quantity: the selected VendingSlot owns quantity and references the
Product that supplies price. One VendingMachine owns multiple VendingSlots. The
next object being derived is CashInventory, using the fact that a total cash
amount is insufficient to prove that exact change can be formed.

CashInventory has now been derived as the owner of committed denomination
counts. A total amount is insufficient because equal totals can have different
change-making ability. `find_change(required_amount, incoming_cash)` performs a
read-only bounded combination search and returns a denomination plan or none;
it must not rely solely on greedy selection because limited denominations can
require backtracking. `apply_purchase(incoming_cash, returned_change)` performs
the permanent denomination update after validation. The next step is to return
to VendingMachine and derive its coordination role across the now-understood
objects.

The learner set Amazon, Stripe, and Google as the target bar for this machine-
coding preparation. Evaluate future work for executable correctness, precise
money and state handling, realistic failure coverage, readable and testable
code, clear trade-off explanations, and the ability to adapt the working design
to requirement changes. SOLID principles and patterns should emerge from real
change pressure rather than being inserted as checkboxes. Add concurrency,
thread safety, and atomicity as an explicit later extension after the sequential
core is correct, including race analysis and concurrent tests.

The learner explicitly owns all implementation and test writing for this
problem. The interviewer must not create, edit, or supply solution code unless
the learner directly asks for it. The interviewer may explain concepts, define
the next bounded behavior, inspect and review learner-written code, diagnose
failures, and provide progressive help only when requested. Testing should be
focused on meaningful observable behavior without ceremonial or excessive
cases; it remains part of the machine-coding standard.

The learner explicitly requested one implementation exception: scaffold all
entity classes in `src/vending_machine/dispenser.py` without implementing the
VendingMachine happy path. The file now imports cleanly and contains Product,
VendingSlot, PurchaseTransaction, CashInventory, and VendingMachine attributes
and method signatures. Product retains the learner's positive-price validation;
other behavior raises `NotImplementedError`. No purchase-flow logic or tests
were added. The learner resumes ownership of all method implementations.

End-of-day checkpoint: requirements, the concrete purchase flow, key
invariants, entity motivations, responsibility boundaries, customer-facing
operations, object relationships, and code skeleton are complete. Executable
behavior is not yet implemented. Next session should begin with one focused
end-to-end test for a ₹35 product purchased using two ₹20 insertions with ₹5
change, followed by the minimum learner-written implementation needed to pass
it. Later work remains: cancellation and failure behavior, exact bounded change
search, broader tests, evidence-driven refactoring, a requirement-change
exercise, and the concurrency/atomicity extension.

The detailed Problem 02 context below is intentionally retained as the handoff
for the paused Job Scheduler exercise. Problem 01: Parking Lot also remains
paused and unchanged.

## Current Problem

Problem 02: Job Scheduler. Design an in-memory, single-process scheduler that
accepts one-time and fixed-interval jobs and dispatches due work to concurrent
workers.

Problem 01: Parking Lot remains in the repository and is paused; its code and
tests have not been changed by this session.

## Current Stage

Requirements and the initial happy path are clarified. One-time registration,
time ordering, automatic condition-based waiting, due-time detection, executor
delegation, successful and failed execution, and explicit lifecycle are
implemented. Unknown job lookup and invalid post-shutdown operations now expose
scheduler-specific exceptions. A real `ThreadPoolExecutor` can be injected;
retries and recurrence are pending.

## Requirements

- Support one-time jobs scheduled for a timestamp.
- Support recurring jobs scheduled at a fixed interval.
- Return a unique job ID after valid submission.
- Treat a past timestamp as immediately eligible.
- Treat scheduled time as eligibility time rather than an exact-start promise.
- Consider due work by scheduled timestamp and then submission order.
- Execute different jobs concurrently through workers.
- Prevent concurrent duplicate execution of the same scheduled occurrence.
- Allow cancellation and status queries.
- Allow recurring jobs to be paused and resumed without interrupting an
  already-running occurrence.
- Retry failures using a configurable attempt limit and delay. A retry becomes
  eligible at failure time plus retry delay and has no worker affinity.
- Isolate job failures from the scheduler and other jobs.
- Keep the first version in memory and within one process.
- Make shared operations thread-safe and handle tens of thousands of scheduled
  jobs efficiently.
- Use best-effort timing and keep scheduling and retry behavior extensible and
  testable.
- Exclude persistence, restart recovery, distributed execution, cron syntax,
  priorities, dependencies, and client notifications.

## Open Requirement Decisions

- Whether separate occurrences of one recurring job can overlap.
- Whether status belongs to the job definition, individual occurrences, or
  both.
- How pause/resume treats recurring occurrences missed during the pause.

## Current Architecture

The current first-pass architecture has an executable `IJob`, a stored `Job`
record, a coordinating `JobSchedular`, a job-ID dictionary, a `heapq` min-heap,
an injected `Clock`, an injected `JobExecutor`, one dispatcher thread, and a
condition variable protecting and signaling shared scheduling state. The
scheduler owns timing and dispatch decisions; the executor boundary owns
running submitted callables. Retry and recurring abstractions remain
provisional and unused.

The learner correctly identified the need for two different access patterns:
constant-time lookup/control by job ID and time-ordered retrieval of the next
eligible execution. A dictionary can serve the first access pattern but cannot
efficiently serve the second by itself.

The narrated happy path is:

1. A client submits executable work, a schedule, and retry configuration.
2. The scheduler validates the request, assigns an ID, stores the scheduled
   entry, and returns the ID.
3. When the entry is due, it is dispatched to an available worker.
4. The worker executes the work and reports success or failure.
5. Success is recorded; recurrence may create a future occurrence.
6. Failure is recorded and may create a retry eligible after its retry delay.

The key modeling question currently posed to the learner is whether a recurring
job definition and one concrete scheduled execution should be different
objects.

## Implementation Status

The implementation creates and retrieves scheduled records, pushes
`(run_at, submission_sequence, job_id)` entries into a min-heap, and peeks the
earliest job without removal. `dispatch_next_due_job` compares the earliest
job's time against the injected clock, leaves future work queued, or pops due
work and submits an execution wrapper. The wrapper calls the client job, marks
it successful, or catches an ordinary `Exception`, marks it failed, and retains
the original exception as `last_error`. `SystemClock` supplies current UTC time;
tests use a fixed clock and immediate recording executor.

`start` creates one daemon dispatcher thread. The dispatcher waits on the
condition when the heap is empty, performs a timed wait for future work, and
rechecks the heap after notification. `schedule` updates dictionary and heap
under the same condition lock and notifies the dispatcher. `shutdown` stops and
joins the dispatcher and transfers shutdown to the owned executor. A
`functools.partial` supplies a zero-argument callable that retains the scheduled
job for later execution.

The current slice intentionally omits retries, recurrence, and cancellation.
Existing cleanup remains: scheduler/file spelling, duplicate
scheduling time inside one-time/recurring executable subclasses, and the unused
global retry policy.

`JobSchedulerError` is the base for scheduler API failures.
`JobNotFoundError` translates an internal dictionary `KeyError` into a meaningful
API error, while `SchedulerShutdownError` rejects scheduling or restarting after
shutdown. Client-job execution exceptions are not converted into these API
errors; they are retained on the failed job.

## Current Implementation Assignment

Review the small failure-state implementation and then pause feature work for a
one-hour, interview-focused Python data-structure revision. Resume with retry
eligibility only after the learner can explain the failure transition. Do not
add recurrence yet.

## Current Blocker

None.

## Mistakes And Corrections

- The first summary assigned retry orchestration to a worker. Clarified that a
  worker executes one attempt and reports its result; scheduler-side policy
  decides whether and when another attempt becomes eligible.
- Pause/resume was initially described as applying to any job execution.
  Clarified that it controls future recurring executions and does not interrupt
  work already running.
- Client notification was mentioned in the happy path even though only status
  queries are required. Notification remains out of scope.
- The first code sketch annotates `job_queue` but does not initialize it and
  calls `generate_job_id(job)` even though the method accepts no job argument.
- One-time versus recurring behavior was placed in subclasses of executable
  work before checking whether recurrence belongs to the work or its schedule.
- The first scheduled-record attempt used an invalid callable annotation,
  time-of-day instead of a timestamp, positional arguments in the wrong order,
  and an uninitialized dictionary. These were identified before adding queue or
  worker behavior.
- The registration flow introduced an artificial Boolean result from
  `add_job()` even though no failure behavior exists. This makes `schedule()`
  optional without a defined reason; use explicit exceptions when real
  validation failures are introduced.
- `get_job` was initially used as a pre-insertion existence check and accepted
  a whole job object. Clarified that ID lookup is needed after registration for
  status and control operations; duplicate-ID detection, if retained, should
  check dictionary membership directly.

## Concepts Encountered

- Requirement notes organized as use cases, behavioral rules, constraints, out
  of scope, and open questions.
- Scheduled time means eligibility time; available worker capacity can delay
  actual execution.
- Submission order breaks ties when scheduled timestamps match, but concurrent
  execution means completion order is not guaranteed.
- A retry is another attempt of one scheduled occurrence, not a new logical job.
- Record design decisions rather than transcribing the whole interview.
- Different retrieval needs can justify coordinated data structures: a mapping
  for job-ID lookup and a time-ordered structure for next-due retrieval.
- A worker pool can own worker availability; the scheduler can submit due work
  rather than model and search individual idle workers.
- Dependency injection separates production infrastructure from deterministic
  tests: production can supply `SystemClock` and a thread-pool executor, while
  tests supply `FixedClock` and `ImmediateExecutor`.
- A zero-argument callable can be handed to an executor for later execution. A
  lambda captures the scheduled job and delays the private execution-method
  call until the executor invokes it.
- Test doubles make boundaries observable: the fixed clock controls time, the
  immediate executor records delegation and runs synchronously, and the
  recording job counts executions.
- A fixed `sleep` until the current earliest deadline is incorrect because a
  concurrent submission can introduce an earlier deadline. A condition
  variable combines protected access to the heap with interruptible waiting:
  `schedule` notifies the dispatcher, which wakes and recalculates its wait.

## Patterns Encountered

None. Retry has appeared as required behavior, but no pattern or abstraction has
been selected or implemented.

## SOLID Principles Encountered

None.

## Hints Used

- Direct assistance — Vending Machine invariants: supplied the complete
  first-version invariant set after the learner explicitly requested it.
- Level 1 — Requirements organization: provided the five-box note-taking
  framework and a compact job-scheduler example after the learner requested a
  way to manage cognitive load.
- Level 1 — Interview sequencing: suggested summarizing scope, narrating one
  happy flow, and deriving responsibilities before implementation.
- Level 2 — Scheduling mechanism: explained the separate lookup and time-order
  access patterns and pointed toward a min-heap plus worker-pool boundary after
  the learner explicitly asked how time-based dispatch should work.
- Level 3 — Scheduled record: after the learner remained blocked, identified
  the missing record that groups job ID, executable task, run time, and status,
  and narrowed the next assignment to one test-driven registration behavior.
- Level 2 — Heap ordering: explained lexicographic tuple comparison, submission
  sequence as a deterministic integer tie-breaker, and the difference between
  `heap[0]` peek and `heappop` removal after the learner attempted the queue.
- Level 3 — Threading foundation: explained threads, thread pools, locks, and
  condition-variable wait/notify behavior from first principles after the
  learner stated they had no prior threading experience.

## Tests Written

Nine pytest tests cover registration, unknown-ID rejection, post-shutdown
scheduling rejection, earliest-job peek, manual due dispatch,
leaving future work scheduled, automatic dispatch after an empty-queue wait,
waking for a newly earlier job, and recording a failed execution with its
original error. Result: 9 passed.

## Next Action

Give the learner a compact Python data-structure revision for the imminent
interview. When implementation resumes, ask them to explain why `_execute_job`
uses `try`/`except`/`else`, then add retry eligibility as the next behavior.
