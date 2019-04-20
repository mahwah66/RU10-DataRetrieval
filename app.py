import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to our Hawaii Weather Station data page. Available routes are:<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br>"
        f"/api/v1.0/&lt;start&gt; or /api/v1.0/&lt;start&gt;/&lt;end&gt;<br>"
        f"<div style='margin-left:20px';>where &lt;start&gt; and &lt;end&gt; are dates in the format YYYY-mm-dd<br>"
        f"examples:<br>"
        f"<a href='/api/v1.0/2017-06-01'>/api/v1.0/2017-06-01</a><br>"
        f"<a href='/api/v1.0/2016-01-01/2016-01-07'>/api/v1.0/2016-01-01/2016-01-07</a>"
    )


@app.route("/api/v1.0/precipitation")
def dateprecip():
    """Return a list of dates/rainfalls"""
    # Query from the first part about dates and rainfall
    latest = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # trying not to hardcode by using date, but relying on format 'y-m-d'  
    ymd = latest[0].split('-')
    querydate = dt.date(int(ymd[0]), int(ymd[1]), int(ymd[2])) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= querydate).order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of all_dates
    all_dates = []
    for date, prcp in results:
        mydict = {}
        mydict["date"] = date
        mydict["precipitation"] = prcp
        all_dates.append(mydict)

    return jsonify(all_dates)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""
    # Query all passengers
    results = session.query(Measurement.station, Station.name).filter(Measurement.station == Station.station).group_by(Measurement.station).all()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_stations= []
    for station, name in results:
        sdict = {}
        sdict["station"] = station
        sdict["name"] = name
        all_stations.append(sdict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def stationobs():
    """Return most recent year of temp observations from most active station"""
    # Query most acitve station and get one year from latest date
    actstation = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.tobs).desc()).first()[0]
    tlatest = session.query(Measurement.date).filter(Measurement.station==actstation).order_by(Measurement.date.desc()).first()
    tymd = tlatest[0].split('-')
    tquerydate = dt.date(int(tymd[0]), int(tymd[1]), int(tymd[2])) - dt.timedelta(days=365)

    # Perform a query to retrieve the temperature observations
    tobsinfo = session.query(Measurement.tobs).filter(Measurement.station==actstation).filter(Measurement.date >= tquerydate)
    tobsL=[ob[0] for ob in tobsinfo]
    return jsonify(tobsL)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def tminmaxavg(start, **kwargs):

    def checkinput(str):
        try:
            t = dt.datetime.strptime(str,'%Y-%m-%d')
            return True
        except ValueError as err:
            return False

    if not checkinput(start):
        return jsonify({"error": "Input for start date not recognized as date format."}), 404
    
    # get last date from db for error checking or default end date
    lastdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    if "end" in kwargs:
        end = kwargs["end"]
        if not checkinput(end):
            return jsonify({"error": "Input for end date not recognized as date format."}), 404
    
    else:
        end = lastdate
    
    # no data beyond lastdate
    if lastdate<start:
        fstr="No data recorded for input date period. Last date on record is "+lastdate
        return jsonify({"error": fstr}), 404
    
    # modify end to lastdate if needed so page returned shows proper data period
    if end > lastdate:
        end = lastdate
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    tdict = {}
    tdict["tmin"] = results[0][0]
    tdict["tavg"] = results[0][1]
    tdict["tmax"] = results[0][2]
    
    retdict={"begin":start, "end":end, "temps":tdict}
    return jsonify(retdict)


if __name__ == '__main__':
    app.run(debug=True)
