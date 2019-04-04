# Import Dependecies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Import Flask
from flask import Flask, jsonify

####################################
# Database Setup
####################################
engine = create_engine("sqlite://Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#####################################
# Flask Setup
#####################################

climateApp = Flask(__name__)

#####################################
# Flask Routes
#####################################

@climateApp.route("/")
def welcome():
     return (
        f"Welcome to Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )

@climateApp.route("/api/v1.0/precipitation")
def precipitation():
    """ Return a JSON list of all precipitation data as a dictionary with date as key and precipitation as value"""
    # Query all precipitation
    precipitation_results = session.query(Measurement.prcp).all()

    # Create a dictionary from the row data and append to a list of all_precipitation
    all_precipitation = []
    for precipitation in precipitation_results:
        precipitation_dict = {}
        precipitation_dict[precipitation.date] = precipitation.prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)


@climateApp.route("/api/v1.0/stations")
def stations():
    """ Return a JSON list of all stations."""
    # Query all stations
    station_results = session.query(Station.name).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(station_results))

    return jsonify(all_stations)

@climateApp.route("/api/v1.0/tobs")
def tobs():
    """ Return a JSON list of Temperature Observations for the last year."""
    # Query all tobs between 2016-08-23 and 2017-08-23
    tobs_results = session.query(Measurement.tobs).filter(Measurement.date.between('2016-08-23', '2017-08-23')).all()

    # Convert list of tuples into normal list
    all_tobs = list(np.ravel(tobs_results))

    return jsonify(all_tobs)

@climateApp.route("/api/v1.0/<start>")
def tobs_start(startDate):
    """ Return TMIN, TAVE, and TMAX for all dates greater than and equal to startDate."""
    # Query all tobs greater than and equal to startDate
    minAveMaxTobs =  session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= startDate).all()

    # Convert list of tuples into normal list
    minAveMaxTobsList = list(np.ravel(minAveMaxTobs))
    
    tmin = minAveMaxTobsList[0]
    tave = minAveMaxTobsList[1]
    tmax = minAveMaxTobsList[2]

    return jsonify(tmin, tave, tmax)

@climateApp.route("/api/v1.0/<start>/<end>")
def tobs_start_end(startDate, endDate):
    """ Return TMIN, TAVE, and TMAX for dates between startDate and endDate inclusive."""
    # Query all tobs between startDate and endDate inclusive
    min_ave_max_tobs = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= startDate).filter(Measurement.date <= endDate).all()

    # Convert list of tuples into normal list
    min_ave_max_tobs_list = list(np.ravel(min_ave_max_tobs))

    tmin = min_ave_max_tobs_list[0]
    tave = min_ave_max_tobs_list[1]
    tmax = min_ave_max_tobs_list[2]

    return jsonify(tmin, tave, tmax)


if __name__ == '__main__':
    climateApp.run(debug=True)
    