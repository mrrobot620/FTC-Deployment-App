from app import db, create_app
from models import Station, Casper, Deployment
from datetime import datetime
import pandas as pd 


df = pd.read_csv("ftc.csv")


# Initialize the Flask app and database
app = create_app()
app.app_context().push()

for _, row in df.iterrows():
    casper = Casper(casper_id=row["casper"] , name=row["name"] , department=row["department"] , designation=row["designation"])
    db.session.add(casper)

db.session.commit()


# Add deployments to the session and commit to save them to the database
print("Sample data added successfully!")

