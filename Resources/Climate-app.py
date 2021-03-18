import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

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
    return (
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"Insert on the last two routes the dates only in format 'YYYY-MM-DD', otherwise it won't work out"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    all_precipitation = []

    for date, prcp in results:
        prec_dict = {}
        prec_dict[date] = prcp
        all_precipitation.append(prec_dict)
    
    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    results1 = session.query(Station.station).all()
    session.close()
    return jsonify(results1)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    st2 = "USC00519397"
    y_tobs1 = session.query(Measurement.date, Measurement.station, Measurement.tobs).\
        filter(Measurement.station == st2).filter(Measurement.date > query_date).all()
    session.close()

    precip_dict = []

    for date, station, tobs in y_tobs1:
        y_tobs = {}
        y_tobs[date] = tobs, station
        precip_dict.append(y_tobs)
    
    return jsonify(precip_dict)

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    sstobs = []
    for tmin,tavg,tmax in query:
        sttob = {}
        qtob = {}
        qtob["Min"] = tmin
        qtob["Avg"] = tavg
        qtob["Max"] = tmax
        sttob[start] = qtob
        sstobs.append(sttob)
    return jsonify(sttob)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):

    session = Session(engine)
    query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()

    sstobs = []
    for tmin,tavg,tmax in query:
        strt_tob = {}
        qtob = {}
        qtob["Min"] = tmin
        qtob["Avg"] = tavg
        qtob["Max"] = tmax
        strt_tob[str(start) + "/" + str(end)] = qtob
        sstobs.append(strt_tob)

    return jsonify(strt_tob)

if __name__ == '__main__':
    app.run(debug=True)