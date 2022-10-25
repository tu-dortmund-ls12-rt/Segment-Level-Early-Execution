import copy
from drs import drs
import numpy as np
import random

# Suspension ratio mode
# mod_r == 0: short suspension
# mod_r == 1: moderate suspension
# mod_r == 2: long suspension

# Number of suspension segments:
# mod_s == 0: rare suspension, 2 segments
# mod_s == 1: moderate suspension, 5 segments
# mod_s == 2: frequent suspension, 8 segments

# task sets generator for uni-processor systems
def generate(ntasks, msets, utilization, mod_r, mod_s):

    tasksets = []

    periods = [1, 2, 5, 10, 20, 50, 100, 200, 1000]
    # self-suspension range
    suspension_ratio = [[0.01, 0.1], [0.1, 0.3], [0.3, 0.6]]
    possible_segments = [2, 5, 8]

    for i in range(msets):
        taskset = []
        # total utilization for each task set
        util_tasks = drs(ntasks, utilization)
        for j in range(ntasks):
            task = []
            # total execution time
            execution_total = util_tasks[j]
            # total suspension time
            sus_ratio = np.random.uniform(suspension_ratio[mod_r][0], suspension_ratio[mod_r][1])
            suspension_total = sus_ratio * (1-execution_total)
            # each task has 2, 5, 8 segments
            num_segments = possible_segments[mod_s]
            executions = drs(num_segments, execution_total)
            suspensions = drs((num_segments-1), suspension_total)
            # construct the task w.r.t. utilizations
            for k in range(num_segments-1):
                task.append(executions[k])
                task.append(suspensions[k])
            task.append(executions[-1])

            period = periods[np.random.randint(0, 9)]
            # task w.r.t. execution times
            for k in range(num_segments*2-1):
                task[k] = task[k] * period
            # attach the utilization (for ordering later)
            task.append(execution_total)
            # attach the period in the end
            task.append(period)
            taskset.append(task)			
        tasksets.append(taskset)
    return tasksets

