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
    priorities = []
    for i in range(len(taskset)):
        priorities.append(sorted_tsk[i][0])

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
                current_time_temp_1 = scheduled[0][3] + scheduled[0][4]
            else:
                current_time_temp_1 = t + 1

            if sus_next_release:
                sus_next_release = deque(sorted(sus_next_release, key=lambda x: x[0]))
                current_time_temp_2 = sus_next_release[0][0]
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
        if count_release[i] * 2 - 1 == num_segments[i]:
            print("All segments are released!")
        else:
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
                    # if new sub job has shorter ddl
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
                current_time_temp_1 = scheduled[0][3] + scheduled[0][4]
            else:
                current_time_temp_1 = t + 1

            if sus_next_release:
                sus_next_release = deque(sorted(sus_next_release, key=lambda x: x[0]))
                current_time_temp_2 = sus_next_release[0][0]
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
        if count_release[i] * 2 - 1 == num_segments[i]:
            print("All segments are released!")
        else:
            print("something is wrong, less releases than expected!")
    return 1


# global edf to schedule the dga with harmonic periods
# also can be used for federated scheduling
# critical section is non-preemptive for the tasks that request the same resource
# but critical section can be preempted by the tasks (with earlier deadline) that request other resources.
def glb_edf(tasksets_org, processors, hyper_period, cs_order_org, deadlines):
    # one completed taskset with m tasks and n resoruces (m=80, n=8 in initial)
    tasksets_ini = copy.deepcopy(tasksets_org)
    tasksets = []
    for i in range(len(tasksets_ini)):
        task_single = []
        for j in range(len(tasksets_ini[i])):
            if (type(tasksets_ini[i][j]) != int):
                task_single.append(list(tasksets_ini[i][j]))
            else:
                task_single.append(int(tasksets_ini[i][j]))
        tasksets.append(task_single)

    cs_order = []
    num_tsk = []
    constraints = []
    max_period = hyper_period

    # init the num_tsk
    for i in range(len(tasksets)):
        num_tsk.append(len(tasksets[i]) - 4)

    for i in range(len(cs_order_org) -1 ):
        single_cs = []
        for j in range(len(cs_order_org[i])):
            single_cs.append(cs_order_org[i][j])
        cs_order.append(single_cs)


    # init the constraints
    constraints = constraints_gen(num_tsk, cs_order)

    # integrate the precedence constraints
    for i in range(len(cs_order)):

        if (len(cs_order[i]) == 1):
            tasksets[cs_order[i][len(cs_order[i]) - 1][0]][cs_order[i][len(cs_order[i]) - 1][1]].append([-1, -1])
        elif (len(cs_order[i]) > 1):
            for j in range(len(cs_order[i])-1):
                tasksets[cs_order[i][j][0]][cs_order[i][j][1]].append(cs_order[i][j+1])
            tasksets[cs_order[i][len(cs_order[i])-1][0]][cs_order[i][len(cs_order[i])-1][1]].append([-1, -1])

    # initialize the current scheduled task
    scheduled = deque()

    # init one ready queue for global scheduling
    ready_list = deque()

    current_time = 0
    next_check = 10

    finished = 1

    for t in range(0, max_period):
        # find all the ready tasks at that time point

        for i in range(len(num_tsk)):
            if (tasksets[i][num_tsk[i]+1] == t):
                # [[tsk_id, part_id], release_time, deadline, starting to be scheduled, rest execution time, point to next sub-task]
                # the last item point to next sub-task only useful for critical section
                ready_list.append([[i, 0], t, deadlines[i][0], t, tasksets[i][0][0], [i, 1]])

        current_time = t

        # select the sub-job to execute
        while (current_time < (t+1)):


            # check the whether the scheudled task has finished at that moment
            if(scheduled):
                scheduled = deque(sorted(scheduled, key=lambda x: (x[3] + x[4])))
                for s in range(0, len(scheduled)):
                    possible_finished = scheduled.popleft()

                    if(current_time > possible_finished[2]):
                        #print ('miss the deadline 1')
                        return 0

                    if((possible_finished[3]+possible_finished[4]) <= current_time):
                        # the task hasn't been preempted
                        # update the constraints
                        constraints = const_update(constraints, possible_finished[0], possible_finished[5])

                        # if normal is finished, critical section will be checked
                        if(possible_finished[0][1]%2 == 0 and possible_finished[0][1] < (num_tsk[possible_finished[0][0]] - 1)):
                            low_task = [possible_finished[0][0], possible_finished[0][1]+1]
                            if(is_ready(constraints, low_task)):

                                ready_list.append([low_task, current_time, deadlines[low_task[0]][low_task[1]], 0, tasksets[low_task[0]][low_task[1]][0], tasksets[low_task[0]][low_task[1]][2]])
                                #print ('low task 1: ', low_task, ' is released at time: ', current_time)
                        # if critical section is finished
                        if(possible_finished[0][1]%2 == 1):
                            low_task = [possible_finished[0][0], possible_finished[0][1]+1]
                            ready_list.append([low_task, current_time, deadlines[low_task[0]][low_task[1]], 0, tasksets[low_task[0]][low_task[1]][0], [low_task[0], low_task[1] + 1]])
                            #print ('low task 2: ', low_task, ' is released at time: ', current_time)
                            # if this critical section is not the last one for corresponding resource
                            if(possible_finished[5][0] != -1):
                                right_task = [possible_finished[5][0], possible_finished[5][1]]
                                if(is_ready(constraints, right_task)):

                                    ready_list.append([right_task, current_time, deadlines[right_task[0]][right_task[1]], 0, tasksets[right_task[0]][right_task[1]][0], tasksets[right_task[0]][right_task[1]][2]])
                                    #print ('right task: ', right_task, ' is released at time: ', current_time)
                    # hasn't finished as expected, requeue it back
                    else:
                        scheduled.append(possible_finished)
                        break

            # pick up the ready task with the earlist deadline,
            # if the time is new release, new jobs may preempted all the scheduled jobs,
            # otherwise, the previous finished job can only release two new jobs (low and right)
            if (ready_list):
                if (current_time == t):
                    num_new_jobs = min(processors, len(ready_list))
                else:
                    num_new_jobs = min(2, len(ready_list))

                for p in range(0, num_new_jobs):
                    ready_list = deque(sorted(ready_list, key=lambda x: x[2]))
                    # in case there are several tasks have the same deadline
                    # the task with the longest execution time has highest priority

                    deadline_temp = ready_list[0][2]

                    temp_ready_list = deque()
                    # get all the tasks with the same deadline

                    for posid in range(0, len(ready_list)):
                        if (ready_list[0][2] == deadline_temp):
                            temp_ready_list.append(ready_list.popleft())
                        else:
                            break

                    if (len(temp_ready_list) == 1):
                        task = temp_ready_list.pop()
                    else:
                        temp_ready_list = deque(sorted(temp_ready_list, key=lambda x: x[4]))
                        task = temp_ready_list.pop()
                        # put the rest tasks back to the original ready list
                        for posid in range(0, len(temp_ready_list)):
                            ready_list.appendleft(temp_ready_list.pop())

                        # schedule the task
                    if(len(scheduled)<processors):
                        task[3] = current_time
                        next_check = task[3] + task[4]
                        #
                        # miss the deadline for sure, return 0
                        if (next_check > task[2]):
                            #print ('miss the deadline 2')
                            #print ('scheduled task', task)
                            #print ('current time:', task[3], ' execution time:', task[4], ' deadline:', task[2])
                            return 0
                        else:
                            scheduled.append(task)
                    else:
                        # check the scheduled sub-job, whether it can be preempted
                        scheduled = deque(sorted(scheduled, key=lambda x: x[2]))
                        # preempt the task with later deadline
                        # if they have the same deadline, the task with the longer execution time has the higer priority
                        if((scheduled[(processors-1)][2] > task[2]) or ((scheduled[(processors-1)][2] == task[2]) and ((scheduled[(processors-1)][4] - (current_time-scheduled[len(scheduled)-1][3])) < task[4]))):
                            preempted_task = scheduled.pop()
                            # update the rest execution time
                            preempted_task[4] = preempted_task[4] - (current_time-preempted_task[3])
                            #print ('preempted task', preempted_task)
                            ready_list.append(preempted_task)
                            # update the starting time of the new scheduled task
                            task[3] = current_time
                            next_check = task[3] + task[4]
                            #print ('edf task', task)
                            # miss the deadline for sure, return 0
                            if (next_check > task[2]):
                                #print ('miss the deadline 3')
                                return 0
                            else:
                                scheduled.append(task)
                        else:
                            ready_list.append(task)
            # update the current time for the next checking point
            # if((len(scheduled) <= processors) or (len(ready_list) == 0)):
            if (scheduled):
                scheduled = deque(sorted(scheduled, key=lambda x: (x[3]+x[4])))
                current_time = scheduled[0][3] + scheduled[0][4]
            else:
                current_time = t+1
            #print ('current time: ', current_time)
    # in the end, we still have at least one job in the ready list, not schedulable
    if(len(ready_list) > 0):
        #print ('miss the deadline 4')
        return 0

    # check all the scheduled tasks in the end of the hyper-period
    current_time = max_period
    if(len(scheduled) > 0):
        for s in range(0, len(scheduled)):
            still_running = scheduled.popleft()
            if((still_running[3]+still_running[4])>current_time):
                #print ('miss the deadline 5')
                return 0
    # print ('schedulable')
    return 1





##################################################################################
# collect the acceptance ratio (schedulability test) according different algorithms
def edf_ss_sched(tasksets, num_sets, hyper_period):
    tasksets = copy.deepcopy(tasksets)
    n_sets = num_sets
    accepted = 0

    for i in range(0, n_sets):
        num_segments = []
        for j in range(len(tasksets[i])):
            num_segments.append(len(tasksets[i][j]) - 5)
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
    print (accepted)
    return accepted