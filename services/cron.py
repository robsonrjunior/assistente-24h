from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from assistant import assistant
from assistant import cron_tools

scheduler = BlockingScheduler()


def _can_run(cron_job: dict) -> bool:
    max_runs = cron_job["max_runs"]
    return max_runs is None or cron_job["run_count"] < max_runs

def load_jobs_from_db():
    """Loads or reloads active cron jobs from the database."""
    scheduler.remove_all_jobs()

    for cron_job in cron_tools.get_all_cron_records(only_active=True):
        if not _can_run(cron_job):
            cron_tools.set_cron_active_status(cron_job["id"], False)
            continue

        scheduler.add_job(
            func=execute_task,
            trigger=CronTrigger.from_crontab(cron_job["cron_expression"]),
            id=str(cron_job["id"]),
            name=cron_job["name"],
            args=[cron_job["id"]],
        )

def execute_task(task_id: int):
    cron_job = cron_tools.get_cron_record(task_id)
    if not cron_job or not cron_job["is_active"]:
        return
    if not _can_run(cron_job):
        cron_tools.set_cron_active_status(task_id, False)
        load_jobs_from_db()
        return

    print(f"Executando: {task_id}")
    assistant.execute_task(task_id)
    cron_tools.increment_cron_run_count(task_id)

    updated_cron = cron_tools.get_cron_record(task_id)
    if updated_cron and not _can_run(updated_cron):
        cron_tools.set_cron_active_status(task_id, False)
        load_jobs_from_db()

def add_task(name: str, description: str, cron_expression: str):
    """Adds a new cron job to the database."""
    cron_tools.add_cron(name=name, description=description, cron_expression=cron_expression)

def remove_task(cron_id: int):
    """Removes a cron job from the database."""
    cron_tools.remove_cron(cron_id)

def start():
    """Loads jobs from the database and starts the scheduler."""
    # Recarrega jobs do DB a cada 1 minuto (pega adições/remoções em runtime)
    scheduler.add_job(load_jobs_from_db, "interval", minutes=1)
    load_jobs_from_db()
    scheduler.start()

if __name__ == "__main__":
    start()