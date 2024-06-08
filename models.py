from typing import DefaultDict
from app import db
from datetime import datetime , date as dt_date

class Deployment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    shift = db.Column(db.String(50), nullable=False)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    casper_id = db.Column(db.Integer, db.ForeignKey('casper.id'), nullable=False)
    station = db.relationship('Station', backref=db.backref('deployments', lazy=True))
    casper = db.relationship('Casper', backref=db.backref('deployments', lazy=True))


    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime("%Y-%m-%d"),
            'shift': self.shift,
            'station': self.station.to_dict() if self.station else None,
            'casper': self.casper.to_dict() if self.casper else None
        }

    def __repr__(self) -> str:
        return f"Date: {self.date} Shift: {self.shift} Station: {self.station} Casper: {self.casper}"

class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    zone = db.Column(db.String(10), nullable=False)
    station = db.Column(db.String(50), nullable=False)
    station_type = db.Column(db.String(50) , nullable=False)
    def to_dict(self):
        return {
            'id': self.id,
            'zone': self.zone,
            'station': self.station,
            "type": self.station_type
        }

    def __repr__(self) -> str:
        return f"Station: {self.station} Zone: {self.zone} Type: {self.station_type}"

class Casper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50) , nullable=False)
    casper_id = db.Column(db.String(10), nullable=False , unique=True)
    designation = db.Column(db.String(50) , nullable=False)
    department = db.Column(db.String(50) , nullable=False)
    designation = db.Column(db.String(50) , nullable=False)
    scan_data = db.relationship('ScanData', backref='casper', lazy=True)


    def to_dict(self):
        return {
            'id': self.id,
            'casper_id': self.casper_id,
            'name': self.name,
            "designation": self.designation,
            "department": self.department
        }

   
    def __repr__(self) -> str:
        return f"Casper Id: {self.casper_id} Name: {self.name}"


class ScanData(db.Model):
    id = db.Column(db.Integer , primary_key=True)
    casper_id = db.Column(db.Integer , db.ForeignKey("casper.casper_id") , nullable=False)
    primary_scan = db.Column(db.Integer , default=0)
    secondary_scan = db.Column(db.Integer , default=0)
    bagging_scan = db.Column(db.Integer , default = 0)
    sl_scan = db.Column(db.Integer , default = 0)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    hour = db.Column(db.Integer , nullable=False , default=datetime.now().hour)
    shift = db.Column(db.String , nullable=False)
    weekday = db.Column(db.Integer, nullable=False, default=datetime.utcnow().weekday())
    station_id = db.Column(db.Integer, db.ForeignKey("station.id"), nullable=False)
    station = db.relationship('Station', backref=db.backref('scan_data', lazy=True))


    def to_dict(self):
        return {
            'id': self.id,
            'casper_id': self.casper_id,
            'station_id': self.station_id,
            'date': self.date.strftime("%Y-%m-%d"),
            'hour': self.hour,
            'shift': self.shift,
            'weekday': self.weekday,
            'primary_scan': self.primary_scan,
            'secondary_scan': self.secondary_scan,
            'bagging_scan': self.bagging_scan,
            'sl_scan': self.sl_scan,
            'station': self.station.to_dict() if self.station else None
        }


    @classmethod
    def total_day_scans(cls , casper_id: int , date: dt_date):
        if casper_id and date:
            scan_data = cls.query.filter_by(casper_id=casper_id , date=date).all()
            total_scans = {
                "primary_scan": sum(data.primary_scan for data in scan_data),
                "secondary_scan": sum(data.secondary_scan for data in scan_data),
                "bagging_scan": sum(data.bagging_scan for data in scan_data),
                "sl_scan": sum(data.sl_scan for data in scan_data)
            }
        else:
            total_scans = {}

        return total_scans

        






