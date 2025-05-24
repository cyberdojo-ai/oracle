from src.cron import Event

from .ics_sans_edu_scraper import cron_events as ics_sans_edu_scraper_cron_events

cron_events: list[Event] = [
    *ics_sans_edu_scraper_cron_events,
]

__all__ = [
    "cron_events",
]
