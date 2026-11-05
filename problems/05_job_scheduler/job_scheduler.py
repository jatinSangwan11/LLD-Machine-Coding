import heapq
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum, auto
from itertools import count
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
    """Run one-time jobs in a fixed worker pool. Call shutdown when done."""

    def __init__(self, max_workers: int = 1) -> None:
        if max_workers < 1:
            raise ValueError("max_workers must be at least 1")

        self._condition = Condition()
        self._pending: list[tuple[datetime, int]] = []
        self._jobs: dict[int, _Job] = {}
        self._job_ids = count(1)
        self._shutdown_requested = False
        self._workers = [
            Thread(target=self._worker_loop, name=f"job-scheduler-{i}", daemon=False)
            for i in range(1, max_workers + 1)
        ]
        for worker in self._workers:
            worker.start()

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
            # Wake idle workers so they can recompute their next deadline.
            self._condition.notify_all()
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
            # Wake every idle worker so it can drain jobs or exit.
            self._condition.notify_all()

        # Join outside the lock so workers can finish updating job statuses.
        for worker in self._workers:
            worker.join()

    def _take_due_job(self) -> _Job | None:
        """Wait for a due job, then mark it running before releasing the lock."""
        with self._condition:
            while True:
                if not self._pending:
                    if self._shutdown_requested:
                        return None
                    self._condition.wait()
                    continue

                scheduled_time, _ = self._pending[0]
                seconds_until_due = (scheduled_time - datetime.now(UTC)).total_seconds()
                if seconds_until_due > 0:
                    self._condition.wait(timeout=min(seconds_until_due, TIMEOUT_MAX))
                    continue

                _, job_id = heapq.heappop(self._pending)
                job = self._jobs[job_id]
                job.status = JobStatus.RUNNING
                return job

    def _worker_loop(self) -> None:
        while True:
            job = self._take_due_job()
            if job is None:
                return

            # The helper has released the lock. User code may take a long time.
            try:
                job.action()
            except Exception as exc:
                # A callback that raises SystemExit must not kill the worker either.
                status = JobStatus.FAILED
                try:
                    message = f"{type(exc).__name__}: {exc}"
                except Exception:
                    message = type(exc).__name__
            else:
                status = JobStatus.SUCCEEDED
                message = "Job completed successfully"

            with self._condition:
                job.status = status
                job.message = message
