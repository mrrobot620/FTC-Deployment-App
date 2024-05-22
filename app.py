from os import stat
from flask import Flask, render_template, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError


db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///ftc_deployment.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate.init_app(app, db)


    from models import Deployment , Station , Casper


    @app.route("/")
    def index():
        return render_template("base.html")
    

    @app.route("/get_deployment" , methods=["GET"])
    def get_deployment():
        try:
            date_str = request.args.get("date")
            shift = request.args.get("shift")
            try:
                date = datetime.strptime(date_str , "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"Error": "Invalid Date Format"}) , 400
            query = Deployment.query
        
            if date:
                query = query.filter_by(date=date)
            if shift:
                query = query.filter_by(shift=shift)

            deployments = query.all()

            if not deployments:
                return jsonify({"Error": "Unable to Find Deployment for the date"}) , 404
            else:
                data = jsonify([deployment.to_dict() for deployment in deployments])
                return data , 200
            
        except Exception as e:
            app.logger.error(f"Unexpected Error: {e}")
            return jsonify({"Error": "Internal Server Error"}), 500


    @app.route("/get_current_deployment" , methods=["GET"])
    def get_current_deployment():
        try:
            casper = request.args.get("casper")
            if casper:
                deployment = Deployment.query.filter_by(casper_id= casper).order_by(Deployment.date.desc()).first()
                if deployment:
                    return jsonify(deployment.to_dict())
                else:
                    return jsonify({"Error": "No Deployment Found for the User"}) , 404
            return jsonify("Error" , "Missing Casper") , 400
        except Exception as e:
            app.logger.error(f"Unexpected Error:  {e}")
            return jsonify({"Error": "Internal Server Error"}) , 500


    @app.route("/get_stations" , methods=["GET"])
    def get_station():
        try:
            zone = request.args.get("zone")
            station_type = request.args.get("type")

            query = Station.query
            if zone:
                query = query.filter_by(zone=zone)
            if station_type:
                query = query.filter_by(station_type=station_type)

            stations = query.all()
            
            if not stations:
                return jsonify({"Error" , "No Matching Station Found"}) , 404
            else:
                data = jsonify([station.to_dict() for station in stations])
                return data , 200


        except Exception as e:
            app.logger.error(f"Unexpected Error:  {e}")
            return jsonify({"Error": "Internal Server Error"}) , 500


    @app.route("/get_all_caspers" , methods=["GET"])
    def get_all_caspers():
        try:
            caspers = Casper.query.all()
            if not caspers:
                return jsonify({"Error": "No Casper ID Available"}), 404
            else:
                data = jsonify([casper.to_dict() for casper in caspers])
                return data , 200
        except Exception as e:
            app.logger.error(f"Unexpected Error: {e}")
            return jsonify({"Error": "Internal Server Error"}) , 500


    @app.route("/add_deployment" , methods=["POST"])
    def add_deployment():
        data = request.get_json()
        try:
            date = datetime.strptime(data.get("date") , "%Y-%m-%d").date()
            shift = data.get("shift")
            station_id = data.get("station_id")
            casper_ids = data.get("casper_ids")
                            
            if not station_id or not casper_ids or not shift:
                return jsonify({"Error": "Missing Fields"}) , 400

            

            deployments = []
            for casper_id in casper_ids:
                deployment = Deployment(date=date , shift=shift , station_id=station_id , casper_id = casper_id)
                db.session.add(deployment)
                deployments.append(deployment)
            db.session.commit()

            return jsonify(deployment.to_dict()) , 201
        except Exception as e:
            app.logger.error(f"Unexpected Error: {e}")
            return jsonify({"Error": "Internal Server Error"}) , 500

    @app.route("/add_casper" , methods=["POST"])
    def add_casper():
        data = request.get_json()
        try:
            if data:
                casper = data.get("casper")
                name = data.get("name")
                department = data.get("department")
                designation = data.get("designation")
                if not casper or not name or not department or not designation:
                    return jsonify({"Error": "Missing Fields"} ) , 400
                
                existing_user = Casper.query.filter_by(casper_id=casper).first()
                if existing_user:
                    return jsonify({"Error": f"Casper ID: {casper} Already Exists"}) , 409

                casper = Casper(casper_id=casper , name=name, department=department , designation=designation)
                db.session.add(casper)
                db.session.commit()
                return jsonify({"Sucess": f"Casper ID: '{casper}' added into DB"}) , 201
            else:
                return jsonify({"Error": "Data not posted"}) , 400
        except Exception as e:
            app.logger.error(f"Unexpected Error: {e}")
            return jsonify({"Error": "Internal Server Error"}) , 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=8000 , debug=True)


