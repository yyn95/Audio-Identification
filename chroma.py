"""
Ploting chromagrams
Yini Yang, 2019
"""
import numpy as np
import matplotlib.pyplot as plt
import pickle

## define chroma features
# transform pitch to frequency
def pitchToFreq(pitch):
    freq = np.power(2,float(pitch-69)/12)*440
    return freq

# transform spectrum to log-frequency spectrum
def logFrequency(freqs, times, amplitudes):
    pitchAmpt=np.zeros((128, len(times)))
    pitch = 0
    upbound = pitchToFreq(pitch+0.5)
    for i in range(1, len(freqs)):       
        while (freqs[i] > upbound):
            pitch += 1
            upbound = pitchToFreq(pitch+0.5)
        pitchAmpt[pitch,:] += np.power(amplitudes[i,:],2)
        if freqs[i] >= 12910:
            break    
    return pitchAmpt

# transform log-freq spectrum to chromagram
def chromagram(LogAmpt):
    chromaAmpt=np.zeros((12, LogAmpt.shape[1]))
    for pitch in range(128):
        chroma = pitch % 12
        chromaAmpt[chroma,:] += LogAmpt[pitch,:]
    return chromaAmpt

## read results
with open('./results/audio_match_task.txt','rb') as f:
    audio_match_task = pickle.load(f)
with open('./results/match_index.txt','rb') as f:
    match_index = pickle.load(f)

## build chroma features for a query and its source candidate
query = audio_match_task.get_query('Q1')
QLogAmpt = logFrequency(query.freqs, query.times, query.amplitudes)
QChromaAmpt = chromagram(QLogAmpt)
document = audio_match_task.get_document('bouba', match_index[0])
DocLogAmpt = logFrequency(document.freqs, document.times, document.amplitudes)
DocChromaAmpt = chromagram(DocLogAmpt)

## plot chromagrams
plt.rc('font', size=15)
plt.subplots(figsize=(30,15))
ax1 = plt.subplot(211)
plt.imshow(QChromaAmpt, origin='lower', cmap='cividis', extent=(0, query.times[-1], 0, 12))
ax1.set_aspect(2)
ax1.axis('tight')
ax1.set_ylabel('pitch class')
ax1.set_xlabel('Time (s)')
plt.title('Chromagram for Q1')
ax2 = plt.subplot(212)
plt.imshow(DocChromaAmpt, origin='lower', cmap='cividis', extent=(0, document.times[-1], 0, 12))
ax2.set_aspect(2)
ax2.axis('tight')
ax2.set_ylabel('pitch class')
ax2.set_xlabel('Time (s)');
plt.title("Chromagram for Q1's source candidate")
plt.show()
