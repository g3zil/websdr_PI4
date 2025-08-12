# -*- coding: utf-8 -*-
# Filename: ff_noise.py
# Program to extract the noise level from wav format file as in WSJT-X
## V1 by Christoph Mayer. 
## V1.1 by Gwyn Griffiths used in WsprDaemon
## V1.21 by Gwyn Griffithsfor use with 24 GHz websdr and this sub-version for PI4
##       Note the one minute for PI4 has the digital mode, a CW ident and tone
## Output single value, being the total power (dB arbitary scale) in the lowest 30% of the Fourier coefficients
## between 373 and 2933 Hz where the passband is flat for CW / JT4G 24 GHz beacons
## where one minute wav file input rather than two minute c2 as in WSPR/FST4W
## The cal_offset value is set to match the noise level to sox rms for additive Gaussian white noise.
## Script takes a single argument, the wav file name to process.
##
## July 2025

import struct
import sys
import numpy as np
import scipy.io.wavfile as wav
import pylab as plt              # used in initial testing, not routine

fn = sys.argv[1]     # wav file name for processing
cal_offset=-118.5    # See Excel workbook '24 GHZ WebSDR.xlsx'  August 2025 for derivation to match RMS Noise only at TRIG01

samplerate, samples = wav.read(fn)
#print ("Sample rate and no of samples: ", samplerate,len(samples))

## One minute should contain 720000 samples
## we perform 64 FFTs, each 11250 samples long
n_fft=64
n_samples=11250

a = samples.reshape(n_fft,n_samples)       # reshape the input data series into n_fft (64) blocks
hann=np.hanning(n_samples)                 # Hann window for time series pre FFT
a =a*hann                                  # Apply the Hann window, it does so for each block

x= np.arange(-5625,5625, dtype=np.float32) # Generate frequency index scale for plotting, so 5625 maps to zero freq and 11250 to 6000 Hz
w = np.square(np.abs(np.fft.fftshift(np.fft.fft(a, axis=1,norm="forward"), axes=1)))  # fft with zero in centre, and coeffs normalised amplitude

## These expressions first trim the frequency range to 373 Hz to 2933 Hz to ensure
## a flat passband without bias from the shoulders of the bandpass filter in the websdr USB setting
## i.e. array indices 5975:8375
w_bandpass=w[:,5975:8375]

## partitioning for selecting 30% of lowest coefficients is done on the sorted flattened array
## we have 2400 freq bins in the bandpass multiply by 64 for blocks = 153600 coefficients, take 30% which is 46080
w_flat_sorted=np.partition(w_bandpass, 46080, axis=None)

noise_level_flat=10*np.log10(np.sum(w_flat_sorted[0:46080])) + cal_offset   # coeffs are linear so simple add, then 10 log 10 to dB as w is squared, see above
print(' %6.2f' % (noise_level_flat))

#############################################################################################
# plot the spectrum - not used, initial diagnostics, but left here in case needed at some time
#fig, ax= plt.subplots()   #
#plt.suptitle("FFT Doppler Spectrum", fontsize=12)
#xaxis_title="Frequency (Hz)"
#w=10*np.log10(w)
#plt.plot(x[5626:6626], w[10,5626:6626], color='black')
#plt.xlabel(xaxis_title)
#plt.ylabel("PSD uncalibrated (dB)")
#plt.show()
