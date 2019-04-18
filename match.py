#!/usr/bin/env python
# coding=utf-8

import os
import os.path
import re
import match_algo.tfidf as TI
import match_algo.sif_embedding as SIF

dataDir = './data/format_data'
sif = SIF.SIF()

#定位段落
def findTopKPara(query, file, k = 3):
    scores = {}
    topKPara = []
    with open(dataDir + '/' + file, 'r') as f:
        for i, para in enumerate(f):
            scores[para.strip()] = TI.tfidf_similarity(query, para) 
        sorted_scores = sorted(scores.items(), key=lambda item:item[1], reverse=True)
        for item in sorted_scores[:k]:
            topKPara.append(item[0])
        return topKPara

#在段落内定位句子范围
def findTopKPart(query, paras, k = 3):
    scores = {}
    topKPart = []
    queryList = query.split('.!?')
    n = len(queryList)
    #print queryList
    #print n
    for item in paras:
        #print '[ ' + item + ']'
        sentences = re.split(r"([.!?])", item)
        sentences = ["".join(i) for i in zip(sentences[0::2], sentences[1::2])]
        m = len(sentences)
        i = 0
        while(i + n <= m):
            part = sentences[i].strip()
            for s in sentences[i+1:i+n]:
                part += ' ' + s.strip()
            #print part
            scores[part.strip()] = TI.tfidf_similarity(query, part)
            i += 1
    sorted_scores = sorted(scores.items(), key=lambda item:item[1], reverse=True)
    #print sorted_scores
    for item in sorted_scores[:k]:
        topKPart.append((item[0], item[1]))

    print topKPart
    return topKPart

def calSimilarityBySIF(query, topPart):
    SIFscore = {}
    for item in topPart:
        sentence = item[0]
        SIFscore[sentence] = sif.calSIF(query, sentence) 
    print SIFscore
    sorted_SIFscore = sorted(SIFscore.items(), key=lambda item:item[1], reverse=True)
    return sorted_SIFscore

def main():
    #query = 'our design has been driven by observations of our application workloads and technological environment'
    query = 'However, hot spots did develop when GFS was ﬁrst used by a batch-queue system: an executable was written to GFS as a single-chunk ﬁle and then started on hundreds of machines at the same time.'
    topKpara = findTopKPara(query, 'new_GFS.txt', 3)
    topKPart = findTopKPart(query, topKpara, 3)
    SIFscore = calSimilarityBySIF(query, topKPart) 
    print SIFscore[0]

if __name__ == '__main__':
    main()
