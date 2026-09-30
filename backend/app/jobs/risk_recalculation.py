def run_daily_risk_job():
    from ..services.risk_service import run_batch_risk_calculation
    print("[Job] Starting daily risk recalculation...")
    count = run_batch_risk_calculation()
    print(f"[Job] Daily risk job complete: {count} personnel scored")
