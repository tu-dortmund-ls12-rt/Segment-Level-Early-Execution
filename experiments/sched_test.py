from __future__ import division
import numpy as np
import math
import sys
import getopt
import os
import json

sys.path.append('../')
from algorithms import list_sched


tasks_org = [[[1, 3, 1, 0.4, 5], [1, 3, 1, 0.4, 5]], [[1, 3, 1, 0.4, 5], [1, 3, 1, 0.4, 5]]]
jobs_org = [[[1, 3, 1, 0.4, 5, 0, 5, 0], [1, 3, 1, 0.4, 5, 0, 5, 1]], [[1, 3, 1, 0.4, 5, 0, 5, 0], [1, 3, 1, 0.4, 5, 0, 5, 1]]]

sched_ss_edf = list_sched.edf_ss_sched(jobs_org, 2, 5)
sched_ss_rm = list_sched.rm_ss_sched(tasks_org, jobs_org, 2, 5)