#!/usr/bin/env python
# coding=utf-8

import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from scipy.linalg import norm
from math import fabs


def tfidf_similarity(s1, s2):
    # 转化为TF矩阵
    cv = TfidfVectorizer()
    corpus = [s1, s2]
    vectors = cv.fit_transform(corpus).toarray()
    #print cv.get_feature_names()
    # 计算TF系数
    sqrtVec0 = norm(vectors[0])
    sqrtVec1 = norm(vectors[1])
    product = sqrtVec0 * sqrtVec1
    if fabs(product) < 1e-6:
        return 0.
    return np.dot(vectors[0], vectors[1]) / product

