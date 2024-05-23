from app import db
from datetime import datetime

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
    casper_id = db.Column(db.String(10), nullable=False , unique=True)
    name = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(50) , nullable=False)
    designation = db.Column(db.String(50) , nullable=False)

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

