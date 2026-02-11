# -*- coding: utf-8 -*-
# March-May  2020 This version for PI4 detections and noise data Nov 2024  Gwyn Griffiths G3ZIL
# Version 1.4 Nov 2024 to August 2025 for PI4 24 WebSDR
#  URL updated to wd1.wsprdaemon.org 23 Nov 2025

import psycopg2                  # This is the main connection tool, believed to be written in C
import psycopg2.extras           # This is needed for the batch upload functionality
import csv                       # To import the csv file
import sys                       # to get at command line argument with argv

# initially set the connection flag to be None
conn=None
connected="Not connected"
cursor="No cursor"
execute="Not executed"
commit="Not committed"
# get the path to the latest_log.txt file from the command line
batch_file_path=sys.argv[1]

try:
    with open (batch_file_path) as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        sql="""INSERT INTO pi4 (time, tx_call, tx_grid, band, frequency, rx_id, rx_grid, mode, rms_noise,\
        t0_freq, t0_level, t1_freq, t1_level, t2_freq, t2_level, t3_freq, t3_level, score, fft_noise, splusn)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
        try:
               # connect to the PostgreSQL database
               #print ("Trying to  connect")
               conn = psycopg2.connect("dbname='tutorial' user='wdupload' host='wd2.wsprdaemon.org' password='Whisper2008'")
               connected="Connected"
               #print ("Appear to have connected")
               # create a new cursor
               cur = conn.cursor()
               cursor="Got cursor"
               # execute the INSERT statement
               psycopg2.extras.execute_batch(cur,sql,csv_data) 
               execute="Executed"
               #print ("After the execute")
               # commit the changes to the database
               conn.commit()
               commit="Committed"
               # close communication with the database
               cur.close()
               #print (connected,cursor, execute,commit)
        except:
               print ("Unable to connect to the database:", connected,cursor, execute, commit)
finally:
        if conn is not None:
            conn.close()
          
