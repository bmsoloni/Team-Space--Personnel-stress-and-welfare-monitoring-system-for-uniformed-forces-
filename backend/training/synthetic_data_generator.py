"""Generate synthetic training data for stress and burnout models."""
import numpy as np
import pandas as pd
import os

np.random.seed(42)

def generate_dataset(n=2000):
    data = []
    for _ in range(n):
        zone = np.random.choice(["peace","field","high_altitude","insurgency","counter_terror"],
                                p=[0.3,0.25,0.2,0.15,0.1])
        zone_risk = {"peace":0.2,"field":0.5,"high_altitude":0.7,"insurgency":0.85,"counter_terror":1.0}[zone]
        dep_days = int(np.random.exponential(180) * (zone_risk + 0.5))
        leave_denied = int(np.clip(np.random.poisson(zone_risk * 3), 0, 10))
        leave_freq = int(np.clip(np.random.poisson(3 - zone_risk * 2), 0, 8))
        duty_hours = float(np.clip(np.random.normal(48 + zone_risk * 12, 8), 35, 80))
        overtime = int(np.clip(np.random.poisson(zone_risk * 5), 0, 20))
        transfers = int(np.clip(np.random.poisson(zone_risk * 2), 0, 6))
        consec_days = int(np.clip(np.random.poisson(7 + zone_risk * 15), 0, 60))
        wellness = float(np.clip(np.random.normal(70 - zone_risk * 30, 15), 10, 100))
        fam_sep = dep_days if np.random.random() > 0.3 else 0
        incidents = int(np.clip(np.random.poisson(zone_risk * 2), 0, 8))
        night_ratio = float(np.clip(np.random.beta(zone_risk * 2 + 0.5, 3), 0, 1))
        yos = int(np.random.uniform(1, 25))

        stress = min(100, max(0,
            20 + dep_days/365*30 + leave_denied*5 + consec_days*1.5 +
            max(0,(duty_hours-48)*0.5) - (wellness-50)*0.3 +
            zone_risk*20 + incidents*3 + np.random.normal(0,5)))
        burnout = min(100, max(0,
            15 + dep_days/365*25 + overtime*2 - (wellness-50)*0.2 +
            night_ratio*25 + leave_denied*3 + np.random.normal(0,5)))

        stress_label = 0 if stress < 60 else 1
        burnout_label = 0 if burnout < 55 else 1

        data.append([leave_freq, leave_denied, duty_hours, overtime, dep_days, transfers,
                     consec_days, wellness, fam_sep, incidents, 0, night_ratio,
                     zone_risk, yos, stress, burnout, stress_label, burnout_label])

    cols = ["leave_frequency_30d","leave_denied_90d","avg_duty_hours_weekly","overtime_days_30d",
            "deployment_duration_days","transfer_count_2yr","consecutive_duty_days","wellness_score_avg",
            "family_separation_days","incident_exposure_count","training_burden_days","night_shift_ratio",
            "zone_risk_factor","years_of_service","stress_score","burnout_score","stress_label","burnout_label"]
    return pd.DataFrame(data, columns=cols)

if __name__ == "__main__":
    df = generate_dataset(3000)
    os.makedirs("../ml_models", exist_ok=True)
    df.to_csv("synthetic_training_data.csv", index=False)
    print(f"Generated {len(df)} samples. Stress HIGH: {df.stress_label.sum()}, Burnout HIGH: {df.burnout_label.sum()}")
