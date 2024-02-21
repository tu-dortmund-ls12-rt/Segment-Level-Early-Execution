from __future__ import division

import json

import numpy as np
import os
import math
import sys
import getopt
import csv
import random

def main(argv):
    ntasks = 10
    msets = 100
    processors = 1
    suspension_length_mod = 0
    # suspension mode: 0-short, 1-moderate, 2-long
    suspension_num_mod = 0
    # num_segments mode: 0-2, 1-5, 2-8
    num_segments = [2, 5, 8]
    # jitter mode: 0-short, 1-moderate, 2-long
    jitter_length_mod = 0
    lbd = 1
    ubd = 1

    jitters = [[0, 0.01], [0.01, 0.05], [0.05, 0.1], [0.03, 0.03]]


    try:
        opts, args = getopt.getopt(argv, "hn:m:p:r:s:l:u:j:", ["ntasks=", "msets=", "processors", "rmod=", "smod=", "lbd=", "ubd=", "jittermod="])
    except getopt.GetoptError:
        print ('tasksets_generater.py -n <n tasks for each set> -m <m tasksets> -p <num of processors> -s <suspension mod> -l <lower bound for real ET> -u <upper bound for real ET>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('tasksets_generater.py -n <n tasks for each set> -m <m tasksets> -p <num of processors> -s <suspension mod> -l <lower bound for real ET> -u <upper bound for real ET>')
            sys.exit()
        elif opt in ("-n", "--ntasks"):
            ntasks = int(arg)
        elif opt in ("-m", "--msets"):
            msets = int(arg)
        elif opt in ("-p", "--processors"):
            processors = int(arg)
        elif opt in ("-r", "--rmod"):
            suspension_length_mod = int(arg)
        elif opt in ("-s", "--smod"):
            suspension_num_mod = int(arg)
        elif opt in ("-l", "--lbd"):
            lbd = int(arg)
        elif opt in ("-u", "--ubd"):
            ubd = int(arg)
        elif opt in ("-j", "--jittermod"):
            jitter_length_mod = int(arg)

    for i in range(5, 101, 5):
        utli = float(i / 100)
        tasksets_name = '../experiments/inputs/tasksets_n' + str(ntasks) + '_m' + str(msets) + '_p' + str(processors) + '_r' + str(suspension_length_mod) + '_s' + str(suspension_num_mod) + '_u' + str(utli) + '.npy'
        jitter_name = '../experiments/inputs/jitter/tasksets_jitter_n' + str(ntasks) + '_m' + str(msets) + '_p' + str(
            processors) + '_r' + str(suspension_length_mod) + '_s' + str(suspension_num_mod) + '_u' + str(
            utli) + '_j' + str(jitter_length_mod) + '.npy'

        tasksets_org = np.load(tasksets_name, allow_pickle=True)

        jitter_sets = []

        for j in range(msets):
            jitter_set = []
            for k in range(ntasks):
                jitter = random.uniform(jitters[jitter_length_mod][0], jitters[jitter_length_mod][1])

                jitter_set.append(jitter)
            jitter_sets.append(jitter_set)
        np.save(jitter_name, jitter_sets)

        #np.save(jitter_name, np.array(jitter_sets, dtype=object))


if __name__ == "__main__":
    main(sys.argv[1:])