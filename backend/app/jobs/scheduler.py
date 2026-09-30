from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit

_scheduler = None

def init_scheduler(app):
    global _scheduler
    _scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
    with app.app_context():
        from .risk_recalculation import run_daily_risk_job
        from .alert_escalation import run_alert_escalation
        _scheduler.add_job(
            func=lambda: _run_with_context(app, run_daily_risk_job),
            trigger=CronTrigger(hour=2, minute=0),
            id="daily_risk_recalculation", replace_existing=True,
        )
        _scheduler.add_job(
            func=lambda: _run_with_context(app, run_alert_escalation),
            trigger=CronTrigger(hour="*/6"),
            id="alert_escalation", replace_existing=True,
        )
    _scheduler.start()
    atexit.register(lambda: _scheduler.shutdown())
    print("[Scheduler] APScheduler started")

def _run_with_context(app, func):
    with app.app_context():
        func()
