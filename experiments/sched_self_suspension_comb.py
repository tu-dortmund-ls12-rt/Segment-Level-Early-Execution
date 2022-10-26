from __future__ import division
import numpy as np
import math
import sys
import getopt
import os
import json

sys.path.append('../')
from algorithms import list_sched

def main(argv):
    ntasks = 10
    msets = 100
    processors = 1
    suspension_length_mod = 0
    suspension_num_mod = 0
    lbd = 1
    ubd = 1
    hyper_period = 1000

    try:
        opts, args = getopt.getopt(argv, "hn:m:p:r:s:l:u:", ["ntasks=", "msets=", "processors", "rmod=", "smod=", "lbd=", "ubd="])
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

    sched = []

    sched_name_ss = './outputs/results_combined_sched_n'+ str(ntasks) + '_m' + str(msets) + '_p' + str(
            processors) + '_r' + str(suspension_length_mod) + '_s' + str(suspension_num_mod) + '.npy'

    print ('Starting series...')

    for i in range(5, 101, 5):
        utli = float(i / 100)
        sched_utli = []

        tasksets_name = './inputs/tasksets_n' + str(ntasks) + '_m' + str(msets) + '_p' + str(
            processors) + '_r' + str(suspension_length_mod) + '_s' + str(suspension_num_mod) + '_u' + str(utli) + '.npy'
        tasksets_org = np.load(tasksets_name, allow_pickle=True)

        job_name = './inputs/jobs/jobs_n' + str(ntasks) + '_m' + str(msets) + '_p' + str(
            processors) + '_r' + str(suspension_length_mod) + '_s' + str(suspension_num_mod) + '_l' + str(lbd) + '_h' + str(ubd) + '_u' + str(utli) + '.npy'

        jobs_org = np.load(job_name, allow_pickle=True)

        ##########################################################################################

        sched_ss_rm = list_sched.combined_ss_sched(tasksets_org, jobs_org, msets, hyper_period)
        sched_utli.append(sched_ss_rm)

        sched.append(sched_utli)
    
    np.save(sched_name_ss, sched)

if __name__ == "__main__":
    main(sys.argv[1:])
