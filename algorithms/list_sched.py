import numpy as np
import math
import copy
from collections import deque
import sys

# Update the deadlines for each sub-job according to their sequence
# Used for EDF scheduling
def deadline_update(task_set):
    taskset = copy.deepcopy(task_set)
    deadlines = []
    # initialize the deadlines for all the sub-tasks using the corresponding period
    for i in range(len(taskset)):
        ddl = []
        ddl_single = taskset[i][-2]
        for j in range(len(taskset[i])-5):
            ddl.append(ddl_single)
        for j in range(len(taskset[i])-7, -1, -1):
            ddl[j] = ddl[j+1] - taskset[i][j+1]
        deadlines.append(ddl)
    return deadlines

# Prioditiy assignment according to Rate-Monotonic scheduling
# Used for RM scheduling
def rm_priority(task_set):
    taskset = copy.deepcopy(task_set)
    list_enum = list(enumerate(taskset))
    sorted_tsk = sorted(list_enum, key = lambda x: (x[1][-1], -x[1][-2]))
    # initialize the priorities array
    priorities = np.zeros(len(taskset))
    for i in range(len(taskset)):
        priorities[sorted_tsk[i][0]] = i
        # the smaller number means higher priority
    return priorities

# EDF scheduling
def edf_self_suspension(tasksets_org, hyper_period, deadlines, num_segments):
    tasksets = copy.deepcopy(tasksets_org)

    # initialize the current scheduled task
    scheduled = deque()

    # init one ready queue for global scheduling
    ready_list = deque()

    # suspension time checker
    sus_next_release = deque()

    count_release = np.zeros(len(tasksets))

    for t in range (0, hyper_period):
        # find all the ready tasks at that time point
        for i in range(len(tasksets)):
            if (tasksets[i][-3] == t):
                # [[tsk_id, part_id], release_time, deadline, starting to be scheduled, rest execution time]
                ready_list.append([[i, 0], t, deadlines[i][0], t, tasksets[i][0]])
                count_release[i] = count_release[i] + 1
        current_time = t

        while (current_time < (t + 1)):
            # check whether the scheduled job finishes at the time point
            if (scheduled):
                possible_finished = scheduled.popleft()
                # deadline miss
                if (current_time > possible_finished[2]):
                    return 0
                # finish the execution of current segment
                if ((possible_finished[3]+possible_finished[4]) <= current_time):
                    # still have following segment(s)
                    if possible_finished[0][1] < num_segments[possible_finished[0][0]]-1:
                        # enqueue the release of next segment
                        # [release time, job_id, segment_id]
                        sus_next_release.append([current_time+tasksets[possible_finished[0][0]][possible_finished[0][1]+1], possible_finished[0][0], possible_finished[0][1]+2])
                else:
                    # append back the job
                    scheduled.append(possible_finished)

            # release the suspended sub-job(s)
            if (sus_next_release):
                sus_next_release = deque(sorted(sus_next_release, key=lambda x: x[0]))
                for ss in range(len(sus_next_release)):
                    if sus_next_release[0][0] <= current_time:
                        new_ss_release = sus_next_release.popleft()
                        ready_list.append([[new_ss_release[1], new_ss_release[2]], current_time, deadlines[new_ss_release[1]][new_ss_release[2]], current_time, tasksets[new_ss_release[1]][new_ss_release[2]]])
                        count_release[new_ss_release[1]] = count_release[new_ss_release[1]] + 1

            # find the next sub-job to be scheduled
            if (ready_list):
                ready_list = deque(sorted(ready_list, key=lambda x: (x[2], -x[4])))
                next_task = ready_list.popleft()
                # already scheduled sub-job exists
                if scheduled:
                    # if new sub job has shorter ddl
                    if (scheduled[0][2] > next_task[2]):
                    # preempt the current executing sub-job
                        # re-insert the sub-job to ready queue
                        preempted_job = scheduled.popleft()
                        preempted_job[4] = preempted_job[4] - current_time + preempted_job[3]
                        ready_list.append(preempted_job)
                        # schedule the new sub-job
                        if current_time + next_task[4] > next_task[2]:
                            return 0
                        else:
                            next_task[3] = current_time
                            scheduled.append(next_task)
                    else:
                        # new sub-job has longer ddl, re-insert to ready queue
                        ready_list.appendleft(next_task)
                # no sub-job is scheduled
                else:
                    # schedule the new sub-job
                    if current_time + next_task[4] > next_task[2]:
                        return 0
                    else:
                        next_task[3] = current_time
                        scheduled.append(next_task)

            # update the current time
            if scheduled:
                current_time_temp_1 = min(scheduled[0][3] + scheduled[0][4], t+1)
            else:
                current_time_temp_1 = t + 1

            if sus_next_release:
                sus_next_release = deque(sorted(sus_next_release, key=lambda x: x[0]))
                current_time_temp_2 = min(sus_next_release[0][0], t+1)
            else:
                current_time_temp_2 = t + 1

            current_time = min(current_time_temp_1, current_time_temp_2)

    # in the end, we still have at least one job in the ready list, not schedulable
    if (len(ready_list) > 0):
        return 0

    # check all the scheduled tasks in the end of the hyper-period
    current_time = hyper_period
    if (len(scheduled) > 0):
        still_running = scheduled.popleft()
        if ((still_running[3] + still_running[4]) > current_time):
            return 0

    for i in range(len(tasksets)):
        if count_release[i] * 2 - 1 != num_segments[i]:
            print("something is wrong, less releases than expected!")
    return 1

# RM scheduling
def rm_self_suspension(tasksets_org, hyper_period, deadlines, num_segments, priorities):
    tasksets = copy.deepcopy(tasksets_org)

    # initialize the current scheduled task
    scheduled = deque()

    # init one ready queue for global scheduling
    ready_list = deque()

    # suspension time checker
    sus_next_release = deque()

    count_release = np.zeros(len(tasksets))

    for t in range (0, hyper_period):
        # find all the ready tasks at that time point
        for i in range(len(tasksets)):
            if (tasksets[i][-3] == t):
                # [[tsk_id, part_id], release_time, deadline, starting to be scheduled, rest execution time, priority]
                ready_list.append([[i, 0], t, deadlines[i][0], t, tasksets[i][0], priorities[tasksets[i][-1]]])
                count_release[i] = count_release[i] + 1
        current_time = t

        while (current_time < (t + 1)):
            # check whether the scheduled job finishes at the time point
            if (scheduled):
                possible_finished = scheduled.popleft()
                # deadline miss
                if (current_time > possible_finished[2]):
                    return 0
                # finish the execution of current segment
                if ((possible_finished[3]+possible_finished[4]) <= current_time):
                    # still have following segment(s)
                    if possible_finished[0][1] < num_segments[possible_finished[0][0]]-1:
                        # enqueue the release of next segment
                        # [release time, job_id, segment_id]
                        sus_next_release.append([current_time+tasksets[possible_finished[0][0]][possible_finished[0][1]+1], possible_finished[0][0], possible_finished[0][1]+2])
                else:
                    # append back the job
                    scheduled.append(possible_finished)

            # release the suspended sub-job(s)
            if (sus_next_release):
                sus_next_release = deque(sorted(sus_next_release, key=lambda x: x[0]))
                for ss in range(len(sus_next_release)):
                    if sus_next_release[0][0] <= current_time:
                        new_ss_release = sus_next_release.popleft()
                        ready_list.append([[new_ss_release[1], new_ss_release[2]], current_time, deadlines[new_ss_release[1]][new_ss_release[2]], current_time, tasksets[new_ss_release[1]][new_ss_release[2]], priorities[tasksets[new_ss_release[1]][-1]]])
                        count_release[new_ss_release[1]] = count_release[new_ss_release[1]] + 1

            # find the next sub-job to be scheduled
            if (ready_list):
                ready_list = deque(sorted(ready_list, key=lambda x: x[5]))
                next_task = ready_list.popleft()
                # already scheduled sub-job exists
                if scheduled:
                    # if new sub job has higher priority
                    if (scheduled[0][5] > next_task[5]):
                    # preempt the current executing sub-job
                        # re-insert the sub-job to ready queue
                        preempted_job = scheduled.popleft()
                        preempted_job[4] = preempted_job[4] - current_time + preempted_job[3]
                        ready_list.append(preempted_job)
                        # schedule the new sub-job
                        if current_time + next_task[4] > next_task[2]:
                            return 0
                        else:
                            next_task[3] = current_time
                            scheduled.append(next_task)
                    else:
                        # new sub-job has longer ddl, re-insert to ready queue
                        ready_list.appendleft(next_task)
                # no sub-job is scheduled
                else:
                    # schedule the new sub-job
                    if current_time + next_task[4] > next_task[2]:
                        return 0
                    else:
                        next_task[3] = current_time
                        scheduled.append(next_task)

            # update the current time
            if scheduled:
                current_time_temp_1 = min(scheduled[0][3] + scheduled[0][4], t+1)
            else:
                current_time_temp_1 = t + 1

            if sus_next_release:
                sus_next_release = deque(sorted(sus_next_release, key=lambda x: x[0]))
                current_time_temp_2 = min(sus_next_release[0][0], t+1)
            else:
                current_time_temp_2 = t + 1
            current_time = min(current_time_temp_1, current_time_temp_2)

    # in the end, we still have at least one job in the ready list, not schedulable
    if (len(ready_list) > 0):
        return 0

    # check all the scheduled tasks in the end of the hyper-period
    current_time = hyper_period
    if (len(scheduled) > 0):
        still_running = scheduled.popleft()
        if ((still_running[3] + still_running[4]) > current_time):
            return 0

    for i in range(len(tasksets)):
        if count_release[i] * 2 - 1 != num_segments[i]:
            print("something is wrong, less releases than expected!")
    return 1


##################################################################################
# collect the acceptance ratio (schedulability test) according different algorithms
def edf_ss_sched(tasksets, num_sets, hyper_period):
    tasksets = copy.deepcopy(tasksets)
    n_sets = num_sets
    accepted = 0

    for i in range(0, n_sets):
        num_segments = []
        #util_acc = 0
        for j in range(len(tasksets[i])):
            #util_acc = util_acc + sum(tasksets[i][j][0:-5])/tasksets[i][j][-4]
            num_segments.append(len(tasksets[i][j]) - 5)
        #print(util_acc)
        deadlines = deadline_update(tasksets[i])
        accept = edf_self_suspension(tasksets[i], hyper_period, deadlines, num_segments)
        # print (accept)
        accepted = accepted + accept
    print (accepted)
    return accepted


def rm_ss_sched(task_org, tasksets, num_sets, hyper_period):
    tasks_org = copy.deepcopy(task_org)
    tasksets = copy.deepcopy(tasksets)
    n_sets = num_sets
    accepted = 0

    for i in range(0, n_sets):
        num_segments = []
        priorities = rm_priority(tasks_org[i])
        for j in range(len(tasksets[i])):
            num_segments.append(len(tasksets[i][j]) - 5)
        deadlines = deadline_update(tasksets[i])
        accept = rm_self_suspension(tasksets[i], hyper_period, deadlines, num_segments, priorities)
        # print (accept)
        accepted = accepted + accept
    #print (accepted)
    return accepted

def combined_ss_sched(task_org, tasksets, num_sets, hyper_period):
    tasks_org = copy.deepcopy(task_org)
    tasksets = copy.deepcopy(tasksets)
    n_sets = num_sets
    accepted = []

    for i in range(0, n_sets):
        num_segments = []
        priorities = rm_priority(tasks_org[i])
        for j in range(len(tasksets[i])):
            num_segments.append(len(tasksets[i][j]) - 5)
        deadlines = deadline_update(tasksets[i])
        accept_1 = rm_self_suspension(tasksets[i], hyper_period, deadlines, num_segments, priorities)
        accept_2 = edf_self_suspension(tasksets[i], hyper_period, deadlines, num_segments)
        # print (accept)
        accepted.append(max(accept_1, accept_2))
    #print (accepted)
    return accepted

def edf_ss_ob_sched(tasksets, num_sets, hyper_period):
    tasksets = copy.deepcopy(tasksets)
    n_sets = num_sets
    accepted = 0

    for i in range(0, n_sets):
        num_segments = np.ones(len(tasksets[i]))
        #util_acc = 0
        new_tsk_set = []
        deadlines = []
        for j in range(len(tasksets[i])):
            new_tsk = []
            deadline = []
            new_tsk.append(sum(tasksets[i][j][0:-5]))
            for k in range(-5, 0, 1):
                new_tsk.append(tasksets[i][j][k])
            #util_acc = util_acc + sum(tasksets[i][j][0:-5])/tasksets[i][j][-4]
            deadline.append(tasksets[i][j][-2])
            new_tsk_set.append(new_tsk)
            deadlines.append(deadline)
        # print(util_acc)
        accept = edf_self_suspension(new_tsk_set, hyper_period, deadlines, num_segments)
        # print (accept)
        accepted = accepted + accept
    print (accepted)
    return accepted

def rm_ss_ob_sched(task_org, tasksets, num_sets, hyper_period):
    tasks_org = copy.deepcopy(task_org)
    tasksets = copy.deepcopy(tasksets)
    n_sets = num_sets
    accepted = 0

    for i in range(0, n_sets):
        new_tsk_set = []
        deadlines = []
        num_segments = np.ones(len(tasksets[i]))
        priorities = rm_priority(tasks_org[i])
        for j in range(len(tasksets[i])):
            new_tsk = []
            deadline = []
            new_tsk.append(sum(tasksets[i][j][0:-5]))
            for k in range(-5, 0, 1):
                new_tsk.append(tasksets[i][j][k])
            # util_acc = util_acc + sum(tasksets[i][j][0:-5])/tasksets[i][j][-4]
            deadline.append(tasksets[i][j][-2])
            new_tsk_set.append(new_tsk)
            deadlines.append(deadline)

        accept = rm_self_suspension(new_tsk_set, hyper_period, deadlines, num_segments, priorities)
        # print (accept)
        accepted = accepted + accept
    print (accepted)
    return accepted