#!/bin/bash
### This bash script with python parts detects (sic - no decode, yet)and uploads PI4 data from Margate 24 GHz SDR
### to a table in tutorial database on WD1
### Basic functional prototype based on jt4 original by Gwyn G3ZIL Oct 2024 - August 2025
### V1.1 for Ubuntu 24.04 and Raspberry Pi Bookworm

########################################################
# Only user-set installation variables are in this block
########################################################
# set up receiver details to go into database table via python
RX_GRID=JO01qj           #  Maidenhead for Margate WebSDR, not where browser is located!
RX_ID=TRIG01/G3ZIL       # The /G3ZIL is a suggested addition, use your callsign to show who is using WebSDR
# alternate receiver that may hear the PI4 beacon
# RX_ID=SHBRG/G3ZIL      # This is SDR at http://sdr.shbrg.nl:8074/ The /G3ZIL is a suggested addition, use your callsign to show who is using it
# RX_GRID=JO21PR
########################################################
# set up base directory and where wav file from WSJT-X JT4 mode selected will reside
BASE_DIR=$(pwd)
PI4_WAV_DIR=${BASE_DIR}/save  #  This is where wsjtx puts the wav file. Note we have to swap setting in wsjtx from jt4!

########################################################
# main code
#######################################################

DECODE_CAPTURE_DATE=$(date -u  +%Y-%m-%dT%H:%M:00Z)                   # easier to get time in required format this way
WAV_FILE=$(ls -ltr ${BASE_DIR}/save| tail -n 1 | awk '{print $9}')    # get the PI4  wav file name to process, every minute
WAV_FILE_TIME=$(ls -ltr ${BASE_DIR}/save| tail -n 1 | awk '{print substr($9, 8,4)}')
LAST_MINUTE=$(date -u  +%Y-%m-%dT%H:%M:00Z --date '-1 min')
echo "File time ${WAV_FILE_TIME}  last minute time ${LAST_MINUTE}"

# if [[ ${WAV_FILE_TIME} = ${LAST_MINUTE} ]]
if [[ ${WAV_FILE_TIME} != ${LAST_MINUTE} ]]
then
    echo 'New data file - so detect PI4 and estimate noise'
    echo "Detection program processing file "${WAV_FILE}
    sox ${BASE_DIR}/save/${WAV_FILE} ${BASE_DIR}/trimmed.wav trim 0 25    # The PI4 tones are in first 25 seconds
    sox ${BASE_DIR}/trimmed.wav -r 12000 ${BASE_DIR}/12000.wav            # resample to 12000 sps for PI4
    /usr/bin/python3 ${BASE_DIR}/PI4_detect.py ${DECODE_CAPTURE_DATE} ${BASE_DIR}/12000.wav  > ${BASE_DIR}/PI4_detect.log   # do the processing!
    ${BASE_DIR}/sn_calc.sh ${WAV_FILE}                                # script uses SOX to estimate RMS noise
    paste -d "," ${BASE_DIR}/noise.csv ${BASE_DIR}/PI4_detections.csv >${BASE_DIR}/temp.csv  # put both csv data sets on one line
    awk -F"," -v OFS="," -v tx_call="${TX_CALL}" -v tx_call="${TX_CALL}" -v tx_grid="${TX_GRID}" -v band="${BAND}" -v frequency="${FREQUENCY}" \
     -v rx_id="${RX_ID}" -v rx_grid="${RX_GRID}" ' {print $1,tx_call,tx_grid,band,frequency,rx_id,rx_grid,$2,$3,$5,$6,$7,$8,$9,$10,$11,$12,$13}' \
     <${BASE_DIR}/temp.csv >${BASE_DIR}/data.csv
    cat ${BASE_DIR}/data.csv
    /usr/bin/python3 ${BASE_DIR}/PI4_upload.py ${BASE_DIR}/data.csv       # uploads to database with mode ident PI4 together with metadata
else
  echo "Stale file - possibly WSJT-X not running"
fi

# Tidy up wav files, keep just last 10
# rm -v -f $(ls -1t ${BASE_DIR}/save/*.wav | tail -n +11)

echo "Processing complete"
