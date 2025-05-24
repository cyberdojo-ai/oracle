from src.cron import CronTab
from .jobs import cron_events


def app() -> None:
    cron = CronTab(
        *cron_events,
    )
    cron.run()
