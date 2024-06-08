from app import db, create_app
from models import Station, Casper, Deployment , ScanData
from datetime import datetime
import pandas as pd 


df = pd.read_csv("ftc.csv")


# Initialize the Flask app and database
app = create_app()
app.app_context().push()

#for _, row in df.iterrows():
 #   casper = Casper(casper_id=row["casper"] , name=row["name"] , department=row["department"] , designation=row["designation"])
  #  db.session.add(casper)

#data = ScanData.query.filter_by(casper_id = 'abhishek.h1').all()

scan = ScanData(casper_id='abhishek.h1' , station_id = 1 , primary_scan = 100 , secondary_scan = 100 , bagging_scan = 100 , sl_scan = 2 , shift='Morning')


db.session.add(scan)
db.session.commit()

#print([d.to_dict() for d in1 data])


# Add deployments to the sessiond and commit to save them to the database
print("Sample data added successfully!")

