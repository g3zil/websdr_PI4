# -*- coding: utf-8 -*-
# PI4 detection algorithm based on the JT4 algorithm with the clever parts all due to Daniel Estevez at link below.
# I am grateful to Daniel for making his code available via GitHub.
# https://github.com/daniestevez/jupyter_notebooks/blob/master/dslwp/JT4G%20detection.ipynb
# Daniel's code is licensed under the MIT license, which is a permissive open source license#
# For PI4 details see  https://rudius.net/oz2m/ngnb/pi4.htm and links therein
# Two command line arguments, the date-time and the wav file that has been subsampled to 12000 ksps
# 24 Dec 2025 scoring code where frequency differences line up correctly from Claude AI Sonnet 4.5
# Gwyn Griffiths G3ZIL V1.1 December 2024-December 2025 

import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile
from scipy import signal        # For the  Continuous Wavelet Transform (CWT)
import sys
import csv
import subprocess
from subprocess import PIPE, run
import shutil
##########################################################################
# Functions
# The CWF approach for peak finding, the jiggle about that peak to find true peak and the interpolation are G3ZIL from HamSCI PSWS research
#
# local peak search: takes array index of CWF identified peak, does local search n bins either side for a true peak, returns index
def findLocalPeak (index, radius,level):
  # This method finds if the true local peak is to one side or other of CWF peak, and if so returns its index
  cwf_peak=level[index]
  for i in range (index-radius,index+radius+1):
     if level[i] > cwf_peak:
       index=i
       cwf_peak=level[i]
  return index

# Interpolate between frequency bins based on the weighted linear signal level at peak and either side
def freqInterpolate (index, radius, x, level):
  # This method interpolates in frequency space around true local peak returning an amplitude-weighted frequency
  sum=0
  sum_weights=0
  for i in range (index-radius,index+radius+1):
      sum=sum+x[i]*level[i]             # weighting by level is linear
      sum_weights=sum_weights+level[i]
  freq_interp=sum/sum_weights           # Interpolated peak frequency
  return freq_interp

# Bubble sort for frequency and correlation at that frequency in CWF peaks list
def bubble_sort(freq_peaks,level_peaks):
    print(len(freq_peaks))
   # Outer loop to iterate through the list n times
    for n in range(len(freq_peaks) - 1, 0, -1):
        # Initialize swapped to track if any swaps occur
        swapped = False
        # Inner loop to compare adjacent elements
        for i in range(n):
            if freq_peaks[i] > freq_peaks[i + 1]:
                # Swap elements if they are in the wrong order
                freq_peaks[i], freq_peaks[i + 1] = freq_peaks[i + 1], freq_peaks[i]
                level_peaks[i], level_peaks[i + 1] = level_peaks[i + 1], level_peaks[i]
                swapped = True
        # If no swaps occurred, the list is already sorted
        if not swapped:
          break
    if freq_peaks[0] <600:          # This is where we check for and remove sidelobes from correlation below 600 Hz
        freq_peaks=np.delete(freq_peaks,0)
        level_peaks=np.delete(level_peaks,0)
        print("First deleted, new first: ", f"{freq_peaks[0]:.2f}") 
        if freq_peaks[0] <600:      #  the second one can only be below 600 if the first one was
          freq_peaks=np.delete(freq_peaks,0)
          level_peaks=np.delete(level_peaks,0)
          print("Second deleted, new first: ", f"{freq_peaks[0]:.2f}")
    return freq_peaks, level_peaks

def remove_adjacent(L):      # This function removes instances where a single peak has adjacent frequencies
  return [elem for i, elem in enumerate(L) if i == 0 or L[i-1]+1 != elem]

def out(command):
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    return result.stdout

# Function from Claude AI
def find_pairs_with_difference(arr, target_diff, diff_margin, exclusion_margin):
    """
    Find pairs of indices whose value difference is close to target_diff.
    Excludes pairs near previously found pairs.
    
    Parameters:
    -----------
    arr : array-like
        One dimensional array of numbers
    target_diff : float
        The target difference between pair values
    diff_margin : float
        Acceptable margin for the difference (±diff_margin)
    exclusion_margin : int
        Index distance to exclude around previously found pairs
        
    Returns:
    --------
    list of tuples
        List of (index1, index2) tuples representing valid pairs
    """
    arr = np.array(arr)
    n = len(arr)
    pairs = []
    excluded_indices = set()
    
    # Check all possible pairs
    for i in range(n):
        if i in excluded_indices:
            continue
            
        for j in range(i + 1, n):
            if j in excluded_indices:
                continue
            
            # Calculate the difference
            diff = abs(arr[j] - arr[i])
            
            # Check if difference is within margin of target
            if abs(diff - target_diff) <= diff_margin:
                pairs.append((i, j))
                
                # Mark indices within exclusion_margin as excluded
                for k in range(max(0, i - exclusion_margin), 
                              min(n, i + exclusion_margin + 1)):
                    excluded_indices.add(k)
                for k in range(max(0, j - exclusion_margin), 
                              min(n, j + exclusion_margin + 1)):
                    excluded_indices.add(k)
                
                break  # Move to next i after finding a pair
    
    return pairs
	
############################################################################

###########
# Main code
###########

date_time=sys.argv[1] 	         	    # date and time passed in command line
wav_file=sys.argv[2] 	         	    # wav file name passed in command line

BASE_DIR=out("pwd")
BASE_DIR = BASE_DIR.strip('\n')

DETECTION_FILE=BASE_DIR + '/PI4_detections.csv'
PLOT_FILE=BASE_DIR + '/output/plots/filename'  # the png gets added in savefig as it needs to know the extension
ARCHIVE_DIR=BASE_DIR + '/archive/'
# Look for six peaks, as well as the wanted four, above 600 Hz if freq correct, 'sidelobes' can appear at lower
# frequencies and confuse matters, so screen those out 
freq_peaks=np.empty(8)
level_peaks=np.empty(8)

########  Start of code from Daniel's work #######################################
fs = 12000                                     # Fs is sampling frequency in sps, 11025 for JT4 
N = 2000                                       # Number of cycles per symbol, so each symbol lasts 0.1667 seconds. 2520 for JT4

rate, x = scipy.io.wavfile.read(wav_file)      # read in the wav file where it has been converted to 12000 sps using sox
print ("Samp rate = ",rate, "x.size ",x.size)  # print as a check, x.size with sox-trimmed 25s file is 25 * fs = 300,000

# Baud rate for PI4 is 5.859375 Hz, which, multiplied by K=40, gives tone spacing of 234.375 Hz
f_shift = 40
baud_rate=5.859375   	          # characteristic for PI4 in Hz
tone_spacing=baud_rate*f_shift    # we will look for peaks at this spacing
T0=683                            # 683 theory PI4 Tone zero frequency (Hz) - but look out for oscillator offset
Tn_tol=10                         # A tolerance for freq diff of tones 1,2,3 from T0, which can be tighter than for T0_tol as it is relative not absolute

# PI4 146 bit pseudo random sync vector provided by Klaus DJ5HG
sync = 2*np.array(list(map(int,'00100111101010100100010001100111100111110011011110101101101000001111101010000011111010010010100001001100000110000110011101110110101010000111000011')), dtype='int8')-1

# From Daniel: "The algorithm goes as follows: first, we perform an FFT so that each tone fits a single bin (FFT resolution = JT4 baudrate).
# Then we compute the power in each bin.
# Next for each symbol, we compute the pwr[tone1] + pwr[tone3] - pwr[tone0] - pwr[tone2]."

f_even = np.abs(np.fft.fftshift(np.fft.fft(x[:x.size//N*N].reshape((-1, N)), axis=1), axes=1))**2  # shape here is [351,2000]\
f_even = f_even[:,f_shift:-2*f_shift] + f_even[:,3*f_shift:] - f_even[:,:-3*f_shift] - f_even[:,2*f_shift:-f_shift]
f_odd = np.abs(np.fft.fftshift(np.fft.fft(x[N//2:x.size//N*N-N//2].reshape((-1, N)), axis=1), axes = 1))**2
f_odd = f_odd[:,f_shift:-2*f_shift] + f_odd[:,3*f_shift:] - f_odd[:,:-3*f_shift] - f_odd[:,2*f_shift:-f_shift]

# This is then correlated against the (bipolar) sync vector of JT4.
acq = np.empty((f_even.shape[0] + f_odd.shape[0] - 2*sync.size + 2, f_even.shape[1]))
acq[::2,:] = scipy.signal.lfilter(sync[::-1], 1, f_even, axis=0)[sync.size-1:,:]  # here the :: means whole list and the 2 is the step parm, hence evens
acq[1::2,:] = scipy.signal.lfilter(sync[::-1], 1, f_odd, axis=0)[sync.size-1:,:]  # starting at 1, with ::2, step in 2s from 1 hence odds

normalise= np.sqrt(np.sum(np.abs(sync[::-1])**2)*np.sum(np.abs(f_even)**2))
#normalise_odd= np.sqrt(np.sum(np.abs(sync[::-1])**2)*np.sum(np.abs(f_odd)**2))
print ("Normalising value ", normalise)

tsync = np.argmax(np.max(acq, axis=1))		# tsync is the time (s) of maximum correlation, as acq is in the time domain
print("Time shift for max correl = ",f"{tsync/2/baud_rate:.2f}", " s")  # convert from time bins to seconds

# Generate frequency axis, and then form frequency and correlation arrays for zoomed-in frequency span
fs = np.arange(-N//2, -N//2 + acq.shape[1])*baud_rate
fsync = np.argmax(acq[tsync,:])
zoom_lo=1033
zoom_hi=1325
f_zoom=fs[zoom_lo:zoom_hi]                         	# This zooms in to ~200 to 1900 Hz. Some wav files are off frequency. 
				   			# Shifted by f_shift for symmetry +/- frequencies
correl_zoom=abs(acq[tsync,zoom_lo:zoom_hi])/normalise         # normalised using factor calculated above
fsync = np.argmax(acq[tsync,zoom_lo:zoom_hi])
print("Fsync maximum correlation= ", f_zoom[fsync])

# Larger figure size
fig_size = [10, 6]
plt.rcParams['figure.figsize'] = fig_size

# plot sync entire band
plt.figure(facecolor='w')
plt.plot(fs, acq[tsync,:])
plt.title('Sync in frequency (full span)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Correlation');
plt.savefig(PLOT_FILE + '_full.png', dpi=300)
#plt.show()

# plot sync in zoomed in frequency around expected
plt.figure(facecolor='w')
plt.plot(f_zoom, correl_zoom)
plt.title('Sync in frequency (zoom)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Correlation')
plt.xlim(600,1600)
plt.savefig(PLOT_FILE + '_zoom.png', dpi=600)
#plt.show()

######################################################################################
# This is material from my HamSCI PSWS research on Doppler spectra
# Scipy find_peaks_cwt approach using continuous wavelet transform 
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks_cwt.html
# I am after the peaks for the four tones, should be separated by 234.375 Hz for PI4.
# i.e. 40 time baud rate of 5.859375 Hz
# but they will be different levels, generally decreasing with increasing baseband frequency
#######################################################################################

peaks = signal.find_peaks_cwt(correl_zoom, widths=np.arange(1,5))  # 2,4 is initial empirical selection
peakind=remove_adjacent(peaks)                                     # in case single peak shown as two adj freqs
print(peakind)
with open(DETECTION_FILE, "w") as out_file:
  out_writer=csv.writer(out_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
 
# find the index at eight successively reducing maxima: algorithm finds first max, finds freq and level at that index, then sets max that index to zero
# and iterates
  for i in range(0,8):
    max=np.argmax(correl_zoom[peakind])
    index_max=peakind[max]
    index_max_original=index_max
    freq_peaks[i]=f_zoom[index_max]
    level_peaks[i]=10*np.log10(correl_zoom[index_max])
    print("CWF peak ",i," frequency = ", freq_peaks[i], " Hz  at level = ",f"{level_peaks[i]:.2f}"," dB at index ",index_max)

# Now call function to look either side to find true peak, revise and print output
# Only search above 597.66 Hz index 69 
    if index_max > 69 and index_max < 288:  
        index_max=findLocalPeak(index_max,3,correl_zoom)
        freq_peaks[i]=float(f_zoom[index_max])
        level_peaks[i]=10*np.log10(correl_zoom[index_max])
        print("Revised CWF peak ",i," frequency = ", freq_peaks[i], " Hz  at level = ",f"{level_peaks[i]:.2f}", " dB at index_max ",index_max)
    if index_max > 69 and index_max < 288: 
        freq_peaks[i]=freqInterpolate(index_max,2,f_zoom,correl_zoom)
        print("Interpolated CWF peak ",i," frequency = ", f"{freq_peaks[i]:.2f}", " Hz" )
# Need to remove the peak just found from the array list of peaks
    to_remove=np.array([index_max_original])
    peakind=np.setdiff1d(peakind,to_remove)

# Some instances where not in frequency order, so have to sort
  freq_peaks,level_peaks =bubble_sort(freq_peaks,level_peaks)
  n_peaks=len(freq_peaks)
  print("freq peaks ", freq_peaks)
	
# Do we have a valid JT4 detection?
# Look for correct tone_spacing within tolerance either side set by Tn_tol, take indicies for matches
# We will call this a  score 1 detection, score 2 if T1 at +310 to +320 Hz, 3 if T2 +630 to +650 Hz and 4 if T3 +950 to +970 Hz
  score=0
  exclusion_margin=1  # to avoid duplicates
	
  result = find_pairs_with_difference(freq_peaks, tone_spacing, Tn_tol, exclusion_margin)
  print(f"Target difference: {tone_spacing} ± {Tn_tol}")
  print(result)
  print(f"\nFound {len(result)} pairs:")  
  for i, j, diff in result:
    print(f"  Indices ({i}, {j}): values {freq_peaks[i]} and {freq_peaks[j]}, difference = {diff}")  
     
# If detections is 4 archive the wav file into the arcive directory
  if score > 3:	
	  wav_file_name=wav_file[wav_file.rindex('/')+1:]
	  wav_file_name=wav_file_name.replace("_12000","")
	  shutil.copyfile(wav_file, ARCHIVE_DIR + wav_file_name)
# output detections data
  out_writer.writerow([date_time, f"{freq_peaks[0]:.2f}", f"{level_peaks[0]:.2f}",f"{freq_peaks[1]:.2f}", f"{level_peaks[1]:.2f}",\
  f"{freq_peaks[2]:.2f}", f"{level_peaks[2]:.2f}", f"{freq_peaks[3]:.2f}", f"{level_peaks[3]:.2f}", score ])
# print frequency differences, should be 234.375 Hz
    
print("f_diff_2-1 ", f"{freq_peaks[1]-freq_peaks[0]:.2f}","f_diff_3-2 ", f"{freq_peaks[2]-freq_peaks[1]:.2f}", "f_diff_4-3 ",\
 f"{freq_peaks[3]-freq_peaks[2]:.2f}", score)
