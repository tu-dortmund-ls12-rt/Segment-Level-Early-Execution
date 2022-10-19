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

    try:
        opts, args = getopt.getopt(argv, "hn:m:p:s:",
                                   ["ntasks=", "msets=", "processors", "smod="])
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

    for i in range(101, 105, 5):
        utli = float(i / 100)
        tasksets_name = '../experiments/inputs/tasksets_n' + str(ntasks) + '_m' + str(msets) + '_p' + str(processors) + '_s' + str(suspension_mod) + '_u' + str(utli) + '.npy'
        tasksets = gen.generate(ntasks, msets, processors * utli, suspension_mod)
        np.save(tasksets_name, tasksets)

if __name__ == "__main__":
    main(sys.argv[1:])
