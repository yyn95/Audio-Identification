
"""
Definition for all classes used in an audio match task.
Yini Yang, 2019
"""

import numpy as np
import librosa
#import pydub
from scipy import signal
import os
import pickle

class AudioMatchTask:
    """Parameter initialization
    fs: the sampling rate
    stft_windowsize: stft window size in ms
    stft_hopsize: stft hop size in ms
    stft_zeropadding: stft zero padding multiplier
    windowsize, hopsize, zeropadding: in the number of samples
    delta_t * delta_f: the size of a ΔT(ms)xΔF(Hz) box in ms to locate an anchor
    deltaT, deltaF: in the number of samples
    timelow, timehigh, freqlow, freqhigh: the boundary of the target zone [t+Δt,t+Δt']*[f*Δf,f*Δf']
                                          to get a Shazam hash (f1,f2,Δt12)  
    database_dict: store all databases:
                   key: database name, eg:kiki, bouba
                   value: a list of addresses of stored Fingerprint objects for all audio files in a database
    query_dict: store all queries:
                   key: query name, eg: 'Q1', 'Q2'
                   value: the address of the stored Fingerprint object for a query
    match_result_dict: store the match results for any query-database pairs:
                   key: a tuple: (query_index, database_name)
                   value: the address of the stored DBMatchResult object for the query-database pair
    """
    fs = 44100
    stft_windowsize=50
    stft_hopsize=10
    stft_zeropadding=4
    windowsize = 2205
    hopsize = 441
    zeropadding = 8820
    freq_resolution = 5
    delta_t=100
    delta_f=882
    deltaT=10
    deltaF=176
    timelow=100
    timehigh=600
    freqlow=np.power(2,-0.5)
    freqhigh=np.power(2,0.5)
    def __init__(self, fs=44100, stft_windowsize=50, stft_hopsize=10, stft_zeropadding=4, \
            delta_t=100, delta_f=882, \
            timelow=100, timehigh=600, freqlow=np.power(2,-0.5), freqhigh=np.power(2,0.5)):
            AudioMatchTask.fs = fs
            AudioMatchTask.stft_windowsize = stft_windowsize
            AudioMatchTask.stft_hopsize = stft_hopsize
            AudioMatchTask.stft_zeropadding = stft_zeropadding
            AudioMatchTask.windowsize = int(AudioMatchTask.stft_windowsize*AudioMatchTask.fs/1000)
            AudioMatchTask.hopsize = int(AudioMatchTask.stft_hopsize*AudioMatchTask.fs/1000)
            AudioMatchTask.zeropadding = AudioMatchTask.stft_zeropadding*AudioMatchTask.windowsize
            AudioMatchTask.freq_resolution = AudioMatchTask.fs/AudioMatchTask.zeropadding
            AudioMatchTask.delta_t = delta_t
            AudioMatchTask.delta_f = delta_f
            AudioMatchTask.deltaT = int(AudioMatchTask.delta_t/AudioMatchTask.stft_hopsize)
            AudioMatchTask.deltaF = int(AudioMatchTask.delta_f/AudioMatchTask.freq_resolution)
            AudioMatchTask.timelow = timelow
            AudioMatchTask.timehigh = timehigh
            AudioMatchTask.freqlow = freqlow
            AudioMatchTask.freqhigh = freqhigh
            self.database_dict = {}
            self.query_dict = {}
            self.match_result_dict = {}

    """Read all audio files in a database and store Fingerprint objects
    database_name: the name of the database
    file_directory: the folder includes the whole database
    store_directory: the folder address for storing all the output fingerprint objects of the database
    """
    def generate_database(self, database_name, file_directory, store_directory):
        database = []
        folder = os.path.exists(store_directory)
        if not folder:
            os.makedirs(store_directory)
        for file in os.listdir(file_directory):
            file_name = file_directory + file
            document = Fingerprint(file_name)
            output_address = store_directory+file[:-4]+'.txt'
            with open(output_address,'wb') as f:
                pickle.dump(document,f)
            database.append(output_address)
            print(file)
        self.database_dict[database_name] = database

    """Get the Fingerprint object of a document
    """
    def get_document(self, database_name, document_index):
        document_addr = self.database_dict[database_name][document_index]
        with open(document_addr,'rb') as f:
            document = pickle.load(f)
        return document

    """Read a query audio file and store its Fingerprint object
    """
    def generate_query(self, query_name, file_dir, store_directory):
        query = Fingerprint(file_dir)
        folder = os.path.exists(store_directory)
        if not folder:
            os.makedirs(store_directory)
        output_address = store_directory+query_name+'.txt'
        with open(output_address,'wb') as f:
            pickle.dump(query, f)
        print("query: " + query_name)
        self.query_dict[query_name] = output_address
    
    """Get the Fingerprint object of a query
    """
    def get_query(self, query_name):
        query_addr = self.query_dict[query_name]
        with open(query_addr,'rb') as f:
            query = pickle.load(f)
        return query

    """Match two fingerprints hashset
    """
    def match_fingerprint(self, fp1, fp2):
        match_list = []
        for key1 in fp1.keys():
            for key2 in fp2.keys():
                if (key1[0]==key2[0]) and (key1[1]==key2[1]) and (key1[2]==key2[2]):
                #if (key1[0]-key2[0])+(key1[1]-key2[1])+(key1[2]-key2[2])==0:
                    for timestamp1 in fp1[key1]:
                        for timestamp2 in fp2[key2]:
                            match_list.append((timestamp1, timestamp2))
        return match_list
    
    """Match a query with a database and store the DBMatchResult object
    """
    def match_database(self, query_name, database_name, store_dir):
        folder = os.path.exists(store_dir)
        if not folder:
            os.makedirs(store_dir)
        query_addr = self.query_dict[query_name]
        with open(query_addr,'rb') as f:
            query = pickle.load(f)
        database_addrlist = self.database_dict[database_name]
        db_match_list = []
        db_match_number = []
        count = 0
        for document_addr in database_addrlist:
            with open(document_addr,'rb') as f:
                document = pickle.load(f)
            match_list = self.match_fingerprint(query.fingerprints, document.fingerprints)
            db_match_list.append(match_list)
            db_match_number.append(len(match_list))
            print("complete match: " + str(count))
            count += 1
        db_match_result = DBMatchResult(db_match_list, db_match_number)
        output_address = store_dir+query_name+database_name+'.txt'
        with open(output_address,'wb') as f:
            pickle.dump(db_match_result, f)
        self.match_result_dict[(query_name, database_name)] = output_address
        print("Match completed for: "+query_name+database_name)

    """Get the DBMatchResult object of a query and a database
    """     
    def get_match_result(self, query_name, database_name):
        result_addr = self.match_result_dict[(query_name, database_name)]
        with open(result_addr,'rb') as f:
            result = pickle.load(f)
        return result


class Fingerprint(AudioMatchTask):

    def __init__(self, filename):
        self.read_file(filename)
        self.stft()
        self.calculate_anchors()
        self.calculate_hashset()

    """Read audio file
    fs: sampling rate
    samples: normalized amplitude samples from audio file, [-1,1]
    samplesNum: the number of samples
    """
    def read_file(self, filename):
        self.samples, _=librosa.load(filename, sr=AudioMatchTask.fs)
        self.samples = np.divide(self.samples, max(self.samples))
        self.samplesNum = len(self.samples)
    

    """Conduct STFT
    windowsize, hopsize, zeropadding: value in samplings
    freqs, times, amplitudes: result of STFT (only keep the data for freq <= 5000)
    freq_resolution: the difference of two adjacent frequencies 
    freq5000index: the index for the maximum frequency <= 5000
    """
    def stft(self):
        self.freqs, self.times, self.amplitudes= signal.stft(self.samples, fs=AudioMatchTask.fs, \
            window='hann', nperseg=AudioMatchTask.windowsize, noverlap=AudioMatchTask.windowsize-AudioMatchTask.hopsize, nfft=AudioMatchTask.zeropadding)
        self.amplitudes = np.abs(self.amplitudes)
        self.amplitudes = self.amplitudes/np.max(self.amplitudes)
        freq5000index = int(5000/AudioMatchTask.freq_resolution) + 1
        self.freqs = self.freqs[:freq5000index]
        #self.times = np.around(self.times, 2)
        self.amplitudes = self.amplitudes[:freq5000index]


    """Locate anchors in the sonogram (only consider frequencies<5000)
    deltaT: deltaTime/hopTime, the number of frames in a ΔTxΔF box
    deltaF: deltaFreq/freq_resolution, the number of frequency samples in a ΔTxΔF box
    anchors: a 3d array: 
             1st: timestamp index(0~timeSegmentNum)
             2nd: freqstamp index(0~freqSegmentNum)
             3rd: anchor position tuple: (freqstamp, timestamp)
             generated column by column, eg: positions[0,:,:] is the first column in the constellation map
    """
    def calculate_anchors(self):
        freqSegmentNum = int(self.amplitudes.shape[0]/AudioMatchTask.deltaF)
        timeSegmentNum = int(self.amplitudes.shape[1]/AudioMatchTask.deltaT)
        self.anchors = []
        timeMinInd = 0

        for i in range(timeSegmentNum):
            timeMaxInd = timeMinInd + AudioMatchTask.deltaT
            freqMinInd = 0
            timeMinAnchors = []
            for j in range(freqSegmentNum):
                region = self.amplitudes[freqMinInd:(freqMinInd+AudioMatchTask.deltaF), timeMinInd:timeMaxInd]
                locationInd = np.unravel_index(np.argmax(region, axis=None), region.shape) + np.array([freqMinInd, timeMinInd])
                anchorLoc = (self.freqs[locationInd[0]], self.times[locationInd[1]])
                timeMinAnchors.append(anchorLoc)
                freqMinInd += AudioMatchTask.deltaF
            
            region = self.amplitudes[freqMinInd:, timeMinInd:timeMaxInd]
            locationInd = np.unravel_index(np.argmax(region, axis=None), region.shape) + np.array([freqMinInd, timeMinInd])
            anchorLoc = (self.freqs[locationInd[0]], self.times[locationInd[1]])
            timeMinAnchors.append(anchorLoc)
            timeMinInd += AudioMatchTask.deltaT
            self.anchors.append(timeMinAnchors)
        self.anchors = np.array(self.anchors)

    """Calculate hashes for all anchors in the constellation map
    anchors: 3d: deltaT windows*deltaF windows*anchor postions(freq,time)  
    fingerprints: dict:
                  key(hash): (f1,f2,Δt12)
                  value: the list of anchor positions(f1,t1) with this hash
    Obtained by traversing column by column in the anchors matrix
    """
    def calculate_hashset(self):
        self.fingerprints = dict()
        timeWindowNum = self.anchors.shape[0]
        freqWindowNum = self.anchors.shape[1]

        for i in range(timeWindowNum):
            for j in range(freqWindowNum):
                curAnchor = self.anchors[i,j,:]
                freqMin = curAnchor[0] * AudioMatchTask.freqlow
                freqMax = curAnchor[0] * AudioMatchTask.freqhigh
                timeMin = curAnchor[1] + AudioMatchTask.timelow/1000
                timeMax = curAnchor[1] + AudioMatchTask.timehigh/1000
                rightInd = 1

                while(i + rightInd < timeWindowNum):
                    # shift one step to the right
                    compareAnchor = self.anchors[i+rightInd,j,:]
                    if(timeMin <= compareAnchor[1] and compareAnchor[1] <= timeMax \
                    and freqMin <= compareAnchor[0] and compareAnchor[0] <= freqMax):
                        hashValue = (curAnchor[0], compareAnchor[0], compareAnchor[1]-curAnchor[1])
                        if hashValue in self.fingerprints:
                            self.fingerprints[hashValue].append(curAnchor[1])
                        else:
                            self.fingerprints[hashValue] = [curAnchor[1]]
                    elif (compareAnchor[1] > timeMax):
                        break
                    
                    # traverse upwards in the same deltaT timeWindow
                    upInd = 1
                    while(j + upInd < freqWindowNum):
                        compareAnchor = self.anchors[i+rightInd,j+upInd,:]
                        if(freqMin <= compareAnchor[0] and compareAnchor[0] <= freqMax):
                            hashValue = (curAnchor[0], compareAnchor[0], compareAnchor[1]-curAnchor[1])
                            if hashValue in self.fingerprints:
                                self.fingerprints[hashValue].append(curAnchor[1])
                            else:
                                self.fingerprints[hashValue] = [curAnchor[1]]
                        elif (compareAnchor[0] > freqMax):
                            break
                        upInd += 1
                    
                    # traverse downwards in the same deltaT timeWindow
                    downInd = 1
                    while(j-downInd >= 0):
                        compareAnchor = self.anchors[i+rightInd,j-downInd,:]
                        if(freqMin <= compareAnchor[0] and compareAnchor[0] <= freqMax):
                            hashValue = (curAnchor[0], compareAnchor[0], compareAnchor[1]-curAnchor[1])
                            if hashValue in self.fingerprints:
                                self.fingerprints[hashValue].append(curAnchor[1])
                            else:
                                self.fingerprints[hashValue] = [curAnchor[1]]
                        elif (compareAnchor[0] < freqMin):
                            break
                        downInd += 1                   
                    rightInd += 1


class DBMatchResult:
    """Store match results between a query and all documents in a database 
    db_match_result: a list of all match lists
    db_match_number: a list of the length of all match lists
    The index is the same as the index of the document in the database
    """
    def __init__(self, db_match_list, db_match_number):
        self.db_match_list = db_match_list
        self.db_match_number = db_match_number