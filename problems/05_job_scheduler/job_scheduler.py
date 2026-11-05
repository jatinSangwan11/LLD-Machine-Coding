import heapq
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum, auto
from itertools import count
from queue import Queue
from threading import TIMEOUT_MAX, Condition, Thread, current_thread


class JobStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    SUCCEEDED = auto()
    FAILED = auto()


@dataclass(frozen=True)
class JobSnapshot:
    job_id: int
    status: JobStatus
    message: str | None


@dataclass
class _Job:
    job_id: int
    action: Callable[[], object]
    status: JobStatus = JobStatus.PENDING
    message: str | None = None


class JobScheduler:
    """Dispatch scheduled jobs to a fixed worker pool. Call shutdown when done."""

    def __init__(self, max_workers: int = 1) -> None:
        if max_workers < 1:
            raise ValueError("max_workers must be at least 1")

        self._condition = Condition()
        self._pending: list[tuple[datetime, int]] = []
        self._jobs: dict[int, _Job] = {}
        self._job_ids = count(1)
        self._shutdown_requested = False
        self._ready: Queue[_Job | None] = Queue()
        self._free_worker_slots = max_workers
        self._workers = [
            Thread(target=self._worker_loop, name=f"job-scheduler-{i}", daemon=False)
            for i in range(1, max_workers + 1)
        ]
        self._dispatcher = Thread(
            target=self._dispatch_loop, name="job-scheduler-dispatcher", daemon=False
        )
        for worker in self._workers:
            worker.start()
        self._dispatcher.start()

    def submit_job(
        self, callable_func: Callable[[], object], time_when_to_run: datetime
    ) -> int:
        if time_when_to_run.utcoffset() is None:
            raise ValueError("Scheduled time must include a timezone")
        scheduled_time = time_when_to_run.astimezone(UTC)

        with self._condition:
            if self._shutdown_requested:
                raise RuntimeError("Scheduler is shutting down")

            # IDs are assigned in acceptance order, so they also break time ties.
            job_id = next(self._job_ids)
            self._jobs[job_id] = _Job(job_id, callable_func)
            heapq.heappush(self._pending, (scheduled_time, job_id))
            # Only the dispatcher waits on the condition; workers wait on Queue.
            self._condition.notify()
            return job_id

    def check_status(self, job_id: int) -> JobSnapshot:
        with self._condition:
            job = self._jobs[job_id]
            return JobSnapshot(job.job_id, job.status, job.message)

    def shutdown(self) -> None:
        """Stop accepting jobs and wait for all accepted jobs to finish."""
        if current_thread() in self._workers:
            raise RuntimeError("A job cannot shut down its own worker pool")

        with self._condition:
            self._shutdown_requested = True
            self._condition.notify()

        # The dispatcher drains the heap and sends the workers their stop signals.
        # Join outside the lock so it and the workers can keep updating state.
        self._dispatcher.join()
        for worker in self._workers:
            worker.join()

    def _reserve_due_job(self) -> _Job | None:
        """Claim the earliest due job when the pool has capacity for it."""
        with self._condition:
            while True:
                if not self._pending:
                    if self._shutdown_requested:
                        return None
                    self._condition.wait()
                    continue

                # Leave waiting jobs in the heap so an earlier job can overtake.
                if self._free_worker_slots == 0:
                    self._condition.wait()
                    continue

                scheduled_time, _ = self._pending[0]
                seconds_until_due = (scheduled_time - datetime.now(UTC)).total_seconds()
                if seconds_until_due > 0:
                    self._condition.wait(timeout=min(seconds_until_due, TIMEOUT_MAX))
                    continue

                _, job_id = heapq.heappop(self._pending)
                job = self._jobs[job_id]
                self._free_worker_slots -= 1
                job.status = JobStatus.RUNNING
                return job

    def _dispatch_loop(self) -> None:
        while True:
            job = self._reserve_due_job()
            if job is None:
                # FIFO puts these behind any jobs already handed off.
                for _ in self._workers:
                    self._ready.put(None)
                return
            self._ready.put(job)

    def _worker_loop(self) -> None:
        while True:
            job = self._ready.get()
            try:
                if job is None:
                    return
                self._run_job(job)
            finally:
                self._ready.task_done()

    def _run_job(self, job: _Job) -> None:
        # No scheduler lock is held while user code runs.
        try:
            job.action()
        except BaseException as exc:
            # A callback raising SystemExit must not kill a pool worker.
            status = JobStatus.FAILED
            try:
                message = f"{type(exc).__name__}: {exc}"
            except BaseException:
                message = type(exc).__name__
        else:
            status = JobStatus.SUCCEEDED
            message = "Job completed successfully"

        with self._condition:
            job.status = status
            job.message = message
            self._free_worker_slots += 1
            self._condition.notify()
