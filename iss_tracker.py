from flask import Flask, request
import json
import xmltodict
import requests 
import math

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
        A vector(list) named spec_epoch taken from specific data in the list of epochs
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

#global trajectory data variable and length
iss_data = get_data()
L = len(iss_data['ndm']['oem']['body']['segment']['data']['stateVector'])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
