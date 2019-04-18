#!/usr/bin/env python
# coding=utf-8

import os.path

def procData(path):
    files = os.listdir(path)
    for file in files:
        print file
        if os.path.isfile(path + '/' + file):
            portion = os.path.splitext(file)
            targetFile = path + '/new_' + portion[0] + '.txt'
            fp = open(path + '/' + file)
            targetFp = open(targetFile, 'a+')
            paraList = []
            emptyLineFlag = 1 #上面一行是空行的标志，1表示上一行是空行
            lineWordNum = 0   #一行的词数
            paraWordNum = 0   #整篇文章的词数
            para = ""
            i = 0
            for line in fp: 
                i += 1
                if line.strip() == '': #整行为空
                    emptyLineFlag = 1
                    #print para
                    writePara2List(para, paraWordNum, paraList)
                    lineWordNum = paraWordNum = 0
                    para = ""
                else: #这行不为空
                    words = line.split()
                    curLineWordNum = len(words)
                    if (curLineWordNum < 4 and lineWordNum < 4) or (para != '' and para[-1] == '.' and line.strip()[-1] != '.'):
                        #当前行和前一行都是短文本，或者上一行已经结束，这一行没有句号
                        lineWordNum = curLineWordNum
                    else: 
                        lineWordNum = curLineWordNum
                        para = AddLine2Para(para, line, words[-1])
                        paraWordNum += curLineWordNum
                        #if line == "tional choices and explored radically diﬀerent points in the\n":
            writePara2List(para, paraWordNum, paraList)
            writeList2File(paraList, targetFp)

def writePara2List(para, allNum, paraList):
    if allNum < 10:
        pass
    else:
        if para != "":
            paraList.append(para)

def writeList2File(paraList, targetFp):
    length = len(paraList)
    print length
    i = 0
    while(i < length):
        if i == 49:
            print paraList[i]
            print paraList[i+1]
            print paraList[i][-1]
            print paraList[i+1][0]
        if (paraList[i] != '' and paraList[i][-1] != '.') and (i + 1 < length and paraList[i+1] != '' and paraList[i+1][0].islower()):
            para = paraList[i] + ' ' + paraList[i+1] + '\n'
            if i == 49:
                print para
            targetFp.write(para)
            i = i + 2
        else:
            para = paraList[i] + '\n'
            targetFp.write(para)
            i = i + 1

def AddLine2Para(para, line, lastWord):
    if para == '':
        para += line.strip()
    else:
        bNeedSpace = True
        if para[-1] == '-':#只有para还有最后的连字符'-'才不用加空格
            para = para[:-1] 
            bNeedSpace = False
        if bNeedSpace:
            para += ' '
        para += line.strip()
    return para

def main():
    procData('/home/billdai/project/data')

if __name__ == '__main__':
    main()
    


