import sys
import os
import csv
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.personnel import Personnel
from app.models.risk_score import RiskScore

app = create_app()

def export_to_csv():
    with app.app_context():
        officers = Personnel.query.all()
        
        csv_file = os.path.join(os.path.dirname(__file__), 'fake_officers_data.csv')
        
        with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow([
                'Name', 'Service Number', 'Rank', 'Unit', 'Deployment Zone',
                'Years of Service', 'Family Station', 'Stress Score', 
                'Burnout Score', 'Overall Risk'
            ])
            
            for o in officers:
                rs = RiskScore.query.filter_by(personnel_id=o.id).order_by(RiskScore.score_date.desc()).first()
                writer.writerow([
                    o.name,
                    o.service_number,
                    o.rank,
                    o.unit_name,
                    o.deployment_zone,
                    o.years_of_service,
                    "Yes" if o.family_station else "No",
                    rs.stress_score if rs else "N/A",
                    rs.burnout_score if rs else "N/A",
                    rs.overall_risk if rs else "N/A"
                ])
                
        print(f"Data successfully exported to {csv_file}")

if __name__ == '__main__':
    export_to_csv()
