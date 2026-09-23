import datetime
import heapq
import threading
import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from functools import partial
from typing import Protocol


# this is the strategy design pattern 
class RetryPolicyStrategy(ABC):
    
    @abstractmethod
    def retry(self):
        ...

# we will have concrete classes for the strategy but we do not need them as that will be provided by the client
# dependency injection

class IJob(ABC):
    @abstractmethod
    def execute(self):
        ...


class Clock(Protocol):
    def now(self) -> datetime.datetime:
        ...


class SystemClock:
    def now(self) -> datetime.datetime:
        return datetime.datetime.now(datetime.timezone.utc)


class JobExecutor(Protocol):
    def submit(self, task: Callable[[], None]) -> object:
        ...

    def shutdown(self, wait: bool = True) -> None:
        ...


class JobSchedulerError(Exception):
    """Base exception for errors produced by the scheduler API."""


class JobNotFoundError(JobSchedulerError):
    """Raised when a requested job ID is not registered."""


class SchedulerShutdownError(JobSchedulerError):
    """Raised when an operation is not allowed after scheduler shutdown."""

class OneTimeJob(IJob):
    """ 
        it will own the time at which the job to run 
    """
    def __init__(self, run_time) -> None:
        self.execute_at = run_time

    
    def execute(self):
        ...
    
    def get_execute_at(self):
        return self.execute_at

class RecurJob(IJob):
    """ 
        it will own the time at which the job to run 
    """
    def __init__(self, run_time) -> None:
        self.execute_at = run_time

    
    def execute(self):
        ...
    
    def get_execute_at(self):
        return self.execute_at

class JobStatus(Enum):
    SCHEDULED = "scheduled"
    FAILED = "failed"
    SUCCESS = "success"
    WORKING = "working"

@dataclass
class Job:
    job_id: str
    status: JobStatus
    run_at: datetime.datetime
    executable_job: IJob
    last_error: Exception | None = None


class JobSchedular:
    
    def __init__(
        self,
        retry_policy: RetryPolicyStrategy,
        clock: Clock,
        executor: JobExecutor,
    ):
        self.retry_policy = retry_policy
        self.clock = clock
        self.executor = executor
        self.jobs_by_id: dict[str, Job]={}
        self.ordered_queue: list[tuple[datetime.datetime, int, str]] = []
        self.submission_sequence: int = 0
        self.condition = threading.Condition()
        self.dispatcher_thread: threading.Thread | None = None
        self.is_running = False
        self.is_shutdown = False
        
        
    def schedule(self, job: IJob, run_at: datetime.datetime) -> str:
        with self.condition:
            if self.is_shutdown:
                raise SchedulerShutdownError(
                    "cannot schedule a job after shutdown"
                )

            job_id = self.generate_job_id()
            scheduled_job = Job(
                job_id,
                JobStatus.SCHEDULED,
                run_at,
                executable_job=job
            )
            self.add_job(job_id, scheduled_job)
            heapq.heappush(
                self.ordered_queue,
                (run_at, self.submission_sequence, job_id)
            )
            self.submission_sequence += 1
            self.condition.notify()

        return job_id
        
    
    def generate_job_id(self) -> str:
        return str(uuid.uuid4())
        
    def add_job(self, job_id: str, scheduled_job: Job) -> None:
        self.jobs_by_id[job_id] = scheduled_job

    def get_job(self, job_id: str) -> Job:
        with self.condition:
            try:
                return self.jobs_by_id[job_id]
            except KeyError as error:
                raise JobNotFoundError(
                    f"job is not registered: {job_id}"
                ) from error

    def peek_next_job(self) -> Job | None:
        with self.condition:
            if not self.ordered_queue:
                return None

            _, _, job_id = self.ordered_queue[0]
            return self.jobs_by_id[job_id]

    def dispatch_next_due_job(self) -> bool:
        with self.condition:
            scheduled_job = self._pop_next_due_job()

        if scheduled_job is None:
            return False

        self.executor.submit(
            partial(self._execute_job, scheduled_job)
        )
        return True

    def start(self) -> None:
        with self.condition:
            if self.is_shutdown:
                raise SchedulerShutdownError(
                    "cannot restart a scheduler after shutdown"
                )
            if self.is_running:
                return

            self.is_running = True
            self.dispatcher_thread = threading.Thread(
                target=self._run_dispatcher,
                name="job-scheduler-dispatcher",
                daemon=True,
            )
            self.dispatcher_thread.start()

    def shutdown(self, wait: bool = True) -> None:
        with self.condition:
            if self.is_shutdown:
                return

            self.is_running = False
            self.is_shutdown = True
            self.condition.notify_all()
            dispatcher_thread = self.dispatcher_thread

        if wait and dispatcher_thread is not None:
            dispatcher_thread.join()

        self.executor.shutdown(wait=wait)

    def _run_dispatcher(self) -> None:
        while True:
            with self.condition:
                while self.is_running and not self.ordered_queue:
                    self.condition.wait()

                if not self.is_running:
                    return

                next_run_at, _, _ = self.ordered_queue[0]
                wait_seconds = (next_run_at - self.clock.now()).total_seconds()
                if wait_seconds > 0:
                    self.condition.wait(timeout=wait_seconds)
                    continue

                scheduled_job = self._pop_next_due_job()

            if scheduled_job is not None:
                self.executor.submit(
                    partial(self._execute_job, scheduled_job)
                )

    def _pop_next_due_job(self) -> Job | None:
        if not self.ordered_queue:
            return None

        run_at, _, job_id = self.ordered_queue[0]
        if run_at > self.clock.now():
            return None

        heapq.heappop(self.ordered_queue)
        scheduled_job = self.jobs_by_id[job_id]
        scheduled_job.status = JobStatus.WORKING
        return scheduled_job

    def _execute_job(self, scheduled_job: Job) -> None:
        try:
            scheduled_job.executable_job.execute()
        except Exception as error:
            with self.condition:
                scheduled_job.status = JobStatus.FAILED
                scheduled_job.last_error = error
        else:
            with self.condition:
                scheduled_job.status = JobStatus.SUCCESS
