#!/bin/bash
### This bash script uses the linux sound utility to determine rms noise level during 40-45 seconds in  a PI4 mixed mode sequence
### See https://rudius.net/oz2m/ngnb/pi4.htm for description of the sequence. So time interval is 49 s to 59 s.
### Basic functional pilot   Gwyn G3ZIL Oct-Nov 2024
### Single command line argument is wav file name in default path
### This version for Raspberry Pi

# set up directory and file where wav file found and temporary files written and set mode to CW for carrier
BASE_DIR=/users/gxg/desktop/PI4
WAV_DIR=${BASE_DIR}/save
MODE=PI4

# get the date in format for database
DECODE_CAPTURE_DATE=$(date -u -v-1M +%Y-%m-%dT%H:%M:00Z) 

# The noise level part. This is dB on arbitary scale dependent on WebSDR/Browser/WSJT-X signal level - unsatisfactory I know, but this is pilot!
# Use of sox and RMS in trough of 50 milliseconds is well documented in Griffiths et al. in QEX for WSPR
#/usr/local/bin/sox ${WAV_DIR}/$1 -n stat
/usr/local/bin/sox ${WAV_DIR}/$1 ${BASE_DIR}/trimmed.wav trim 40 5                                        # trim time interval to 40 to 40+5 seconds 
/usr/local/bin/sox ${BASE_DIR}/trimmed.wav ${BASE_DIR}/filtered.wav sinc 1200-2000                         # sinc bandpass filter away from carrier 
NOISE=$(/usr/local/bin/sox ${BASE_DIR}/filtered.wav -n stats 2>&1 | grep 'RMS Tr dB' | awk '{print $4}')   # get stats, look for trough value quietest 50 ms and grab value
RMS_NOISE=$(/usr/bin/bc <<< "scale=2; $NOISE - 29")    # account for the 800 Hz bandwidth for noise measurement to get dB in 1 Hz

echo "RMS_NOISE (dB)= ${RMS_NOISE}"

# log current time, noise estimate and mode and save as csv
echo ${DECODE_CAPTURE_DATE}","${MODE}","${RMS_NOISE} >${BASE_DIR}"/noise.csv"
