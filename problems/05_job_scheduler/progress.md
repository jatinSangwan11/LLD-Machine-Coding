# Job Scheduler Progress

Last updated: 2026-11-05

- Stage: Deadline dispatcher and ready queue implemented at learner request
- Source: Mentor-authored exercise from the original curriculum
- Mode: Interviewer; learner drives the design and implementation; no timer started
- Implementation: Mentor wrote `job_scheduler.py` at explicit request
- Tests: Manual assertions passed; no permanent tests added yet
- Assistance: Worker-loop pseudocode and full implementation supplied

## Interview brief

Implement an in-memory Python scheduler for one-time jobs. A caller submits
a callable and the earliest time it may run, and receives an ID for checking
its status. The scheduler runs due jobs one at a time, in scheduled-time order,
and never starts a job early. Each job gets at most one attempt; a job failure
must be visible and must not prevent later jobs from running. Jobs can run late
if another job is still executing. The initial baseline used one worker; the
learner later requested the worker-pool extension below. Recurring jobs,
retries, and persistence remain outside scope.

## Clarifying questions

1. **How many workers execute jobs?** One by default. After the worker-pool
   upgrade, `max_workers` sets the limit. A due job waits if all workers are busy.
2. **Do jobs run automatically or does the caller trigger processing?** Jobs
   run automatically. The scheduler starts its worker pool when created; callers
   submit jobs and do not need to poll or trigger execution.
3. **What time does a caller supply? What if it is in the past?** Supply an
   absolute, timezone-aware Python `datetime`. Compare times by instant. A
   past or current time makes the job eligible immediately, but it still waits
   its turn. Its original scheduled time determines its priority.
4. **What if two jobs have the same scheduled time?** FIFO by acceptance
   order when workers claim jobs. This also defines a tie-breaker when callers
   submit concurrently. With multiple workers, actual callback start and
   completion order are not guaranteed.
5. **What can callers see about a job?** Look up its status by ID: `PENDING`,
   `RUNNING`, `SUCCEEDED`, or `FAILED`. A failed job includes a
   short error message. No result retrieval or automatic retry is required.
6. **What happens on shutdown?** Stop accepting new submissions and finish
   every accepted job. Pending jobs still respect their scheduled times. Shutdown
   waits for all workers to exit after the queue drains. Status lookup still works.
   The learner chose this policy in place of the original cancel-pending policy.
7. **Can callers submit jobs or check status while a job is running?** Yes.
   Multiple callers may submit and query concurrently; execution is limited to
   the configured pool size. A running job must not block submission or lookup.

## Next action

Learner traces `submit_job` → `_dispatch_loop` → ready queue → `_worker_loop`,
then writes focused tests and explains the lock boundaries. Parking Lot's final
review remains separate. Independent scheduler implementation is not demonstrated.

## Design checkpoint

- Proposed API: `submit_job(callable_func, time_when_to_run)` returns a job ID;
  `check_status(job_id)` returns a snapshot and raises `KeyError` for unknown IDs;
  `shutdown()` drains pending jobs and waits for the worker to finish.
- State transitions: `PENDING` to `RUNNING`, then `SUCCEEDED` or `FAILED`.
  Due jobs stay pending until the worker starts them.
- Learner proposed a min-heap keyed by `(scheduled_time, sequence_number, job_id)`
  and a `Condition`. Use timed waits for deadlines and notifications for new
  submissions or shutdown. Job records are indexed by ID.
- Pseudocode review: peek before popping, mark `RUNNING` before execution,
  execute outside the lock, and write `SUCCEEDED` only on the success path.

## Implementation checkpoint

One worker owns the execution loop; `_take_due_job` waits and claims a job, then
returns with the lock released. `_worker_loop` calls the action, sets the result
via `try`/`except`/`else`, and publishes it under the lock. Increasing job IDs
also serve as FIFO sequence numbers, so the heap stores `(utc_time, job_id)`.
Shutdown closes submissions under the lock, keeps the heap intact, and joins
outside the lock. The worker exits when shutdown was requested and the heap is
empty after completing the last job. A callback cannot synchronously shut down
its own worker. Earlier manual checks passed due-time gating, earlier-job
ordering, equal instants/FIFO, failure isolation, invalid time/ID handling, and
concurrent submit/status. New manual checks passed draining running, due, and
future jobs in order, preserving deadlines, continuing after failure, rejecting
new submissions during shutdown, and idle/repeated shutdown. No permanent tests
added; `git diff --check` passed.

## Worker-pool extension

At learner request, added `JobScheduler(max_workers=1)`. A fixed pool of
reusable threads shares one condition, deadline heap, and job table. Each claim
and `RUNNING` transition is atomic; callbacks run outside the lock. Submission
and shutdown use `notify_all()` so idle workers recheck deadlines or exit.
Shutdown joins every worker outside the lock. Manual checks passed overlapping
callbacks with two workers, a queued third job, no early execution, rejection
of submissions during draining, complete pool shutdown, invalid worker counts,
and unchanged FIFO in the default one-worker mode. No permanent tests added.

## Dispatcher and ready-queue extension

At learner request, split deadline scheduling from execution. One dispatcher owns
timed waiting on the heap; workers block on a thread-safe `Queue`. The dispatcher
reserves a free worker slot and marks the earliest due job `RUNNING` under the
condition lock before enqueueing it. With no free slot, jobs stay `PENDING` in
the heap so an earlier submission can still take priority. Worker completion
records the terminal status, returns the slot, and notifies the dispatcher.
Shutdown drains the heap, sends one stop marker per worker from the dispatcher,
and joins the dispatcher and workers outside the lock. FIFO applies to claims,
not callback start/completion order. Manual assertions passed saturation and
priority/FIFO, overlapping execution, no early start, `SystemExit` isolation,
rejected submissions during shutdown, complete drain, and idle/repeated
shutdown. No permanent tests added; `git diff --check` passed.
