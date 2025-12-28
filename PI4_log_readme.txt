                                    PI4_log
   
A prototype package for 24/7 monitoring and logging of PI4 signals at the Kent 24 GHz WebSDR

Gwyn Griffiths G3ZIL   gxgriffiths@virginmedia.com
with Dr John Worsnop G4BAO

Installation, test and operating instructions for a Raspberry Pi running PiOS or a machine running Ubuntu 24.04

Version 1.1 December 2025     adapted to also run under Ubuntu 24.04, and various improvements
                              First version at Github
---------------------------------------------------------

1. Prerequisites and PI4_log package download
	a) A browser capable of connecting to the WebSDR at trig01.ddns.net:8073
	   Have used Vivaldi and Firefox.
	b) WSJT-X package set up to use VHF extensions to enable mode JT4 submode G
     WSJT-X is only used as waterfall display and acquirer of wav files every one minute.
 c) A virtual cable (e.g. pulseaudio) to connect the browser audio to WSJT-X
    and pavucontrol to set audio level to WSJT-X. Affects signal level (not SNR)
    keep to same setting and watch out if keyboard volume control affects the level
    On the WSJT-X Settings->Audio page select pulse as the input source, or to suit if you use another option.
	d) On the Save pulldown of WSJT-X select Save all for the wav files.
	   PI4_log will keep the number of wav files to the latest 10.
	e) Here it is assumed you cloned the Github repository and run the setup and python scripts.
           Go to your home directory cd ~
           check that directory websdr_PI4 has been created in your home directory and contents are as below:
	   (times will be different)
     pi@cutiepi:~/websdr_PI4 $ ls -l
    total 96
    drwxr-xr-x 2 pi pi  4096 Dec 28 17:03 archive
    -rw-r--r-- 1 pi pi  3067 Dec 28 17:03 fft_noise.py
    drwxr-xr-x 3 pi pi  4096 Dec 28 17:03 output
    -rw-r--r-- 1 pi pi  1045 Dec 28 17:03 PI4_config_template.ini
    -rw-r--r-- 1 pi pi 14362 Dec 28 17:03 PI4_detect_new.py
    -rwxr-xr-x 1 pi pi 13138 Dec 28 17:03 PI4_detect.py
    -rw-r--r-- 1 pi pi 11657 Dec 28 17:03 PI4_detect_replay.py
    -rw-r--r-- 1 pi pi  3567 Dec 28 17:03 PI4_detect_simulation.py
    -rw-r--r-- 1 pi pi    18 Dec 28 17:03 PI4_log_readme.txt
    -rwxr-xr-x 1 pi pi  3201 Dec 28 17:03 PI4_log.sh
    -rwxr-xr-x 1 pi pi  2264 Dec 28 17:03 PI4_upload.py
    -rw-r--r-- 1 pi pi    56 Dec 28 17:03 python_requirements.txt
    -rw-r--r-- 1 pi pi  2350 Dec 28 17:03 README.md
    drwxr-xr-x 2 pi pi  4096 Dec 28 17:03 save
    -rwxr-xr-x 1 pi pi   564 Dec 28 17:03 setup.sh
    -rwxr-xr-x 1 pi pi  2628 Dec 28 17:03 sn_calc.sh
     
2. Preparing for use PI4_log.sh	
	a) Change directory using cd ~/websdr_PI4
	b) Copy the PI4_config_template.ini file into PI4_config.ini
     edit the RX_GRID and RX_ID fields to suit your setup and save,
	   suggestion is to use TRIG01/yourcallsign to show who is using it

3. Preparing for use WSJT-X and the WebSDR browser 
	a) On a Raspberry Pi tests have shown that, over time (ten+ hours) noise and spurs
     are introduced (somehow) into the virtual audio chain. It presence and growth is
     minimised if the default sample rate in pulseaudio is changed from 44.1 ksps
	   to 48 ksps, which is the preferred WSJT-X sample rate. This change is made by:
	     sudo su
	     nano /etc/pulse/daemon.conf
	   find line
	     ;default-sample-format = s16le
	   remove the semi colon to uncomment and make active
	   remove the semicolon from next line for the default sampling rate, and add comment, so you would have:
	     default-sample-rate = 48000     # changed from 44100 G3ZIL at *** UTC on *** 2024
	   This is a useful but insufficient remedy for the noise and spur growth.
     An effective additional step is described in section 6.
	   Now Reboot the computer for the change to take effect. On restart, open web browser. 
	b) With the web browser at trig01.ddns.net:8073 set its frequency to 24.04898428 GHz, mode USB, this is for ON0HVL PI4 beacon, best chance
	c) In WSJT-X set mode JT4 and submode G
	d) If not already done, in File->Settings->Frequencies tab add 24048.98428 MHz as a JT4 mode, just for reference, not used
	   This frequency, by trial and error, brings the ON0HVL signal to about the right tone PI4 frequencies: it does drift +/- 30 Hz.
	e) In WSJT-X menu File->Settings->Audio set the save directory to
           /home/pi/websdr_PI4/save
           NB Change pi to your userid if Ubuntu etc
	   You may need to recheck this setting if WSJT-X crashes, it is kept after a normal close.
	f) Start monitoring on the websdr with frequency 24.04898428 GHz (band 1.25 cm), examine the WSJT-X waterfall display.
	   Second half of each minute should show a single frequency peak at ~900 Hz, the carrier plus CW.
	   First half of each minute should be four peaks, at ~683, 917, 1151, 1385 Hz. They will be weaker, and likely unequal strength.
	g) WSJTX Band Activity window is meaningless.

4. Test PI4_log.sh in manual mode
	a) Change directory using cd ~/websdr_PI4 
           Check that at least one wav file has been recorded using
           ls -l ./save
           if so, start the script in manual mode:
	   ./jt4_log.sh
           if not, check correct save directory file name in wsjtx and Save All has been selected.
	b) If the script runs (hopefully properly!) it will output either:

           For an odd minute where it has measured the CW carrier signal level and the noise level

	   Modules OK
	   If odd minute then CW file for signal level and noise, else if even a missed JT4 spot interval
	   File time 0845  last minute time 0845
	   Correct odd minute - so process signal and noise  
	   RMS_NOISE (dB)= -73.84
	   RMS_SIGNAL (dB)= -49.66
	   removed '/home/pi/jt4/save/241106_1603.wav'
	   Processing complete

	   or, if WSJT-X has crashed, it sees a time discrepancy between 'now' and expected file time:

	   Modules OK
	   If odd minute then CW file for signal level and noise, else if even a missed JT4 spot interval
	   File time 0845  last minute time 0854
	   File time mismatch: WSJT-X likely not running
	   Processing complete

	   or, for an even minute in which there was no JT4G decode:

	   Modules OK
	   If odd minute then CW file for signal level and noise, else if even a missed JT4 spot interval
	   removed '/home/pi/jt4/save/241106_1608.wav'
	   Processing complete

	   or it might output:

	   Modules OK
           Spot has been uploaded previously - exiting

	   or, for an even minute in which there was a JT4G decode

	   Modules OK
	   New spot decoded
	   done
	   Decode data and added variables written to spots_azi.csv file

	   Best check in both even and odd minutes.
           In every case it tidies up the wav file directory, keeping only the last 10.
	c) If anything other than the responses above appear please contact gwyn at gxgriffiths@virginmedia.com
	d) But if all is well, in your browser go to the WebSDR_jt4 Grafana dashboard
           (userid: wdread password: JTWSPR2008)
	   at:
	   http://logs1.wsprdaemon.org:3000/d/qO0MwaZHz/websdr_jt4?orgId=1&from=now-3h&to=now-1m&var-band_cm=1.25&var-receiver=TRIG01%2FG3ZIL&var-beacon=GB3PKT

	   You will need to select your receiver name from the pull down list top left.
	   Hopefully you will see data points for:
	   (top panel) Signal+Noise level in 200 Hz bandwidth and absolute humidity
	   (next) Signal+Noise to Noise ratio estimate from JT4G - inaccurate if using WSJT-X 2.7, correct in WSJT-X improved 2.8 onward
	   (next) Signal+Noise to Noise ratio estimate from the CW signal (not JT4G) and the noise level estimate in dB in 1 Hz
	   (next) Baseband frequency of the JT4G signal whenever there is a decode
	   (next) Air, water and dew point temperatures from Met Office buoy F3 in the channel east of Margate
	   (next) Wind speed and direction from the buoy
	   (next) Relative humidity from the buoy
	   (bottom) Rainfall rate from Environment Agency sensor at Tillingham, Essex.

	   If things look odd, contact Gwyn.

5. Operate jt4_log.sh in automatic mode
	a) In operation the script is run by cron, set up using the command:

	   crontab -e

	b) Add the following line to the end of the cron file that will be listed:

           * * * * * cd /home/pi/websdr_jt4 ; /home/pi/websdr_jt4/jt4_log.sh >/home/pi/websdr_jt4/cronlog.txt 2>&1

	   This will run the script every minute. After execution, the content of the file ~/websdr_jt4/cronlog.txt
	   should be one of the three messages listed above. If not, contact Gwyn.
           Be sure to change the THREE instances of userid pi if necessary.
           The individual scripts will pick up their own correct home directory, only in this cron line is up to you.
	   You can monitor the cronlog.txt file when in the ~/websdr_jt4 directory with:
	   watch cat cronlog.txt
	   Control C to exit - the display shpould update some seconds after each top of the minute.

	c) After a little time, check the Grafana dashboard using step 4f above.

6. Script to close WSJT-X, restart the pulseaudio service and restart WSJT-X
	a) This is a work-around to the growth of virtual audio noise and spurs seen on a Raspberry Pi.
	   The data deterioration is minimal if this is done every hour. Hence the pa_restart.sh script is run using cron.
	b) Set up using the command:

	   crontab -e
	c) Add the following line at the end of the cron file:

           1 * * * * XDG_RUNTIME_DIR=/run/user/$(id -u) cd /home/pi/websdr_jt4 ; /home/pi/websdr_jt4/pa_restart.sh >/home/pi/websdr_jt4/cron_kill.log 2>&1

	   This runs the restart script one minute past the hour. Consequently, most times, JT4 decodes are not missed.
           As for the first cron job, check the THREE instances of home directory name.

Gwyn G3ZIL Version 1.1 December 2025





