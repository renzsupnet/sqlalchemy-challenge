# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, desc, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def homepage():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs"     
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Calculate the date for the last 12 months of data
    most_recent_date = session.query(Measurement.date).order_by(desc(Measurement.date)).first()
    date_str = most_recent_date[0]
    date_obj = dt.datetime.strptime(date_str, '%Y-%m-%d')
    one_year_ago = date_obj - dt.timedelta(days=365)
    one_year_ago = one_year_ago.strftime('%Y-%m-%d')

    # Perform a query to retrieve the data and precipitation scores
    data = session.query(Measurement.date, Measurement.prcp).filter(
        Measurement.date >= one_year_ago
    ).order_by(Measurement.date).all()

    # Extracting values from data
    data_val = {}
    for val in data:
        data_val[val[0]] = val[1]
    
    return jsonify(data_val)


@app.route("/api/v1.0/stations")
def stations():

    # Query to retrieve stations
    data = session.query(Station.station).all()

    # Extracting values from data
    data_val = []
    for val in data:
        data_val.append(val[0])

    return jsonify(data_val)

@app.route("/api/v1.0/tobs")
def tobs():

    # Calculate the date for the last 12 months of data
    most_recent_date = session.query(Measurement.date).order_by(desc(Measurement.date)).first()
    date_str = most_recent_date[0]
    date_obj = dt.datetime.strptime(date_str, '%Y-%m-%d')
    one_year_ago = date_obj - dt.timedelta(days=365)
    one_year_ago = one_year_ago.strftime('%Y-%m-%d')

    # Query to retrieve the most active station
    most_active_station = session.query(
    Station.station
    ).filter(Station.station == Measurement.station)\
    .group_by(Station.station).order_by(desc(func.count(Measurement.station))).all()[0][0]

    # Query to retrieve the temperature observations for the last 12 months of data
    data = session.query(
        Measurement.date, Measurement.tobs
    ).filter(Measurement.date >= one_year_ago).order_by(Measurement.date).all()

    # Extracting values from data
    data_val = {}
    for val in data:
        data_val[val[0]] = val[1]
    
    return jsonify(data_val)

@app.route("/api/v1.0/<start>")
def stat_starting_from(start):

    # Aggregated functions
    sel = [
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
    ]

    # Query to retrieve the min, max and average tobs
    data = session.query(*sel).filter(Measurement.date >= start).all()

    # Extracting values from data
    data_val = {}
    for val in data:
        data_val["TMIN"] = val[0]
        data_val["TMAX"] = val[1]
        data_val["TAVG"] = val[2]
    
    return jsonify(data_val)

@app.route("/api/v1.0/<start>/<end>")
def stat_from_to(start, end):

    # Aggregated functions
    sel = [
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
    ]

    # Query to retrieve the min, max and average tobs between start and end
    data = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Extracting values from data
    data_val = {}
    for val in data:
        data_val["TMIN"] = val[0]
        data_val["TMAX"] = val[1]
        data_val["TAVG"] = val[2]
    
    return jsonify(data_val)

if __name__ == '__main__':
    app.run(debug=True)


session.close()


