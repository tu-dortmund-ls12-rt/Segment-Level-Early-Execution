from __future__ import division

import json

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
    num_segments = [2, 5, 8]
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

    ratio = 10**5

    csv_name = '../experiments/inputs/csv/tasksets_n' + str(ntasks) + '_m' + str(msets) + '_p' + str(
        processors) + '_r' + str(suspension_length_mod) + '_s' + str(suspension_num_mod) + '.csv'

    header = ['period', 'execution', 'deadline', 'utilization', 'sslength', 'minSr', 'paths', 'Cseg', 'Sseg']
    header_2 = ['Cseg', 'Sseg', 'deadline']

    with open(csv_name, 'w', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        for i in range(5, 101, 5):
            utli = float(i / 100)
            tasksets_name = '../experiments/inputs/tasksets_n' + str(ntasks) + '_m' + str(msets) + '_p' + str(processors) + '_r' + str(suspension_length_mod) + '_s' + str(suspension_num_mod) + '_u' + str(utli) + '.npy'

            tasksets_org = np.load(tasksets_name, allow_pickle=True)

            for j in range(msets):
                for k in range(ntasks):
                    exec_segments = []
                    sus_segmants = []
                    # calculate the deadlines
                    deadlines = []
                    # prepare the execution and suspension segments
                    for seg in range(0, len(tasksets_org[j][k])-3, 2):
                        exec_segments.append(math.ceil(tasksets_org[j][k][seg] * ratio))
                        sus_segmants.append(math.ceil(tasksets_org[j][k][seg+1] * ratio))
                        deadlines.append(-1)
                    exec_segments.append(math.ceil(tasksets_org[j][k][-3] * ratio))
                    deadlines.append(-1)

                    task_csv = []
                    # period
                    task_csv.append(int(tasksets_org[j][k][-1] * ratio))
                    # total execution
                    task_csv.append(sum(exec_segments))
                    # deadline
                    task_csv.append(int(tasksets_org[j][k][-1] * ratio))
                    # utilization
                    task_csv.append(tasksets_org[j][k][-2])
                    # suspension length: sslength
                    task_csv.append(int(sum(sus_segmants)))
                    # minimal number of segments: minSr
                    task_csv.append(num_segments[suspension_num_mod])
                    # Path
                    path_dict = {}
                    path_dict['Cseg'] = exec_segments
                    path_dict['Sseg'] = sus_segmants
                    path_dict['deadline'] = deadlines
                    # json_path = json.dumps([path_dict])
                    task_csv.append([path_dict])
                    #Cseg
                    task_csv.append(exec_segments)
                    #Sseg
                    task_csv.append(sus_segmants)

                    writer.writerow(task_csv)


if __name__ == "__main__":
    main(sys.argv[1:])