from enum import unique
from os import stat
from flask import Flask, json, render_template, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import text
import pandas as pd
import os
import pandas as pd


db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///ftc_deployment.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate.init_app(app, db)

    UPLOAD_FOLDER = 'upload'
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)


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
                data = [deployment.to_dict() for deployment in deployments]
                df = pd.json_normalize(data)
                overview = df.pivot_table(index='station.type' , values='casper.name' , aggfunc='count')
                overview2 = overview.rename(columns={'casper.name': "type"})
                overview_dict = overview2.to_dict()

                station_wise = df.pivot_table(index="station.station" , values='casper.name' , aggfunc='count')
                station_wise2 = station_wise.rename(columns={'casper.name': "type"})
                station_wise_dict = station_wise2.to_dict()
                response_data = {
                    "data": data,
                    "overview": overview_dict,
                    "stations_wise": station_wise_dict
                }
                return jsonify(response_data) , 200
            
        except Exception as e:
            app.logger.error(f"Unexpected Error: {e}")
            return jsonify({"Error": "Internal Server Error"}), 500


    @app.route("/get_current_deployment" , methods=["GET"])
    def get_current_deployment():
        try:
            casper = request.args.get("casper")
            if casper:
                deployment = Deployment.query.filter_by(casper_id=casper).order_by(Deployment.date.desc()).first()
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
        deployed = set()
        already_deployedd = set()
        try:
            date = datetime.strptime(data.get("date") , "%Y-%m-%d").date()
            shift = data.get("shift")
            station_id = data.get("station_id")
            casper_ids =  data.get("casper_ids")

            if not station_id or not casper_ids or not shift:
                return jsonify({"Error": "Missing Fields"}) , 400
            already_deployed = isAlreadyDeployed(casper_ids , date)
            deployments = []
            for casper_id in casper_ids:
                deployment = Deployment(date=date , shift=shift , station_id=station_id , casper_id = casper_id)
                if casper_id not in already_deployed:
                    db.session.add(deployment)
                    deployments.append(deployment)
                    db.session.commit()
                    deployed.add(casper_id)
                else:
                    already_deployedd.add(casper_id)
            return jsonify({"Deployed": list(deployed) , "Already Deployed": list(already_deployedd)}) , 201
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


    @app.route("/get_zonewise_station" , methods=["GET"])
    def get_zonewise_station():
        zone = request.args.get("zone")
        try:
            if zone:
                stations = Station.query.filter_by(zone=zone)
                if stations:
                    data = [station.to_dict() for station in stations]
                    return jsonify(data) , 200
                else:
                    return jsonify("Error", "Stations not Available for this zone") , 404
            else:
                return jsonify("Error" , "Missing Fields") , 400
        except Exception as e:
            app.logger.error(f"Unexpected Error:  {e}")
            return jsonify({"Error": "Internal Server Error"}) , 500

    @app.route("/get_zone" , methods=["GET"])
    def get_zone():
        try:
            zones = db.session.query(Station.zone.distinct()).all()
            zone = [zone[0] for zone in zones]
            return jsonify(zone) , 200
        except Exception as e:
            app.logger.error(f"Unepected Error:  {e}")
            return jsonify({"Error": "Internal Server Error"}) , 500


    def isAlreadyDeployed(casper_ids , date):
        already_deployed = []
        try:
            today_deployment = Deployment.query.filter_by(date=date).all()
            deployment = [str(deployment.casper_id) for deployment in today_deployment]
            print(f"casper_ids => {casper_ids} , today_deployment => {deployment}")
            for casper in casper_ids:
                if casper in deployment:
                    already_deployed.append(casper) 
            print(already_deployed)
        except Exception as e:
            app.logger.error(f'Unexpected Error:  {e}')
        
        return already_deployed

    @app.route("/delete_deployment" , methods=["POST"])
    def delete_deployment():
        try:
            deployment_id = request.args.get("deployment_id")
            if not deployment_id:
                return jsonify({"Error": "Missing Deployment ID"}) , 400
            deployment = Deployment.query.get(deployment_id)
            if not deployment:
                return jsonify({"Error" , "Deployment Not Found"}) , 404
            db.session.delete(deployment)
            db.session.commit()
            return jsonify({"Sucess":  f"Deployment ID: {deployment_id} deleted successfully"}) , 200
        except Exception as e:
            app.logger.error(f"Unexpected Error:  {e}")
            return jsonify({"Error": "Internal Server Error"}) , 500


    @app.route("/upload_users" , methods=["POST"])
    def upload_users():
        if 'file' not in request.files:
            return jsonify({"Error": "No File Found"}) , 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"Error": "No File Uploaded"}) , 400

        if file and file.filename.endswith(".csv"):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'] , filename)
            print(f'FilePath => {filepath}')
            file.save(filepath)
            success, message = save_users(filepath)
            if success:
                return jsonify({"message": message}) , 200
            else:
                return jsonify({"error": message}) , 400
        else:
            return jsonify({"error": "Invalid Filetype"}) , 400


    def save_users(filepath: str) -> tuple:
        headers = ["casper" , "name" , "designation" , "department"] 
        if not os.path.exists(filepath):
            return False , "File Does Not Exists"
        df = pd.read_csv(filepath)
        file_headers = df.columns.to_list()
        app.logger.debug(f"Server Headers => {headers} || File Headers => {file_headers}")

        if headers != file_headers:
            return False , "CSV Headers are different"

        new_users = 0

        for _, row in df.iterrows():
            if not Casper.query.filter_by(casper_id= row["casper"]).first():
                casper = Casper(
                    casper_id = row["casper"],
                    name = row['name'],
                    designation = row['department'],
                    department = row['department']
                )
                db.session.add(casper)
                new_users += 1

        db.session.commit()

        if new_users <= 0:
            return True  , "No new users Added"
        else:
            return True , f"{len(str(new_users))} users added Sucessfully"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=8000 , debug=True )

