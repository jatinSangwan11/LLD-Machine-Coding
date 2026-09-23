import datetime
from collections.abc import Callable
import threading

import pytest

from job_scheduler.schedular import (
    IJob,
    JobNotFoundError,
    JobSchedular,
    JobStatus,
    SchedulerShutdownError,
)


class RecordingJob(IJob):
    def __init__(self) -> None:
        self.execution_count = 0

    def execute(self) -> None:
        self.execution_count += 1


class FailingJob(IJob):
    def execute(self) -> None:
        raise ValueError("job execution failed")


class FixedClock:
    def __init__(self, current_time: datetime.datetime) -> None:
        self.current_time = current_time

    def now(self) -> datetime.datetime:
        return self.current_time


class ImmediateExecutor:
    def __init__(self) -> None:
        self.submission_count = 0
        self.task_finished = threading.Event()
        self.was_shutdown = False

    def submit(self, task: Callable[[], None]) -> object:
        self.submission_count += 1
        try:
            task()
        finally:
            self.task_finished.set()
        return object()

    def shutdown(self, wait: bool = True) -> None:
        self.was_shutdown = True


def create_scheduler(
    current_time: datetime.datetime,
) -> tuple[JobSchedular, ImmediateExecutor]:
    executor = ImmediateExecutor()
    scheduler = JobSchedular(
        retry_policy=None,
        clock=FixedClock(current_time),
        executor=executor,
    )
    return scheduler, executor


def test_schedule_registers_one_time_job() -> None:
    current_time = datetime.datetime(
        2026,
        9,
        15,
        9,
        0,
        tzinfo=datetime.timezone.utc,
    )
    scheduler, _ = create_scheduler(current_time)
    executable_job = RecordingJob()
    run_at = datetime.datetime(
        2026,
        9,
        15,
        10,
        0,
        tzinfo=datetime.timezone.utc,
    )

    job_id = scheduler.schedule(executable_job, run_at)

    scheduled_job = scheduler.get_job(job_id)
    assert scheduled_job.job_id == job_id
    assert scheduled_job.status is JobStatus.SCHEDULED
    assert scheduled_job.run_at == run_at
    assert scheduled_job.executable_job is executable_job
    assert executable_job.execution_count == 0


def test_get_job_rejects_unknown_job_id() -> None:
    current_time = datetime.datetime(
        2026,
        9,
        15,
        9,
        0,
        tzinfo=datetime.timezone.utc,
    )
    scheduler, _ = create_scheduler(current_time)

    with pytest.raises(JobNotFoundError, match="missing-job"):
        scheduler.get_job("missing-job")


def test_schedule_rejects_new_job_after_shutdown() -> None:
    current_time = datetime.datetime(
        2026,
        9,
        15,
        9,
        0,
        tzinfo=datetime.timezone.utc,
    )
    scheduler, _ = create_scheduler(current_time)
    scheduler.shutdown()

    with pytest.raises(SchedulerShutdownError, match="after shutdown"):
        scheduler.schedule(RecordingJob(), current_time)


def test_peek_next_job_returns_earliest_scheduled_job() -> None:
    current_time = datetime.datetime(
        2026,
        9,
        15,
        9,
        0,
        tzinfo=datetime.timezone.utc,
    )
    scheduler, _ = create_scheduler(current_time)
    later_job = RecordingJob()
    earlier_job = RecordingJob()
    later_run_at = datetime.datetime(
        2026,
        9,
        15,
        11,
        0,
        tzinfo=datetime.timezone.utc,
    )
    earlier_run_at = datetime.datetime(
        2026,
        9,
        15,
        10,
        0,
        tzinfo=datetime.timezone.utc,
    )

    scheduler.schedule(later_job, later_run_at)
    earlier_job_id = scheduler.schedule(earlier_job, earlier_run_at)

    next_job = scheduler.peek_next_job()

    assert next_job.job_id == earlier_job_id
    assert next_job.executable_job is earlier_job
    assert next_job.run_at == earlier_run_at


def test_dispatch_executes_due_job_and_marks_it_successful() -> None:
    current_time = datetime.datetime(
        2026,
        9,
        15,
        10,
        0,
        tzinfo=datetime.timezone.utc,
    )
    scheduler, executor = create_scheduler(current_time)
    executable_job = RecordingJob()
    job_id = scheduler.schedule(executable_job, current_time)

    was_dispatched = scheduler.dispatch_next_due_job()

    assert was_dispatched is True
    assert executor.submission_count == 1
    assert executable_job.execution_count == 1
    assert scheduler.get_job(job_id).status is JobStatus.SUCCESS
    assert scheduler.peek_next_job() is None


def test_dispatch_marks_job_failed_and_records_original_error() -> None:
    current_time = datetime.datetime(
        2026,
        9,
        15,
        10,
        0,
        tzinfo=datetime.timezone.utc,
    )
    scheduler, executor = create_scheduler(current_time)
    job_id = scheduler.schedule(FailingJob(), current_time)

    was_dispatched = scheduler.dispatch_next_due_job()

    failed_job = scheduler.get_job(job_id)
    assert was_dispatched is True
    assert executor.submission_count == 1
    assert failed_job.status is JobStatus.FAILED
    assert isinstance(failed_job.last_error, ValueError)
    assert str(failed_job.last_error) == "job execution failed"
    assert scheduler.peek_next_job() is None


def test_dispatch_leaves_future_job_scheduled() -> None:
    current_time = datetime.datetime(
        2026,
        9,
        15,
        10,
        0,
        tzinfo=datetime.timezone.utc,
    )
    scheduler, executor = create_scheduler(current_time)
    executable_job = RecordingJob()
    run_at = current_time + datetime.timedelta(hours=1)
    job_id = scheduler.schedule(executable_job, run_at)

    was_dispatched = scheduler.dispatch_next_due_job()

    assert was_dispatched is False
    assert executor.submission_count == 0
    assert executable_job.execution_count == 0
    assert scheduler.get_job(job_id).status is JobStatus.SCHEDULED
    assert scheduler.peek_next_job().job_id == job_id


def test_background_dispatcher_executes_job_scheduled_while_queue_is_empty() -> None:
    current_time = datetime.datetime(
        2026,
        9,
        15,
        10,
        0,
        tzinfo=datetime.timezone.utc,
    )
    scheduler, executor = create_scheduler(current_time)
    executable_job = RecordingJob()
    scheduler.start()

    try:
        job_id = scheduler.schedule(executable_job, current_time)
        assert executor.task_finished.wait(timeout=1)

        assert executable_job.execution_count == 1
        assert scheduler.get_job(job_id).status is JobStatus.SUCCESS
        assert scheduler.peek_next_job() is None
    finally:
        scheduler.shutdown()

    assert executor.was_shutdown is True


def test_new_earlier_job_wakes_background_dispatcher() -> None:
    current_time = datetime.datetime(
        2026,
        9,
        15,
        10,
        0,
        tzinfo=datetime.timezone.utc,
    )
    scheduler, executor = create_scheduler(current_time)
    future_job = RecordingJob()
    due_job = RecordingJob()
    future_job_id = scheduler.schedule(
        future_job,
        current_time + datetime.timedelta(hours=1),
    )
    scheduler.start()

    try:
        due_job_id = scheduler.schedule(due_job, current_time)
        assert executor.task_finished.wait(timeout=1)

        assert due_job.execution_count == 1
        assert scheduler.get_job(due_job_id).status is JobStatus.SUCCESS
        assert future_job.execution_count == 0
        assert scheduler.get_job(future_job_id).status is JobStatus.SCHEDULED
        assert scheduler.peek_next_job().job_id == future_job_id
    finally:
        scheduler.shutdown()
