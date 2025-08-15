# -*- coding: utf-8 -*-
# A simple numerical simulator to calculate the probability of recoding 0, 1, 2, 3 and 4 matches
# for spectral peaks aligning with PI4 Tone 0 and Tones 1-3 frequencies with the criteria used in PI4_detect.py
# Gwyn Griffiths G3ZIL August 2025

import numpy as np
import random

#################
# Function
#################
# Bubble sort for frequency and correlation at that frequency in CWF peaks list
def bubble_sort(freq_peaks):
   # Outer loop to iterate through the list n times
    for n in range(len(freq_peaks) - 1, 0, -1):
        # Initialize swapped to track if any swaps occur
        swapped = False
        # Inner loop to compare adjacent elements
        for i in range(n):
            if freq_peaks[i] > freq_peaks[i + 1]:
                # Swap elements if they are in the wrong order
                freq_peaks[i], freq_peaks[i + 1] = freq_peaks[i + 1], freq_peaks[i]
                swapped = True
        # If no swaps occurred, the list is already sorted
        if not swapped:
          break
    if freq_peaks[0] <600:          # This is where we check for and remove sidelobes from correlation below 600 Hz
        freq_peaks=np.delete(freq_peaks,0)
        if freq_peaks[0] <600:      #  the second one can only be below 600 if the first one was
          freq_peaks=np.delete(freq_peaks,0)
    return freq_peaks

###########
# Main code
###########

# declare number of simulations to run and set constants to match PI4_detect.py
n_samples=10000000
score=np.empty(n_samples)

f_shift = 40
baud_rate=5.859375   	          # characteristic for PI4 in Hz
tone_spacing=baud_rate*f_shift    # we will look for peaks at this spacing

T0=683                            # PI4 Tone zero frequency (Hz)
T0_tol=100			  # A tolerance for T0 to give a window for TCXO stability.
Tn_tol=10                         # A tolerance for freq diff of tones 1,2,3 from T0, which can be tighter than for T0_tol as it is relative not absolute

# Generate six frequencies from a uniform random distribution between 200 Hz and 1910.9373 Hz
# spaced by the baud rate 5.859375 Hz

for j in range (0,n_samples):
  freq_peaks=np.empty(6)
  for i in range (0,6):
      freq_peaks[i]=(np.floor(random.uniform(0,292))*baud_rate)+200  # random 1 of 292 possible frequencies, as integer, then mult by baud rate and add offset

# bubble sort into ascending order, dropping first and, if need be, second if below 600 Hz, always keep 4
  freq_peaks= bubble_sort(freq_peaks)
  
  for k in range (0,4):
  # Do we have a valid detection? First step, do we have T0 frequency  between T0-T0_tol and  T0+T0_tol
  # We will call this a  score 1 detection, score 2 if T1 at +310 to +320 Hz, 3 if T2 +630 to +650 Hz and 4 if T3 +950 to +970 Hz
  # These are the same criteria as in PI4_detect.py
    score[j]=0
    if freq_peaks[0] > T0-T0_tol and freq_peaks[0] < T0+T0_tol:
      score[j]=1
      if freq_peaks[1] > freq_peaks[0]-Tn_tol+tone_spacing and freq_peaks[1] < freq_peaks[0]+Tn_tol+tone_spacing:
        score[j]=2
        if freq_peaks[2] >  freq_peaks[0]-Tn_tol+2*tone_spacing and freq_peaks[2] < freq_peaks[0]+Tn_tol+2*tone_spacing:
          score[j]=3
          if freq_peaks[3] > freq_peaks[0]-Tn_tol+3*tone_spacing and freq_peaks[3] < freq_peaks[0]+Tn_tol+3*tone_spacing:
            score[j]=4
 
# output the score
print("Count score 0: ", (0 == score).sum())
print("Count score 1: ", (1 == score).sum())
print("Count score 2: ", (2 == score).sum())
print("Count score 3: ", (3 == score).sum())
print("Count score 4: ", (4 == score).sum())
