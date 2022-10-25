from __future__ import division
import numpy as np
import os
import math
import sys
import getopt
import csv

def main(argv):
    ntasks = 10
    msets = 100
    processors = 1
    suspension_length_mod = 0
    # suspension mode: 0-short, 1-moderate, 2-long
    suspension_num_mod = 0
    # num_segments mode: 0-2, 1-5, 2-8
    lbd = 1
    ubd = 1

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

    for i in range(5, 101, 5):
        utli = float(i / 100)
        tasksets_name = '../experiments/inputs/tasksets_n' + str(ntasks) + '_m' + str(msets) + '_p' + str(
            processors) + '_r' + str(suspension_length_mod) + '_s' + str(suspension_num_mod) + '_u' + str(utli) + '.npy'

        tasksets_org = np.load(tasksets_name, allow_pickle=True)

        job_name = '../experiments/inputs/jobs/jobs_n' + str(ntasks) + '_m' + str(msets) + '_p' + str(
            processors) + '_r' + str(suspension_length_mod) + '_s' + str(suspension_num_mod) + '_l' + str(lbd) + '_h' + str(ubd) + '_u' + str(utli) + '.npy'

        jobs_set = []
        for st in range(0, msets):
            jobs = []
            for ntsk in range(0, ntasks):
                for per in range(0, 1000, int(tasksets_org[st][ntsk][-1])):
                    job = []
                    # real execution times and suspension times
                    for jb in range(len(tasksets_org[st][ntsk])-2):
                        job.append(tasksets_org[st][ntsk][jb] * np.random.uniform(lbd, ubd))
                    # utilization for total executions (except the suspensions)
                    job.append(tasksets_org[st][ntsk][-2])
                    # period
                    job.append(int(tasksets_org[st][ntsk][-1]))
                    # starting time
                    job.append(int(per))
                    # deadline
                    job.append(int(per + tasksets_org[st][ntsk][-1]))
                    # id of task
                    job.append(int(ntsk))
                    jobs.append(job)
            jobs_set.append(jobs)
        np.save(job_name, jobs_set)

if __name__ == "__main__":
    main(sys.argv[1:])