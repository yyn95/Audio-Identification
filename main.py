"""
Running for audio match results.
Yini Yang, 2019
"""
import numpy as np
from fingerprint import AudioMatchTask, Fingerprint
import os
import pickle

## initialize the task
audio_match_task = AudioMatchTask()
## read queries
for file in os.listdir('./queries/'):
    query_name = file[:-4]
    file_dir = './queries/' + file
    audio_match_task.generate_query(query_name, file_dir, './database/query/')
    print("Complete: "+query_name)

## read kiki and bouba dataset
audio_match_task.generate_database('kiki','./dataset/kiki/','./database/kiki/')
audio_match_task.generate_database('bouba','./dataset/bouba/','./database/bouba/')

## match all queries with the two databases
for query_name in audio_match_task.query_dict.keys():
    audio_match_task.match_database(query_name, 'kiki','./results/')
    audio_match_task.match_database(query_name, 'bouba','./results/')

## store results
with open('./results/audio_match_task.txt','wb') as f:
    pickle.dump(audio_match_task,f)

