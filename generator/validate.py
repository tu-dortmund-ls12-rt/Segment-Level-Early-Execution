from __future__ import division
import numpy as np
import generator as gen
import os
import math
import sys
import getopt


def main(argv):
    ntasks = 10
    msets = 100
    processors = 1
    suspension_mod = 0
    # suspension mode: 0-short, 1-moderate, 2-long
    util = 90

    try:
        opts, args = getopt.getopt(argv, "hn:m:p:s:u:",
                                   ["ntasks=", "msets=", "processors", "smod=", "util="])
    except getopt.GetoptError:
        print ('tasksets_generater_periodic.py -n <n tasks for each set> -m <m tasksets> -p <num of processors> -s <suspension mod>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('tasksets_generater_periodic.py -n <n tasks for each set> -m <m tasksets> -p <num of processors> -s <suspension mod>')
            sys.exit()
        elif opt in ("-n", "--ntasks"):
            ntasks = int(arg)
        elif opt in ("-m", "--msets"):
            msets = int(arg)
        elif opt in ("-p", "--processors"):
            processors = int(arg)
        elif opt in ("-s", "--smod"):
            suspension_mod = int(arg)
        elif opt in ("-u", "--util"):
            util = int(arg)


    utilization = float(util / 100)
    tasksets_name = '../experiments/inputs/tasksets_n' + str(ntasks) + '_m' + str(msets) + '_p' + str(processors) + '_s' + str(suspension_mod) + '_u' + str(utilization) + '.npy'
    tasksets = np.load(tasksets_name, allow_pickle=True)

    for i in range(msets):
        util_acc = 0
        util_sus_acc = 0
        for j in range(ntasks):
            exec_acc = 0
            sus_acc = 0
            for k in range(0, len(tasksets[i][j])-1, 2):
                exec_acc = exec_acc + tasksets[i][j][k]
            for k in range(1, len(tasksets[i][j])-2, 2):
                sus_acc = sus_acc + tasksets[i][j][k]
            util_acc = util_acc + exec_acc/tasksets[i][j][-1]
            util_sus_acc = util_sus_acc + sus_acc/tasksets[i][j][-1]
        print(util_acc)
        print(util_sus_acc)

if __name__ == "__main__":
    main(sys.argv[1:])