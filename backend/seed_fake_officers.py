import sys
import os
import random
from datetime import datetime, timedelta

# Add backend dir to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.personnel import Personnel
from app.models.risk_score import RiskScore
from app.models.leave_record import LeaveRecord
from app.models.deployment_record import DeploymentRecord
from app.models.alert import Alert

app = create_app()

first_names = [
    "Vikram", "Ajay", "Manoj", "Deepak", "Sunil", "Pawan", "Rakesh", "Amitabh",
    "Sanjay", "Anil", "Rahul", "Vijay", "Rajesh", "Ramesh", "Suresh", "Mahesh",
    "Arun", "Tarun", "Karan", "Arjun", "Kunal", "Rohan", "Nitin", "Praveen",
    "Ashok", "Alok", "Dev", "Raj", "Vikas", "Vishal", "Akash", "Anand"
]
last_names = [
    "Rathore", "Verma", "Yadav", "Rawat", "Chhetri", "Kalyan", "Sharma", "Roy",
    "Singh", "Kumar", "Gupta", "Patel", "Das", "Joshi", "Chauhan", "Rajput",
    "Mishra", "Pandey", "Tiwari", "Reddy", "Nair", "Menon", "Pillai", "Iyer"
]
ranks = ["Constable", "Head Constable", "ASI", "SI", "Inspector", "DSP"]
units = ["204 CoBRA", "RAF 101", "139 Bn CRPF", "88 Bn CRPF", "1st Bn BSF", "10th Bn ITBP"]
zones = ["peace", "field", "high_altitude", "insurgency", "counter_terror"]

def get_risk_factors(overall_risk):
    factors = []
    if overall_risk in ["HIGH", "CRITICAL"]:
        factors.extend(["High operational stress", "Frequent deployments", "Lack of leaves"])
    elif overall_risk == "MODERATE":
        factors.extend(["Moderate operational stress", "Recent transfer"])
    else:
        factors.append("No significant risk factors")
    return factors

def main():
    with app.app_context():
        # Clean existing data
        print("Cleaning existing data...")
        Alert.query.delete()
        RiskScore.query.delete()
        LeaveRecord.query.delete()
        DeploymentRecord.query.delete()
        Personnel.query.delete()
        db.session.commit()
        
        print("Generating 60 fake officers...")
        personnel_list = []
        for i in range(60):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            service_no = f"POL-{2010 + random.randint(0, 14)}-{1000 + i}"
            rank = random.choice(ranks)
            unit_name = random.choice(units)
            zone = random.choice(zones)
            
            p = Personnel()
            p.name = name
            p.service_number = service_no
            p.unit_id = random.randint(1, 5)
            p.unit_name = unit_name
            p.rank = rank
            p.years_of_service = random.randint(1, 20)
            p.deployment_zone = zone
            p.family_station = random.choice([True, False])
            
            doj_years_ago = p.years_of_service
            p.date_of_joining = datetime.now().date() - timedelta(days=doj_years_ago*365)
            p.current_posting_date = datetime.now().date() - timedelta(days=random.randint(100, 1000))
            
            db.session.add(p)
            personnel_list.append(p)
            
        db.session.commit()
        print("Officers created. Generating risk scores...")
        
        for p in personnel_list:
            # Generate 3 risk scores for the past 3 months
            for month_offset in [60, 30, 0]:
                rs = RiskScore()
                rs.personnel_id = p.id
                rs.score_date = datetime.now().date() - timedelta(days=month_offset)
                
                # Zone multiplier
                zone_mult = {"peace": 1.0, "field": 1.2, "high_altitude": 1.5, "insurgency": 1.6, "counter_terror": 1.8}[p.deployment_zone]
                
                base_stress = random.uniform(20, 50)
                stress = min(100, base_stress * zone_mult)
                base_burnout = random.uniform(10, 40)
                burnout = min(100, base_burnout * zone_mult)
                
                rs.stress_score = round(stress, 1)
                rs.burnout_score = round(burnout, 1)
                
                avg = (stress + burnout) / 2
                if avg < 40:
                    rs.overall_risk = "LOW"
                elif avg < 60:
                    rs.overall_risk = "MODERATE"
                elif avg < 80:
                    rs.overall_risk = "HIGH"
                else:
                    rs.overall_risk = "CRITICAL"
                    
                rs.risk_factors = get_risk_factors(rs.overall_risk)
                db.session.add(rs)
                
        db.session.commit()
        print("Done successfully!")

if __name__ == '__main__':
    main()
