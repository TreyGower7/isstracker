# Interesting ISS Trajectory Data

folder contents / project objective
-----------------------------
Folder contains 1 .py script iss_tracker.py. The objective is to feed in the data, query it and return more interesting data we can do calculations with.

Data Access
-----------------------------
using the the iss_tracker python script and pythons import requests library we access and get data from the data set found here: 'https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml'. The download contains data in 4 minute intervals of position, and velocity of the iss.

Description of Scripts
-----------------------------
The script iss_tracker.py gets the data from an xml file from NASA and imports the data. Then we store the cordinates in vectors(lists) for specific epochs in the data set. Then, this data is used to do some basic calculations.

Instructions on Use Using Existing Docker Image
-----------------------------
In your linux environment run the command:   
```sh  
docker pull tagower/iss_tracker:hw05
```
then to ensure the image exists:
```sh  
docker images
```
then we run it
```sh  
docker run -it --rm -p 5000:5000 tagower/iss_tracker:hw05
```
***Now Refer To Correct Ports and Example Outputs Section***

Instructions on Use Building A New Docker Image
-----------------------------
In your linux environment run the command: 
```sh  
wget https://github.com/TreyGower7/coe322-trey/blob/main/homework05/iss_tracker.py
```
then we need to create our docker build by creating a new file and writing some commands in.
```sh  
vi Dockerfile
```
Next what commands to use:

FROM python:3.8.10

RUN pip install Flask==2.2.2
RUN pip install xmltodict==0.13.0
RUN pip install requests==2.22.0

COPY iss_tracker.py /iss_tracker.py

CMD ["python", "iss_tracker.py"]

***To ensure it runs properly DO NOT change from Python version 3.8.10 or Flask 2.2.2 (unless you are editing the code to run with newer versions)***
Now to build: 
```sh  
docker build -t username/iss_tracker:hw05 .
```
then to find your newly built image:
```sh  
docker images
```
and to run the image:
```sh  
docker run -it --rm -p 5000:5000 <username>/iss_tracker:<yourtag> 
```
***Now Refer To Correct Ports and Example Outputs Section***

Correct Ports and Example Outputs
-----------------------------
Ensure when curling an image you use the second ip listed in green box (It could be different for you).

<img width="842" alt="Screenshot 2023-02-26 at 9 38 31 PM" src="https://user-images.githubusercontent.com/70235944/221581571-f313db39-6111-4ec8-ad5b-ed4c9d2e7fcb.png">

Example Outputs:

* For all paths usecurl localhost:5000/help

	To Delete or Post Data from the iss trajectory:
```sh
curl -X POST <GreenBoxIP>:5000/post-data 
```	
or  
```sh  
curl -X DELETE <GreenBoxIP>:5000/delete-data
```
Outputs a string verifying status of the data such as: Data Delete
	
Other examples:
	curl localhost:5000/epochs
        returns all epochs in the data set (a big list!)
	or
```sh 
curl localhost:5000/epochs/<specific epoch you want from epoch data set>
```
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
    
	 [
        7.659431437012692
        ]   
Data and Unit Information
-----------------------------
All data being reported in each epoch has units time, km, km/s respectively. Where the epoch is time and date X,Y,Z is in km and X_DOT,Y_DOT, and Z_DOT are all in km/s. 

***When curling the speed function speed is returned in km/s as well.***
