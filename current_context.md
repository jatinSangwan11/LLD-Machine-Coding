# Current Engineering Context

Last updated: 2026-09-23

## Active Session Note

Problem 03: Vending Machine is now the active interview exercise at the
requirements-clarification stage. Its empty project scaffold lives at
`problems/03_vending_machine`; no design, public API, implementation, or tests
have been chosen yet. The learner's first assignment is to ask requirement
questions that materially affect the design and then narrate one successful
purchase flow in plain language.

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
