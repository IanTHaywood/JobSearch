from apscheduler.job import Job
from apscheduler.triggers.cron import CronTrigger
from fastapi import APIRouter, HTTPException

from jobsearch.api.schemas import CronJobIn, CronJobOut
from jobsearch.api.scheduler import get_scheduler, run_connector_job
from jobsearch.ingest.registry import CONNECTORS

router = APIRouter(prefix="/api/cron", tags=["cron"])


def _job_to_out(job: Job) -> CronJobOut:
    return CronJobOut(
        id=job.id,
        connector=job.args[0] if job.args else "",
        # job.name carries the original crontab string (set at creation)
        # since str(job.trigger) doesn't round-trip it exactly.
        cron_expression=job.name or "",
        next_run_time=job.next_run_time,
        paused=job.next_run_time is None,
    )


def _get_job_or_404(job_id: str) -> Job:
    job = get_scheduler().get_job(job_id)
    if job is None:
        raise HTTPException(404, f"No cron job with id {job_id}")
    return job


@router.get("", response_model=list[CronJobOut])
def list_cron_jobs() -> list[CronJobOut]:
    return [_job_to_out(job) for job in get_scheduler().get_jobs()]


@router.post("", response_model=CronJobOut)
def create_cron_job(payload: CronJobIn) -> CronJobOut:
    if payload.connector not in CONNECTORS:
        raise HTTPException(404, f"Unknown connector: {payload.connector}")
    try:
        trigger = CronTrigger.from_crontab(payload.cron_expression)
    except ValueError as exc:
        raise HTTPException(400, f"Invalid cron expression: {exc}") from exc
    job = get_scheduler().add_job(
        run_connector_job,
        trigger=trigger,
        args=[payload.connector],
        name=payload.cron_expression,
    )
    return _job_to_out(job)


@router.post("/{job_id}/pause", response_model=CronJobOut)
def pause_cron_job(job_id: str) -> CronJobOut:
    _get_job_or_404(job_id)
    get_scheduler().pause_job(job_id)
    return _job_to_out(_get_job_or_404(job_id))


@router.post("/{job_id}/resume", response_model=CronJobOut)
def resume_cron_job(job_id: str) -> CronJobOut:
    _get_job_or_404(job_id)
    get_scheduler().resume_job(job_id)
    return _job_to_out(_get_job_or_404(job_id))


@router.delete("/{job_id}")
def delete_cron_job(job_id: str) -> dict:
    _get_job_or_404(job_id)
    get_scheduler().remove_job(job_id)
    return {"status": "deleted", "id": job_id}
