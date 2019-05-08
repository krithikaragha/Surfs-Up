# Import Dependecies
import os
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
from dateutil.relativedelta import relativedelta

# Import Flask
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

#####################################
# Flask Setup
#####################################

climateApp = Flask(__name__)

####################################
# Database Setup
####################################
climateApp.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgres://urdigfhxdarjoh:43a9cf1dc23b6559a374c5c5e71524bcd4208077b39d704a1db650eedb61cf8b@ec2-54-225-116-36.compute-1.amazonaws.com:5432/deodg0vhaa6b0j')
db = SQLAlchemy(climateApp)
# engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(db.engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(db.engine)

#####################################
# Flask Routes
#####################################

@climateApp.route("/")
def index():
    return render_template("index.html")

@climateApp.route("/api/v1.0/precipitation")
def precipitation():
    """ Return a JSON list of all precipitation data as a dictionary with date as key and precipitation as value"""
    # Query all precipitation
    precipitation_results = session.query(Measurement.date, Measurement.prcp).all()

    # Convert list of tuples into normal list
    precipitation_resultsList = list(np.ravel(precipitation_results))

    # Create a dictionary from the row data and append to a list of all_precipitation
    dates = precipitation_resultsList[0::2]
    prcp = precipitation_resultsList[1::2]   
    precipitation_dict = dict(zip(dates, prcp))

    return jsonify(precipitation_dict)


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
def tobs_start(start):
    """ Return TMIN, TAVE, and TMAX for all dates greater than and equal to startDate."""

    # Query the database to get the maximum date
    max_date_query = session.query(func.max(Measurement.date)).scalar()

    # Convert max_date to proper date format
    max_date = dt.datetime.strptime(max_date_query, '%Y-%m-%d').date()

    # Query all tobs greater than and equal to startDate
    minAveMaxTobs =  session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= max_date).all()

    # Convert list of tuples into normal list
    minAveMaxTobsList = list(np.ravel(minAveMaxTobs))
    
    tmin = minAveMaxTobsList[0]
    tave = minAveMaxTobsList[1]
    tmax = minAveMaxTobsList[2]

    return jsonify(tmin, tave, tmax)

@climateApp.route("/api/v1.0/<start>/<end>")
def tobs_start_end(start, end):
    """ Return TMIN, TAVE, and TMAX for dates between startDate and endDate inclusive."""

    # Query all tobs between startDate and endDate inclusive
    min_ave_max_tobs = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    # Convert list of tuples into normal list
    min_ave_max_tobs_list = list(np.ravel(min_ave_max_tobs))

    tmin = min_ave_max_tobs_list[0]
    tave = min_ave_max_tobs_list[1]
    tmax = min_ave_max_tobs_list[2]

    return jsonify(tmin, tave, tmax)

if __name__ == '__main__':
    climateApp.run(debug=True)
    