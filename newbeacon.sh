#!/bin/bash
### This bash script is run whenever a new beacon is to be minitored, either when first used, or on change of beacon
### It needs three command line parameters, the beacon callsign and grid location and the id for the receiver e.g.
### ./new_beacon.sh PA3GCO JO01MT TRIG01/G3ZIL 
### The other metadata is assumed to be for the Kent WebSDR

TX_CALL=$1
TX_GRID=$2
RX_ID=$3

BASE_DIR=$(pwd)
DATE=$(date -u +%Y-%m-%dT%H:%M:00Z)
META_DATA="1.25,,,,,,,,${RX_ID},JO01qj,51.396,1.375,,,,,"

echo "${DATE},${TX_CALL},${TX_GRID},${META_DATA}" >${BASE_DIR}/spots_azi.csv
