"""
Analyzing audio match results.
Yini Yang, 2019
"""
import numpy as np
import matplotlib.pyplot as plt
import pickle
import heapq

## read results from file
with open('./results/audio_match_task.txt','rb') as f:
    audio_match_task = pickle.load(f)

# get database match results
kiki_results = []
bouba_results = []
for query_name in audio_match_task.query_dict.keys():
    kiki_result = audio_match_task.get_match_result(query_name,'kiki')
    bouba_result = audio_match_task.get_match_result(query_name,'bouba')
    kiki_results.append(kiki_result)
    bouba_results.append(bouba_result)
queryNum = len(kiki_results)
docNum = len(kiki_results[0].db_match_number)

## visualize all the matching number results
index = np.linspace(1,docNum,docNum)
plt.rc('font', size=15)
plt.figure(figsize=(25,15))
for i in range(1,queryNum+1):
    ax = plt.subplot(320+i)
    plt.plot(index, kiki_results[i-1].db_match_number, linewidth=1.5, color='orange', label='kiki')
    plt.plot(index, bouba_results[i-1].db_match_number, linewidth=1.5, color='skyblue', label='bouba')
    ax.set_xlim(1, docNum)
    ax.set_xlabel('Index')
    ax.set_ylabel('Matching number')
    plt.title('Q'+str(i))
    plt.legend(loc='upper left')
plt.subplots_adjust(hspace=0.5)
plt.savefig('./graphs/match result.png')
plt.show()

## get match points
types = ['bouba', 'bouba', 'kiki', 'kiki', 'bouba', 'kiki']
queries = []
documents = []
match_points_list = []
match_index = []
for i in range(1,queryNum+1):
    query = audio_match_task.get_query('Q'+str(i))
    if types[i-1] == 'bouba':
        match_number = bouba_results[i-1].db_match_number
        maxindex = match_number.index(max(match_number))
        document = audio_match_task.get_document('bouba',maxindex)
        match_list = bouba_results[i-1].db_match_list[maxindex]
        documents.append(document)
        match_points_list.append(match_list)
        match_index.append(maxindex)
    elif types[i-1] == 'kiki':
        match_number = kiki_results[i-1].db_match_number
        maxindex = match_number.index(max(match_number))
        document = audio_match_task.get_document('kiki',maxindex)
        match_list = kiki_results[i-1].db_match_list[maxindex]
        documents.append(document)
        match_points_list.append(match_list)
        match_index.append(maxindex)
    queries.append(query)
    print("Complete: Q"+str(i))

## visualize all matched points
plt.rc('font', size=15)
plt.figure(figsize=(25,15))
for i in range(1,queryNum+1):
    ax = plt.subplot(320+i)
    match_list = np.array(match_points_list[i-1])
    plt.scatter(match_list[:,1], match_list[:,0], marker='x', color='black', s=50)
    ax.set_xlim(0, documents[i-1].times[-1])
    ax.set_ylim(0, queries[i-1].times[-1])
    ax.set_xlabel('Document timestamp (s)')
    ax.set_ylabel('Query timestamp (s)')
    plt.title('Matching points for Q'+str(i))
plt.subplots_adjust(hspace=0.5)
plt.savefig('./graphs/matched points.png')
plt.show()

## store results
with open('./results/match_index.txt','wb') as f:
    pickle.dump(match_index,f)
