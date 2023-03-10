# Tracking The Swiftly Soaring Space Station (The ISS)

Project Objective
-----------------------------
The objective is to feed in data from NASA using python requests library, query it, and return data that tracks the geopostion.

Description of Files
-----------------------------
The Python script iss_tracker.py gets the NASA data from an xml file from NASA and imports the data. Then we store the coordinates in vectors or lists for specific epochs (the date and time of the trajectory data) in the data set. Then, this data is used to do useful calculations for geo position (where the ISS is relative to earth) and speed.

The Dockerfile is used to capture the docker image. The file specifies the Python version, and downloads any libraries used in the python script that needs to be installed to run the application. 

The docker-compose.yml file is extremely useful as it saves the user (you) from having to type in tricky commands to run the docker image. Instead it wraps the information for the docker image into one file and runs it with a simple command.

Data Access
-----------------------------
Using the the iss_tracker python script and pythons import requests library we access and get data from the data set found here: 'https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml'. The download contains data in 4 minute intervals of position, and velocity of the ISS Space Station.

Full website here: https://spotthestation.nasa.gov/trajectory_data.cfm

Instructions on Use Using Existing Docker Image
-----------------------------
In your linux environment run the command:
	
	wget https://github.com/TreyGower7/isstracker/blob/main/docker-compose.yml
then:
```sh  
docker pull tagower/iss_tracker:midterm
```
then to ensure the image exists:
```sh  
docker images
```
***You should see image by tagower named: iss_tracker with tag: midterm***
then we run it with our docker-compose.yml file included in this repository
```sh  
docker-compose up
```
***Now Refer To Correct Ports and Example Outputs Section***

Instructions on Use Building A New Docker Image
-----------------------------
To get the files, in your linux environment run the command: 
```sh  
git clone https://github.com/TreyGower7/isstracker.git
```
now using the included Dockerfile we build:
```sh  
docker build -t <username>/iss_tracker:<yourtag> .
```
then to find your newly built image:
```sh  
docker images
```
and to run the image:
```sh  
docker-compose up
```
Another option to run:
```sh  
docker run -it --rm -p 5000:5000 <username>/iss_tracker:<yourtag> 
```
***Now Refer To Correct Ports and Example Outputs Section***

Correct Ports and Example Outputs
-----------------------------
Ensure when curling an image you use the second ip listed in green box (IP could be different for you).

<img width="842" alt="Screenshot 2023-02-26 at 9 38 31 PM" src="https://user-images.githubusercontent.com/70235944/221581571-f313db39-6111-4ec8-ad5b-ed4c9d2e7fcb.png">

Example Outputs:

*For a help screen containing all paths use 
```sh
curl <GreenBoxIP>/help
```

To Delete or Post Data from the iss trajectory:

```sh
curl -X POST <GreenBoxIP>:5000/post-data 
```	
or  
```sh  
curl -X DELETE <GreenBoxIP>:5000/delete-data
```
Outputs a string verifying status of the data such as: Data Deleted
	
Other examples:
	curl localhost:5000/epochs
        returns all epochs in the data set (a big list!)
	or
```sh 
curl localhost:5000/epochs/<specific epoch you want from epoch data set>
```
Output:	
	{
  	"EPOCH": "2023-061T12:00:00.000Z",
  	"X": {
    		"#text": "3578.8574821437401",
    		"@units": "km"
  	},
  	"X_DOT": {
    		"#text": "5.03904352218286",
    		"@units": "km/s"
  	},
  	"Y": {
    		"#text": "-5454.7252313410299",
    		"@units": "km"
  	},
  	"Y_DOT": {
    		"#text": "1.32725609415084",
    		"@units": "km/s"
  	},
  	"Z": {
    		"#text": "1908.4598652639199",
   		 "@units": "km"
  	},
  	"Z_DOT": {
    		"#text": "-5.6136727354188301",
    		"@units": "km/s"
  	}
	}		

or

```sh 	
curl localhost:5000/epochs/2023-061T12:00:00.000Z/speed
```
Output:
	 [
        7.659431437012692
        ] 
	
Location path example: 
```sh 	
curl <GreenboxIP>:5000/now
```
Output:	
{
  "Location": {
    "altitude": {
      "units": "km",
      "value": 421.71468241492767
    },
    "latitude": 19.826402294406098,
    "longitude": -110.99463933219616
  },
  "Speed": {
    "units": "km/s",
    "value": 7.665369813786189
  },
  "closest_epoch": "2023-069T05:12:00.000Z",
  "geo": "Somewhere over the ocean",
  "seconds_from_now": -16.571338891983032
}

Data and Unit Information
-----------------------------
All data being reported in each epoch has units time, km, km/s respectively. Where the epoch is time and date X,Y,Z is in km and vector <X_DOT,Y_DOT,Z_DOT> is in km/s. 

Longitude and latitude are given in degrees based on the earch. Altitude is a distance extending in the normal direction from earth to the ISS.

***When curling the speed function speed is returned in km/s as well.***
