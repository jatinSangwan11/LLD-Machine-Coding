# Problem 02: Job Scheduler

Status: Requirements clarified; responsibility modeling next

## Interview Brief

Design a job scheduler that accepts jobs and executes them at their scheduled
times.

Use Python for any later implementation. For now, this problem contains only
the interview scope and an empty project scaffold; no design or implementation
has been chosen.

## Clarified Scope

- A client can schedule a one-time job for a timestamp.
- A client can schedule a recurring job at a fixed interval.
- Submitting a valid job returns a unique job ID.
- A timestamp in the past makes the job eligible immediately.
- The scheduled time is an eligibility time, not an exact-start guarantee.
- Due jobs are considered by scheduled time and then submission order.
- Multiple workers may execute different jobs concurrently.
- The same scheduled occurrence must not execute concurrently more than once.
- A client can cancel a job and query its status.
- A recurring job can be paused and resumed. An already-running execution is
  not interrupted.
- A failed occurrence may be retried according to a configurable maximum
  attempt count and retry delay.
- A retry becomes eligible at `failure time + retry delay` and may run on any
  worker.
- Failure in one job must not stop the scheduler or other jobs.
- The scheduler is single-process, in-memory, thread-safe, and expected to
  handle tens of thousands of scheduled jobs efficiently.
- Timing is best-effort rather than hard real-time.
- Persistence, restart recovery, distributed coordination, cron expressions,
  priorities, dependencies, and client notifications are out of scope.

## Open Requirement Decisions

- Whether separate occurrences of one recurring job may overlap.
- Whether status is exposed for the recurring job definition, its individual
  executions, or both.
- Whether occurrences missed while a recurring job is paused are skipped or
  executed after resume.

## Next Interview Step

Trace the successful one-time-job flow and assign each decision and state
change to a responsible collaborator. Then decide whether a recurring job
definition and one scheduled execution should be represented separately.
