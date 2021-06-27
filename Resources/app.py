
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np

from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    return(
        f"Available routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"Please, for both start and end dates enter them as 'YYYY-MM-DD'"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)

    prec = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > '2016-08-23').all()
    
    session.close()

    prcp_list = []
    for d,p in prec:
        prcp_dict = {}
        prcp_dict[d] = p
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    records = session.query(Station.station).all()
    
    session.close()

    stations = []
    for station in records:
        stations.append(station)

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    st1 = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]
    
    records = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == st1).\
        filter(Measurement.date > '2016-08-23').all()

    all_tobs = []
    for d,t in records:
        st_tob = {}
        re_tob = {}
        re_tob[d] = t
        st_tob[st1] = re_tob
        all_tobs.append(st_tob)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def start_date(start):

    session = Session(engine)

    query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    session.close()
    
    start_tobs = []
    for tmin,tavg,tmax in query:
        strt_tob = {}
        query_tob = {}
        query_tob["Min"] = tmin
        query_tob["Avg"] = tavg
        query_tob["Max"] = tmax
        strt_tob[start] = query_tob
        start_tobs.append(strt_tob)
    
    return jsonify(strt_tob)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):

    session = Session(engine)

    query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    session.close()
    
    start_tobs = []
    for tmin,tavg,tmax in query:
        strt_tob = {}
        query_tob = {}
        query_tob["Min"] = tmin
        query_tob["Avg"] = tavg
        query_tob["Max"] = tmax
        strt_tob[str(start) + "/" + str(end)] = query_tob
        start_tobs.append(strt_tob)
    
    return jsonify(strt_tob)

if __name__ == '__main__':
    app.run(debug=True)