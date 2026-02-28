#!/bin/bash
# script to run Paul PE1LXX's PI4 decoder see 
# ./PE1LXX/decoder-options.txt and post at https://groups.io/g/PI-RX/topic/command_line_pi4_decoder/88555819?page=2
# One command line argument the file name, which includes the .wav 

FILE_NAME=$1
FILE_PATH='./save'
FILE=${FILE_PATH}/${FILE_NAME}

DECODE_DATE=$(date -u  "+%Y-%m-%d %H:%M:00")

echo "Processing wav file ${FILE} using PE1LXX PI4 decoder"  # Options use default 800 Hz carrier tone and capture +/-50Hz
./PE1LXX/pi-rx --freq 800 --capture 100 --width 3 ${FILE} > ./raw_decode.txt

if grep -q "MSG" ./raw_decode.txt; then                      # Valid decode message has a MSG prefix in the line we want, else do nothing and end
  # we have a decoded message
  DATA_LINE=$(grep -m 1 "MSG" ./raw_decode.txt)               # get the decode line itself then extract the data fields using awk         

  tx_call=$(echo "$DATA_LINE"   | awk -F'MSG='   '{split($2,a," "); print a[1]}')
  snr=$(echo "$DATA_LINE"   | awk -F'S/N='   '{split($2,a," "); print a[1]}')
  cnr=$(echo "$DATA_LINE"   | awk -F'C/N='   '{split($2,a," "); print a[1]}')
  frequency=$(echo "$DATA_LINE"  | awk -F'Freq='  '{split($2,a," "); print a[1]}')

  # extract metadata parameters from PI4_config.ini, they are not in the PI4 decoder message
  rx_call=$(grep -m 1 "RX_ID=" ./PI4_config.ini | awk -F'=' '{print $2}' | awk -F'#' '{print $1}' | xargs)
  band=$(grep -m 1 "BAND=" ./PI4_config.ini | awk -F'=' '{print $2}'| awk -F'#' '{print $1}' | xargs)
 
  echo ${DECODE_DATE}","${tx_call}","${rx_call}","${band}","${snr}","${cnr}","${frequency} >>ALL_decode.txt   # save the data locally

  # Into postgresql database
  # insert into data table pi4_spots in database tutorial on WSPRDaemon wd2 server
  PGPASSWORD=Whisper2008 psql -U wdupload -d tutorial -h wd2.wsprdaemon.org -c \
    "INSERT INTO pi4_spots (time, tx_call, rx_call, band, snr, cnr, frequency) \
     VALUES ('${DECODE_DATE}','${tx_call}', '${rx_call}', ${band}, ${snr}, ${cnr}, ${frequency});"

fi
