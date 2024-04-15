import numpy as np

import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#  Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

# Create Flask app
app = Flask(__name__)

# Define route for homepage
@app.route('/')
def homepage():
    """Homepage - List all available routes"""
    return """
    <h1>Welcome to Climate App API!</h1>
    <h2>Available Routes:</h2>
    <ul>
        <li><a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a> - Precipitation data for the last year</li>
        <li><a href="/api/v1.0/stations">/api/v1.0/stations</a> - List of weather stations</li>
        <li><a href="/api/v1.0/tobs">/api/v1.0/tobs</a> - Temperature observations for the last year</li>
        <li>/api/v1.0/&lt;start&gt; - Min, Avg, and Max temperature for a given start date (format: YYYY-MM-DD)</li>
        <li>/api/v1.0/&lt;start&gt;/&lt;end&gt; - Min, Avg, and Max temperature for a given date range (format: YYYY-MM-DD/YYYY-MM-DD)</li>
    </ul>
    """

# Define route for precipitation data
@app.route('/api/v1.0/precipitation')
def precipitation():
    """Precipitation data for the last year"""
    # Perform query to retrieve precipitation data for the last year
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    
    # Convert query results to dictionary with date as key and prcp as value
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    
    return jsonify(precipitation_dict)

# Define route for weather stations
@app.route('/api/v1.0/stations')
def stations():
    """List of weather stations"""
    # Query to retrieve list of weather stations
    station_list = session.query(Station.station).all()
    
    # Convert query results to list
    stations = [station[0] for station in station_list]
    
    return jsonify(stations=stations)

# Define route for temperature observations
@app.route('/api/v1.0/tobs')
def tobs():
    """Temperature observations for the last year"""
    # Perform query to retrieve temperature observations for the most active station for the last year
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= one_year_ago).all()
    
    # Convert query results to list of dictionaries
    temperature_list = [{'Date': date, 'Temperature': tobs} for date, tobs in temperature_data]
    
    return jsonify(temperatures=temperature_list)

# Define route for temperature statistics for a given start date
@app.route('/api/v1.0/<start>')
def temperature_start(start):
    """Min, Avg, and Max temperature for a specified start date"""
    # Perform query to calculate temperature statistics for dates greater than or equal to start date
    temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    # Convert query results to dictionary
    temp_stats_dict = {
        'Min Temperature': temperature_stats[0][0],
        'Avg Temperature': temperature_stats[0][1],
        'Max Temperature': temperature_stats[0][2]
    }
    
    return jsonify(temp_stats_dict)

# Define route for temperature statistics for a given date range
@app.route('/api/v1.0/<start>/<end>')
def temperature_range(start, end):
    """Min, Avg, and Max temperature for a specified date range"""
    # Perform query to calculate temperature statistics for dates between start and end date
    temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    # Convert query results to dictionary
    temp_stats_dict = {
        'Min Temperature': temperature_stats[0][0],
        'Avg Temperature': temperature_stats[0][1],
        'Max Temperature': temperature_stats[0][2]
    }
    
    return jsonify(temp_stats_dict)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

