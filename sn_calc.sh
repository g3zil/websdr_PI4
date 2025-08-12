#!/bin/bash
### This bash script uses the linux sound utility to determine rms noise level during 40-45 seconds in  a PI4 mixed mode sequence
### See https://rudius.net/oz2m/ngnb/pi4.htm for description of the sequence. So time interval is 49 s to 59 s.
### Basic functional pilot   Gwyn G3ZIL Oct 2024 - August 2025
### Single command line argument is wav file name in default path
### This version for Ubuntu 24.04 and Raspberry Pi Bookworm

# set up directory and file where wav file found and temporary files written and set mode to CW for carrier
BASE_DIR=$(pwd)
WAV_DIR=${BASE_DIR}/save
MODE=PI4

# get the date in format for database
DECODE_CAPTURE_DATE=$(date -u +%Y-%m-%dT%H:%M:00Z --date '-1 min') 

# The noise level part. This is dB on arbitary scale dependent on WebSDR/Browser/WSJT-X signal level - unsatisfactory I know, but this is pilot!
# Use of sox and RMS in trough of 50 milliseconds is well documented in Griffiths et al. in QEX for WSPR

sox ${WAV_DIR}/$1 ${BASE_DIR}/trimmed.wav trim 40 5                                         # trim time interval to 40 to 40+5 seconds 
sox ${BASE_DIR}/trimmed.wav ${BASE_DIR}/filtered.wav sinc 1200-2000                         # sinc bandpass filter away from carrier 
NOISE=$(sox ${BASE_DIR}/filtered.wav -n stats 2>&1 | grep 'RMS Tr dB' | awk '{print $4}')   # get stats, look for trough value quietest 50 ms and grab value
RMS_NOISE=$(/usr/bin/bc <<< "scale=2; $NOISE - 29")                                         # account for 800 Hz noise measurement bw to get dB in 1 Hz

# The FFT noise part. This uses essentially same algorithm as in wsprdaenon: sum lowest 30% of fourier coefficients in band 373 Hz to 2933 Hz
FFT_NOISE=$(python3 fft_noise.py ${WAV_DIR}/$1)

echo "RMS_NOISE (dB)= ${RMS_NOISE}"
echo "FFT_NOISE (dB)= ${FFT_NOISE}"

# The signal+noise level part. This is dB on arbitary scale dependent on WebSDR/Browser/WSJT-X signal level - unsatisfactory I know, but this is pilot!

sox ${WAV_DIR}/$1 ${BASE_DIR}/trimmed.wav trim 46 13                                        # trim time interval to the carrier interval 46 to 19 s 
sox ${BASE_DIR}/trimmed.wav ${BASE_DIR}/filtered.wav sinc 750-850                           # sinc bandpass filter around the carrier
SPLUSN=$(sox ${BASE_DIR}/filtered.wav -n stats 2>&1 | grep 'RMS lev dB' | awk '{print $4}') # get stats, look for RMS level and grab value

echo "RMS_SIGNAL+NOISE (dB)= ${SPLUSN}"
# log current time, noise and signal plus noise level estimates and mode and save as csv
echo ${DECODE_CAPTURE_DATE}","${MODE}","${RMS_NOISE}","${FFT_NOISE}","${SPLUSN} >${BASE_DIR}"/noise.csv"
