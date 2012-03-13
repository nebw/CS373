#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys 
reload(sys) 
sys.setdefaultencoding('utf8')

colors = [['red', 'green', 'green', 'red' , 'red'],
          ['red', 'red', 'green', 'red', 'red'],
          ['red', 'red', 'green', 'green', 'red'],
          ['red', 'red', 'red', 'red', 'red']]

measurements = ['green', 'green', 'green' ,'green', 'green']


motions = [[0,0],[0,1],[1,0],[1,0],[0,1]]

sensor_right = 0.8

p_move = 0.6

def show(p):
     for i in range(len(p)):
         for w in range(len(p[0])):
             print "%.4f" % p[i][w],
         print '.' * 45
     print '.' * 80

def spark_matrix(data):
	#by roquin https://github.com/roquin
    #ticks = u'▁▂▃▄▇█'
    # If the last symbol in ticks does not look good, uncomment the next line.
    ticks = u'▁▂▃▄▅▆▇'
    maxV = max(max(l) for l in data)
    minV = min(min(l) for l in data)
    step = float(maxV - minV) / len(ticks)
    for row in data:
        heights = []
        for n in row:
            height = 0
            if step != 0:
                height = int((n - minV)/step)
                if height == len(ticks):
                    height = len(ticks) - 1
            heights.append(height)
        print ''.join(ticks[i] for i in heights)

def calculate(debug=False):      
    dimX = len(colors[0])
    dimY = len(colors)
    uniform_fraction = 1. / (dimX * dimY)

    p = [[uniform_fraction] * dimX] * dimY

    def calc_sum(p):
        sum = 0
        for i in range(len(p)):
            for j in range(len(p[i])):
                sum += p[i][j]
        return sum

    def normalize(p, sum_p):
        for i in range(len(p)):
            for j in range(len(p[i])):
                p[i][j] /= sum_p
        return p
        
    def sense(p, Z):
        q = []
        for i in range(len(p)):
            q.append([])
            for j in range(len(p[i])):
                hit = colors[i][j] == Z
                q[i].append(p[i][j] * (hit * sensor_right + (1-hit) * (1-sensor_right)))
        sum_p = calc_sum(q)
        q = normalize(q, sum_p)
        return q

    def move(p, U):
        q = []
        for i in range(len(p)):
            q.append([])
            for j in range(len(p[i])):
                #robot moves
                s = p[(i-U[0])%len(p)][(j-U[1])%len(p[i])] * p_move
                #robot does not move
                s += p[i][j] * (1-p_move)
                q[i].append(s)
        return q

    if debug:
        print 'initial distribuation:'
        spark_matrix(p)
    for k in range(len(measurements)):
        p = move(p, motions[k])
        if debug:
            print 'move {}'.format(motions[k])
            spark_matrix(p)
        p = sense(p, measurements[k])
        if debug:
            print 'sense {}'.format(measurements[k])
            spark_matrix(p)

    return p

if __name__ == '__main__':
    calculate(debug=True)

