# websdr_PI4
## Installation 
This experimental software has been tested on Raspberry Pi PiOS Bookworm and Ubuntu 24.04 LTS Linux systems.

### Download
You need to clone the package from github.com and run the software in the websdr_PI4 sub-directory. 
```
cd ~
git clone https://github.com/g3zil/websdr_PI4.git
cd ~/websdr_PI4
```
Execute all further commands in the ~/websdr_PI4 directory.
Updates can be downloaded with:
```
git pull
```

### Requirements
The shell script requirements are listed in the bash_requirements.txt file.
Any missing modules are loaded one by one when you first run the script setup.sh.
Run script using sudo, which may need your password:
```
sudo ./setup.sh
```

#### Open environments
The python modules requirements are listed in the python_requirements.txt file.
These can be installed with:
```
python3 -m pip install -r python_requirements.txt
```
#### Externally managed environment
```
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r python_requirements.txt
```

## Instructions for setting up and operation
Full details are in the PI4_log_readme.txt file.\
Suggest you have that file open in a window as you set up in another.

## Architecture of the application: Shell script and python scripts
This experimental software aims to:\
\
a) Detect [PI4-encoded](https://rudius.net/oz2m/ngnb/pi4.htm) digital mode signals from microwave beacons by correlating the incoming 4-tone signal with the PI4 sync vector and gioving a score of 0-4 for the number of tines at the expected frequencies. The correlation code is a variant for PI4 I wrote based on the version for JT4 by [Daniel Estevez](https://github.com/daniestevez/jupyter_notebooks/blob/master/dslwp/JT4G%20detection.ipynb), used with kind permission.\
\
b) Measure the signal + noise (splusn) level during the carrier interval.\
\
c) Measure the noise using an FFT frequency domain algorithm during the pause.

The diagram below outlines the data flow from a web browser connected to a websdr, through WSJT-X, to the scripts comprising this websdr_PI4 application. The database is hosted by the WsprDaemon group and access to the Grafana visulaization tool is available on request.

![24GHz WebSDR Monitoring](https://github.com/user-attachments/assets/d51133b6-2ca3-4b3e-8219-f1239d9d6394)
