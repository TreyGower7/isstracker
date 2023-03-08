from flask import Flask, request
import json
import xmltodict
import requests 
import math
import yaml
import time
from geopy.geocoders import Nominatim

"""getting iss trajectory data and doing calculations 

This script gets the data from an xml file from NASA and imports the data. Then we store the cordinates in vectors(lists) for specific epochs in the data set. Where we then want to do some basic calculations.

Typical Usage Example:

    first get the epoch you want from the list using:
        curl localhost:5000/epochs
    then use the epoch to calculate some data:
        curl localhost:5000/epochs/2023-061T12:00:00.000Z/speed
        [
        7.659431437012692
        ]   
"""
app = Flask(__name__)

@app.route('/help', methods=['GET'])
def help() -> str:
    """Provides a manual for the user

    Args:
        None
    Returns:
        Help string with useful path data

    """
    get_help = """Usage:  curl [Localhost ip]:5000/[Path]\n
            A general utility for iss_tracking and paths\n
Path Options:\n
            (1)  / (gets all data from the ISS)\n
            (2)  /epochs (gets all epochsfrom the ISS)\n
            (3)  /epochs?limit=int&offset=int  (Return modified list of Epochs given query parameters)\n
            (4) /epochs/<epoch> (return a specific epoch given a date and time)\n
            (5) /epochs/<epoch>/speed (Return instantaneous speed for a specific Epoch)\n
            (6) /delete-data (Deletes all data from data set)\n
            (7) /post-data  (Reloads all data from data from the web)\n
***End Help Section For ISS Tracking***\n"""
    return get_help 

@app.route('/', methods=['GET']) 
def get_data():
    """From the NASA website this function retrieves data
    
    Args:
        None

    Returns:
        A dictionary named iss_data containing the data imported from an xml file using python requests library
        **Can also return a string if the data does not get retrieved**
    """
    url = 'https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml'
    response = requests.get(url)
    if response.status_code == 200:
        iss_data = xmltodict.parse(response.text)
        return iss_data
    else:
        return 'failed to retrieve data'


@app.route('/status', methods=['GET'])
def data_status() -> dict:
    """Gets trajectory data from ISS and checks status of deletion
    Args:
        None
    Returns:
        iss_data (dict) dictionary containing data from nasa
    """
    if iss_data == {}:
        return 'Data was deleted (use path /post-data to fetch it)'
    else:
        return iss_data

@app.route('/comment', methods=['GET'])
def get_comment() -> list:
    """
    Getting the comment data from the xml file from NASA

    Args:
        None
    Returns:
        list with the comment data
    """
    if iss_data == {}:
        return data_status()
    comments = iss_data['ndm']['oem']['body']['segment']['data']['COMMENT']
    return comments

@app.route('/header', methods=['GET'])
def get_header() -> dict:
    """
    Getting the header data from the xml file from NASA

    Args:
        None
    Returns:
        dictionary with the header data
    """
    if iss_data == {}:
        return data_status()
    header = iss_data['ndm']['oem']['header']
    return header

@app.route('/metadata', methods=['GET'])
def get_metadata() -> dict:
    """
    Getting the meta data from the xml file from NASA

    Args:
        None
    Returns:
        dictionary with the meta data
    """
    if iss_data == {}:
        return data_status()
    metadata = iss_data['ndm']['oem']['body']['segment']['metadata']
    return metadata

@app.route('/epochs', methods=['GET'])
def get_epochs() -> list:
    """Seperates all epochs from dictionary of iss_data
    Args:
        None
    Returns: 
        A list named epochs of all the epochs in the data set
    """
    if iss_data == {}:
        return data_status()
    epoch_data = []
    for x in range(L):
        epoch_data.append(iss_data['ndm']['oem']['body']['segment']['data']['stateVector'][x]['EPOCH'])
   
    offset = request.args.get('offset',0)
    limit = request.args.get('limit',0)
    if offset or limit:
        try:
            offset=int(offset)
            limit = int(limit)
        except ValueError:
            return f'invalid input, must be numeric'
    if offset < 0:
        offset ==0
    for i in range(offset-1,-1,-1):
        epoch_data.pop(i)
    if limit != 0:
        while len(epoch_data) > limit:
            epoch_data.pop(-1)
    return epoch_data

@app.route('/epochs/<epoch>', methods=['GET'])
def vec_epochs(epoch) -> list:
    """isolates an epoch from the list of epochs
    Args:
        epoch (a specific epoch we want to look at)

    Returns:
        A vector(list of dictionaries) named spec_epoch returning data for a single epoch
    """
    if iss_data == {}:
        return data_status()

    spec_epoch = []
    epoch_data = iss_data['ndm']['oem']['body']['segment']['data']['stateVector']
    for x in range(len(epoch_data)):
        if epoch == str(epoch_data[x]['EPOCH']):
            spec_epoch = epoch_data[x]
            return spec_epoch

@app.route('/epochs/<epoch>/speed', methods=['GET'])
def speed_epoch(epoch) -> list:
    """Calulates speed for a specific epoch vector
    Args:
        epoch (a specific epoch we want to calculate for)

    Returns:
       dictionary containing speed for instantaneous speed at a given epoch
    """
    if iss_data == {}:
        return data_status()

    spec_epoch = vec_epochs(epoch)
    z_dot = float(spec_epoch['Z_DOT']["#text"])
    y_dot = float(spec_epoch['Y_DOT']["#text"])
    x_dot = float(spec_epoch['X_DOT']["#text"])
    speed = math.sqrt(x_dot**2 + y_dot**2 + z_dot**2)
    return {'Speed': speed}

@app.route('/delete-data', methods=['DELETE'])
def delete_data() -> str:
    """Deletes all data in the list iss_data
    Args:
        None

    Returns:
        a message string
    """
    global iss_data
    iss_data.clear()
    return 'data cleared'

@app.route('/post-data', methods=['POST'])
def post_data() -> str:
    """Retrieves all data from NASA into iss_data
    Args:
        None

    Returns:
        a message string
    """
    global iss_data
    iss_data = get_data()
    return 'Data Posted'

def get_config() -> dict:
    """
    Function attempts to find a configuration for the user if not we use the default configuration
    Args:
        none
    Returns:
        dictionary with configuration information such as debug setting.
    """
    default_config = {"debug": True}
    try:
        with open('config.yaml', 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Couldn't load the config file; details: {e}")
    return default_config

@app.route('/epochs/<epoch>/location', methods=['GET'])
def get_location(epoch) -> dict:
    """
    Retrieves location data from a specific epoch
    Args:
        epoch (a list of dictionaries with a specific epoch and its data)
    returns:
        Returns a dictionary with latitude, longitude, altitude, and geoposition for given Epoch
    """
    data = vec_epochs(epoch)
    time = get_time(epoch)
    x = float(data['X']['#text'])
    y = float(data['Y']['#text'])
    z = float(data['Z']['#text'])
    lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2)))
    lon = math.degrees(math.atan2(y, x)) - ((time['hrs']-12)+(time['mins']/60))*(360/24) + 24
    alt = math.sqrt(x**2 + y**2 + z**2) - 6371
    lon = lon_correction(lon)
    geocoder = Nominatim(user_agent='iss_tracker')
    geoloc = geocoder.reverse((lat,lon), zoom=15, language='en')
    if geoloc == None:
        location= 'Somewhere over the ocean'
    else:
        location = {'Address': geoloc.address}
    geodata= {'latitude': lat,'longitude': lon, 'altitude': alt, 'geoposition': location}
    return geodata

@app.route('/now', methods=['GET'])
def get_now() -> dict:
    """
    Based on current data provided by NASA gets the closest ISS epoch data based on your currrent time of day
    Args:
        none
    Returns:
        dictionary of the closest epoch, the geopositional data, and speed
    """
    prevdiff = 0;
    for epoch in get_epochs:
        time_now = time.time()
        time_close = get_time(epoch)
        time_diff = math.abs(time_now-time_close['sec'])
        if time_diff < prevdiff:
            nearest = [vec_epochs(epoch), time_close]
        prevdiff = time_diff
#***need to add code to get positional data and stuff for nearest epoch now***

def lon_correction(lon):
    """
    This funtion serves to adjust longitude if it deviates outside of -180 deg => 180 deg by normalizing the value
    Args: 
        lon (the uncorrected longitudinal value)
    returns:
        An integer (lon) of the corrected longitudinal value
    """
    while lon >= 180:
        lon -= 360
    while lon <= -180:
        lon += 360

    return lon

def get_time(epoch):
        """
        Getting the time from each epoch and then converting to seconds
        Args:
            epoch (the data for a given date/time)
        returns:
            A dictionary containing time taken from the epoch key
        """
        time=epoch
        hrs = int(time[9:11])
        mins = int(time[12:14])
        sec = time.mktime(time.strptime(epoch[:-5], '%Y-%jT%H:%M:%S'))
        return {'hrs':hrs, 'mins': mins, 'sec': seconds} 

#global trajectory data variable and length
iss_data = get_data()
L = len(iss_data['ndm']['oem']['body']['segment']['data']['stateVector'])

if __name__ == '__main__':
    config = get_config()
    if config.get('debug', True):
        app.run(debug=True, host='0.0.0.0')
    else:
        app.run(host='0.0.0.0')
