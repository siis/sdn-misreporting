#!/usr/bin/env python3.7
#
# File: parse_exp.py
#
# Description   : parse experimental results
# Date          : November 2019
# Last Modified : July 2020


### Imports ###
import matplotlib.pyplot as plt
import numpy as np
import sys
from scipy.stats import median_test, ks_2samp
import itertools
import csv


### Globals ###
NUM_MEMBERS = None
ATK_WINDOW_BEGIN = 900
ATK_WINDOW_END = 1200

LL=1
LC=2
POLICY=LL
div=1000.0 if POLICY==LL else 1.0
traffic_type = "Short"

marker = itertools.cycle((',', '+', '.', 'o', '*'))

### Functions ###

num_experiments = 1 # parse multiple lb-decisions files pasted into the directory (change this and the file name used in open below in order to test the stat tests)

def parse():
    ### Parse loads from lb-decisions
    member_loads = [{i: list() for i in range(1, NUM_MEMBERS+1)} for _ in range(num_experiments)]  # loads over time (in BPS)!!!
    load_files = [{i: open("load_data/load_values_mem-exp%d-mem%d.csv" % (exp_idx, i), 'w')
                  for i in range(1, NUM_MEMBERS+1)} for exp_idx in range(num_experiments)]
    for exp_idx in range(num_experiments):
        with open('pylb-output/lb-decisions') as f:
            try:
                lines = f.readlines()
                for i in range(len(lines)):
                    if lines[i].startswith('BANDWIDTH USAGE'):
                        i += 1
                        if i >= len(lines):
                            # print(i)
                            break
                        while True:
                            if i >= len(lines):
                                # print(i)
                                break
                            # keep going until you hit a '=======' or newline/space
                            if lines[i].startswith('00'):
                                # for j in range(NUM_MEMBERS):
                                member = lines[i].strip().strip(
                                    '\n').split('NodeID: ')[1].split(',')[0]
                                # load = int(lines[i].strip().strip('\n').split('): ')[1].split(' bps')[0], 16)/1000.0/8 # KB/s (bytes); simulator is in bytes
                                load = int(lines[i].strip().strip('\n').split('): ')[1].split(
                                    ' bps')[0], 16)/div  # Kb/s (using bits now)
                                # print("\nline: %s" %lines[i][:-1])
                                # print("test: ", lines[i].strip().strip('\n').split('): ')[1].split(' bps')[0])
                                # print("member: %s, load: %d" % (member, load))
                                if int(member) in member_loads[exp_idx].keys():
                                    member_loads[exp_idx][int(member)].append(load)
                                    load_files[exp_idx][int(member)].write(str(load)+"\n")
                                i += 1
                            else:
                                break
            finally:
                f.close()
        _ = [load_files[exp_idx][i].close() for i in range(1, NUM_MEMBERS+1)]
    print("============== Load Results (switch view for [10])\nOverall: ")
    member_avgs = [dict() for _ in range(num_experiments)]
    for exp_idx in range(num_experiments):
        for member in member_loads[exp_idx].keys():
            # print("member[%d] loads: " % key, member_loads[key])
            member_avgs[exp_idx][member] = np.mean(member_loads[exp_idx][member])
            # print("member[%s] average: %.3f KB" % (member, member_avgs[member]))
            print("member[%s] average: %.3f %s" % (member, member_avgs[exp_idx][member], "Kb" if POLICY==LL else "flows"))
        overall_avg = np.mean([member_avgs[exp_idx][member]
                            for member in member_avgs[exp_idx].keys()])
        print("overall average: %.3f %s" % (overall_avg, "Kb" if POLICY==LL else "flows"))

        print("====")

    print("During atk: ")
    member_avgs_during_atk = [dict() for _ in range(num_experiments)]
    for exp_idx in range(num_experiments):
        for member in member_loads[exp_idx].keys():
            # print("member[%d] loads: " % key, member_loads[key])
            member_avgs_during_atk[exp_idx][member] = np.mean(
                member_loads[exp_idx][member][ATK_WINDOW_BEGIN:ATK_WINDOW_END])
            print("member[%s] average_during_atk: %.3f %s" %
                (member, member_avgs_during_atk[exp_idx][member], "Kb" if POLICY==LL else "flows"))
        overall_avg_during_atk = np.mean(
            [member_avgs_during_atk[exp_idx][member] for member in member_avgs_during_atk[exp_idx].keys()])
        print("overall average_during_atk: %.3f %s\n" % (overall_avg_during_atk, "Kb" if POLICY==LL else "flows"))
        print("====")        


    ### Parse loads from recorded misreports and update them (if wanting to do controller view)
    controller_view = True
    misreported_epochs = [set() for _ in range(num_experiments)]
    if controller_view: # NOTE: this updates the dict in place so its reflected in graph()
        adversary_misreported_load_during_atk = [list() for _ in range(num_experiments)]
        for exp_idx in range(num_experiments):
            with open('pylb-output/adversary-misreported-loads-exp%d' % exp_idx) as f: # the reports that CONTROLLER sees
                try:
                    lines = f.readlines()
                    for i in range(len(lines)):
                        t = int(lines[i].strip().strip('\n').split('[')[1].split(']')[0].split('=')[1].split('s')[0])
                        load = int(lines[i].strip().strip('\n').split(']:')[1], 16)
                        # print("(t, load): ", (t, load))
                        adversary_misreported_load_during_atk[exp_idx].append((t, load))
                        misreported_epochs[exp_idx].add(t)
                finally:
                    f.close()

            # for i in range(ATK_WINDOW_BEGIN, ATK_WINDOW_END+1): # just simulate trivial atk to see what it looks like
            #     member_loads[exp_idx][NUM_MEMBERS][i] = 0
            for t,load in adversary_misreported_load_during_atk[exp_idx]: # just simulate trivial atk to see what it looks like
                member_loads[exp_idx][NUM_MEMBERS][t] = load # t should be correct index


    graph(member_loads)
    plot_computed_flow_durs()
    # run_stat_tests(member_loads)
    # find_largest_jump(member_loads, misreported_epochs)
    plot_shift(member_loads)
    # return member_loads

def plot_computed_flow_durs():

    plt.figure()
    with open('flooderc/computed-durs.csv', newline='') as f:
        reader = csv.reader(f)
        durs = list(map(float, list(itertools.chain.from_iterable(list(reader)))[:-1])) # last entry is empty
    # print("some: ", durs)
    print("mean dur: %.3fs" % np.mean(durs))

    sorted_durs = sorted(durs)
    cdf_durs = calc_cdf_fast(sorted_durs)
    plt.plot(sorted_durs, cdf_durs, linewidth=0.75) 
    
    # display plots
    # plt.ylim(0, 1)
    plt.xlabel("dur (s)", fontsize=15)
    plt.ylabel('cdf', fontsize=15)
    plt.grid(True, color='grey', linestyle=':', linewidth=0.25, alpha=0.25)
    plt.xticks([0,1,2,3,4,5], [0,1,2,3,4,5], fontsize=15)
    plt.yticks(fontsize=15)
    plt.title('computed durs', fontsize=14)
    plt.savefig('computed-durs.pdf')

"""
NOTE: just plots the first experiment (index 0 in member loads)
"""
def find_largest_jump(loads, misreported_epochs):
    print("============== Detector results (controller view for [10]) (adaptive flow counting)")
    print("misreported_epochs: ", sorted(misreported_epochs))

    # JUMP ANOMALIES
    jump_size = {i: list() for i in range(1, NUM_MEMBERS+1)}
    for mem in range(1, NUM_MEMBERS+1):
        prev = loads[0][mem][0]
        for i in range(1, len(loads[0][NUM_MEMBERS])):
            jump = loads[0][mem][i] - prev # compute the change
            if jump>0: # only record the increasing ones (says in paper)
                jump_size[mem].append(jump) # save to this members list
            else:
                jump_size[mem].append(None) # just mark as empty so we can still use correct indices
            prev = loads[0][mem][i] # make current load the next prev

    atk_max = max([j for j in jump_size[NUM_MEMBERS] if j is not None])
    atk_mean = np.mean([j for j in jump_size[NUM_MEMBERS] if j is not None])
    atk_std = np.std([j for j in jump_size[NUM_MEMBERS] if j is not None])
    atk_detection_bound = atk_mean+3*atk_std
    print("Attacker largest jump: %.2f" % (atk_max))
    print("Attacker mean jump: %.2f" % (atk_mean))
    print("Attacker std jump: %.2f" % (atk_std))
    print("Attacker mean+3*std jump: %.2f" % (atk_detection_bound))               
    member = 1
    honest_max = max([j for j in jump_size[member] if j is not None])
    honest_mean = np.mean([j for j in jump_size[member] if j is not None])
    honest_std = np.std([j for j in jump_size[member] if j is not None])
    honest_detection_bound = honest_mean+3*honest_std
    print("Member[%d] largest jump: %.2f" % (member, honest_max))
    print("Member[%d] mean jump: %.2f" % (member, honest_mean))
    print("Member[%d] std jump: %.2f" % (member, honest_std))
    print("Member[%d] mean+3*std jump: %.2f" % (member, honest_detection_bound))

    atk_max_l = max(loads[0][NUM_MEMBERS])
    atk_mean_l = np.mean(loads[0][NUM_MEMBERS])
    atk_std_l = np.std(loads[0][NUM_MEMBERS])
    atk_detection_bound_l = atk_mean_l+3*atk_std_l
    print("\nAttacker max load: %.2f" % (atk_max_l))
    print("Attacker mean load: %.2f" % (atk_mean_l))
    print("Attacker std load: %.2f" % (atk_std_l))
    print("Attacker mean+3*std load: %.2f" % (atk_detection_bound_l))               
    member = 1
    honest_max_l = max(loads[0][member])
    honest_mean_l = np.mean(loads[0][member])
    honest_std_l = np.std(loads[0][member])
    honest_detection_bound_l = honest_mean_l+3*honest_std_l
    print("Member[%d] max load: %.2f" % (member, honest_max_l))
    print("Member[%d] mean load: %.2f" % (member, honest_mean_l))
    print("Member[%d] std load: %.2f" % (member, honest_std_l))
    print("Member[%d] mean+3*std load: %.2f\n===\n" % (member, honest_detection_bound_l))


    detected_jump_anomalies = {i: 0 for i in range(1, NUM_MEMBERS+1)}
    total_positives_jump = {i: 0.0 for i in range(1, NUM_MEMBERS+1)} # we have some None jumps so need to count this to divide correctly to get rate
    total_negatives_jump = {i: 0.0 for i in range(1, NUM_MEMBERS+1)}
    false_positive_rate_jump = {i: 0.0 for i in range(1, NUM_MEMBERS+1)}
    false_negative_rate_jump = {i: 0.0 for i in range(1, NUM_MEMBERS+1)}
    for mem in range(1, NUM_MEMBERS+1):
        for jump_idx in range(len(jump_size[mem])):
            if jump_size[mem][jump_idx] is None: # the system skips these ones that are not positive, so they are automatically false negatives
                if mem==NUM_MEMBERS:
                    if (jump_idx) in misreported_epochs:
                        total_negatives_jump[mem] += 1.0
                        false_negative_rate_jump[mem] += 1.0
                continue # skip empty ones (just needed to have correct indices for below)
            if mem==NUM_MEMBERS:
                if jump_size[mem][jump_idx] > atk_detection_bound:
                    # print("jump_size length: ", len(jump_size[mem]))
                    # print("ok: ", jump_size[mem][jump_idx])
                    print("Detected attacker 'jump' anomaly between t=(%d, %d) -- jump_size: %.2f" % (jump_idx, jump_idx+1, jump_size[mem][jump_idx]))
                    detected_jump_anomalies[mem] += 1.0
                    total_positives_jump[mem] += 1.0
                    if (jump_idx) not in misreported_epochs: # it would claim a misreport on jump_idx-1 (the previous epoch)
                        false_positive_rate_jump[mem] += 1.0
                else:
                    if (jump_idx) in misreported_epochs: # if the detector didnt call it an anomaly but it was a misreported epoch, bad
                        false_negative_rate_jump[mem] += 1.0
                    total_negatives_jump[mem] += 1.0
            else:
                if jump_size[mem][jump_idx] > honest_detection_bound:
                    # print("Detected mem[%d] anomaly between t=(%d, %d)" % (mem, jump_idx-1, jump_idx))
                    detected_jump_anomalies[mem] += 1.0
                    total_positives_jump[mem] += 1.0
                    if (jump_idx) not in misreported_epochs: # it would claim a misreport on jump_idx-1 (the previous epoch)
                        false_positive_rate_jump[mem] += 1.0
                else:
                    if (jump_idx) in misreported_epochs: # if the detector didnt call it an anomaly but it was a misreported epoch, bad
                        false_negative_rate_jump[mem] += 1.0
                    total_negatives_jump[mem] += 1.0
    
    print("\ndetected jump anomalies:")
    for mem in range(1, NUM_MEMBERS+1):
        print("mem[%d]: %d" % (mem, detected_jump_anomalies[mem]))

    print("JUMP anomalies score against attacker:")
    print("total_negatives_jump[NUM_MEMBERS]: ", total_negatives_jump[NUM_MEMBERS])
    print("false_negative_rate_jump[NUM_MEMBERS]: ", false_negative_rate_jump[NUM_MEMBERS])
    print("false positive: %.2f%%" % (false_positive_rate_jump[NUM_MEMBERS]/total_positives_jump[NUM_MEMBERS]*100.0))
    print("false negative: %.2f%%\n===\n" % (false_negative_rate_jump[NUM_MEMBERS]/total_negatives_jump[NUM_MEMBERS]*100.0))
    # print("false negative: %.2f%%\n===\n" % (false_negative_rate_jump[NUM_MEMBERS]/len(misreported_epochs)*100.0))

        
    # LOAD ANOMALIES
    detected_load_anomalies = {i: 0 for i in range(1, NUM_MEMBERS+1)}
    total_positives_load = {i: 0.0 for i in range(1, NUM_MEMBERS+1)}
    total_negatives_load = {i: 0.0 for i in range(1, NUM_MEMBERS+1)}
    false_positive_rate_load = {i: 0.0 for i in range(1, NUM_MEMBERS+1)}
    false_negative_rate_load = {i: 0.0 for i in range(1, NUM_MEMBERS+1)}
    for mem in range(1, NUM_MEMBERS+1):
        for i in range(1, len(loads[0][mem])):
            if mem==NUM_MEMBERS:
                if loads[0][mem][i] > atk_detection_bound_l:
                    print("Detected attacker 'load' anomaly at t=%d -- load: %.2f" % (i,  loads[0][mem][i]))
                    detected_load_anomalies[mem] += 1.0
                    total_positives_load[mem] += 1 # generally end up being just true positives here from what I see
                    if (i-1) not in misreported_epochs:
                        false_positive_rate_load[mem] += 1.0
                else:
                    if (i-1) in misreported_epochs: # if the detector didnt call it an anomaly but it was a misreported epoch, bad
                        false_negative_rate_load[mem] += 1.0
                    total_negatives_load[mem] += 1
            else:
                if loads[0][mem][i] > honest_detection_bound_l:
                    detected_load_anomalies[mem] += 1.0
                    total_positives_load[mem] += 1
                    if (i-1) not in misreported_epochs:
                        false_positive_rate_load[mem] += 1.0
                else:
                    if (i-1) in misreported_epochs: # if the detector didnt call it an anomaly but it was a misreported epoch, bad
                        false_negative_rate_load[mem] += 1.0
                    total_negatives_load[mem] += 1

    print("\ndetected load anomalies:")
    for mem in range(1, NUM_MEMBERS+1):
        print("mem[%d]: %d" % (mem, detected_load_anomalies[mem]))

    print("LOAD anomalies score against attacker:")
    print("total_negatives_load[NUM_MEMBERS]: ", total_negatives_load[NUM_MEMBERS])
    print("false_negative_rate_load[NUM_MEMBERS]: ", false_negative_rate_load[NUM_MEMBERS])
    print("false positive: %.2f%%" % (false_positive_rate_load[NUM_MEMBERS]/total_positives_load[NUM_MEMBERS]*100.0))
    print("false negative: %.2f%%" % (false_negative_rate_load[NUM_MEMBERS]/total_negatives_load[NUM_MEMBERS]*100.0))
    # print("false negative: %.2f%%" % (false_negative_rate_load[NUM_MEMBERS]/len(misreported_epochs)*100.0))
    # meh the misreported epochs from the file might be alittle off. These should be the correct epochs. We just know that it only detected a few out of many anomalies and so the false negative rate was extremely high


"""
NOTE: averages over all experiments (as opposed to just using index 0--experiment 1)
"""
def run_stat_tests(member_loads):
    TESTING_WINDOW_BEGIN_ATTACKER = 0
    TESTING_WINDOW_END_ATTACKER = 1500
    # TESTING_WINDOW_BEGIN_IDS = 0
    # TESTING_WINDOW_END_IDS = 187

    # loads_list = list(member_loads[exp_idx][i] for i in range(1, NUM_MEMBERS+1))
    # print("member_loads[exp_idx]: ", loads_list)
    print("=== median test ===")
    tester = NUM_MEMBERS
    res = [{i: tuple(median_test(member_loads[exp_idx][i][TESTING_WINDOW_BEGIN_ATTACKER:TESTING_WINDOW_END_ATTACKER], member_loads[exp_idx][tester][TESTING_WINDOW_BEGIN_ATTACKER:TESTING_WINDOW_END_ATTACKER])) for i in range(
        1, NUM_MEMBERS+1)} for exp_idx in range(num_experiments)]  # sample sizes can be diff, maybe just aggregate all others
    print("Tests for member%d:" % tester)
    for exp_idx in range(num_experiments):
        print("=== Experiment [%d]: " % exp_idx)
        for i in range(1, NUM_MEMBERS+1):
            print("Test against member%d: " %
                i, "\nstat: ", res[exp_idx][i][0], "\npval: ", res[exp_idx][i][1])
    # print("grand med: ", med)
    # print("tbl: ", tbl)
    # print("pval: ", p)

    print("=== KS test ===")
    tester = NUM_MEMBERS
    res = [{i: tuple(ks_2samp(member_loads[exp_idx][i][TESTING_WINDOW_BEGIN_ATTACKER:TESTING_WINDOW_END_ATTACKER], member_loads[exp_idx][tester][TESTING_WINDOW_BEGIN_ATTACKER:TESTING_WINDOW_END_ATTACKER])) for i in range(
        1, NUM_MEMBERS+1)} for exp_idx in range(num_experiments)]  # sample sizes can be diff, maybe just aggregate all others
    # res = {i:tuple(ks_2samp(member_loads[exp_idx][i], member_loads[exp_idx][tester], alternative='less')) for i in range(1, NUM_MEMBERS+1)}
    print("Tests for member%d:" % tester)
    for exp_idx in range(num_experiments):
        print("=== Experiment [%d]: " % exp_idx)
        for i in range(1, NUM_MEMBERS+1):
            print("Test against member%d:\nstat: " %
                i, res[exp_idx][i][0], "\npval: ", res[exp_idx][i][1])
    # print("stat: ", stat)
    # print("pvals: ", p)


    ### plot the pval changes
    window_start_time_first = 0
    window_start_time_last = 1600

    window_sizes = [60, 300] # 1 and 5 min windows
    ks_pvals = dict()
    median_pvals = dict()

    # using controller_view loads ***
    f1_ks = open("load_data/pvals-ks%d.csv" % 1, 'w')
    f1_ks_writer = csv.writer(f1_ks)
    f1_med = open("load_data/pvals-med%d.csv" % 1, 'w')
    f1_med_writer = csv.writer(f1_med)    
    for window_size in window_sizes:
        ks_pvals[window_size] = list()
        median_pvals[window_size] = list()
        for window_start_time in range(window_start_time_first, window_start_time_last):
            # take average pval from testing against all members
            ks_res = [{i: tuple(ks_2samp(member_loads[exp_idx][i][window_start_time:window_start_time+window_size], member_loads[exp_idx][10][window_start_time:window_start_time+window_size])) for i in range(1, NUM_MEMBERS+1)} for exp_idx in range(num_experiments)]
            ks_avg_pval = np.mean([ks_res[exp_idx][i][1] for i in range(1, NUM_MEMBERS) for exp_idx in range(num_experiments)]) # dont include the attacker in avg; take average across all members and experiments
            # print("ks_avg_pval: ", ks_avg_pval)
            ks_pvals[window_size].append(ks_avg_pval)
            # f1_ks.write(str(ks_avg_pval)+",,")
            f1_ks_writer.writerow([ks_avg_pval])
            # print("ks_avg_pval: ", ks_avg_pval)

            median_res = [{i: tuple(median_test(member_loads[exp_idx][i][window_start_time:window_start_time+window_size], member_loads[exp_idx][10][window_start_time:window_start_time+window_size])) for i in range(1, NUM_MEMBERS+1)} for exp_idx in range(num_experiments)]
            median_avg_pval = np.mean([median_res[exp_idx][i][1] for i in range(1, NUM_MEMBERS) for exp_idx in range(num_experiments)]) # dont include the attacker in avg
            f1_med_writer.writerow([median_avg_pval])
            # print("median_avg_pval: ", median_avg_pval)
            median_pvals[window_size].append(median_avg_pval)
    f1_ks.close()


    # plot ks
    plt.figure()
    for window_size in window_sizes:
        plt.plot([window_start_time for window_start_time in range(window_start_time_first, window_start_time_last)][300:window_start_time_last], ks_pvals[window_size][300:window_start_time_last], marker='x', markevery=100, markersize=7, label="ks, window_size=%d" % (window_size))
        # plt.plot([window_start_time for window_start_time in range(window_start_time_first, window_start_time_last)][300:window_start_time_last], median_pvals[window_size][300:window_start_time_last], linestyle=':', marker='o', markevery=[i*100 for i in range(3, 17)], label="median, window_size=%d" % (window_size))
    plt.xlabel('Window start time (s)')
    plt.ylabel('p-value')
    plt.grid(True, color='grey', linestyle=':', linewidth=0.25, alpha=0.25)
    plt.legend(loc='best')
    plt.savefig('detect-ks.pdf')


    # plot median
    plt.figure()
    for window_size in window_sizes:
        # plt.plot([window_start_time for window_start_time in range(window_start_time_first, window_start_time_last)][300:window_start_time_last], ks_pvals[window_size][300:window_start_time_last], linestyle=':', marker='x', markevery=[i*100 for i in range(3, 17)], label="ks, window_size=%d" % (window_size))
        plt.plot([window_start_time for window_start_time in range(window_start_time_first, window_start_time_last)][300:window_start_time_last], median_pvals[window_size][300:window_start_time_last], marker='x', markevery=100, markersize=7, label="median, window_size=%d" % (window_size))
    plt.xlabel('Window start time (s)')
    plt.ylabel('p-value')
    plt.grid(True, color='grey', linestyle=':', linewidth=0.25, alpha=0.25)
    plt.legend(loc='best')
    plt.savefig('detect-med.pdf')


"""
NOTE: just plots the first experiment (index 0 in member loads)
"""
def graph(_member_loads):
    # plot time series
    gr = plt.GridSpec(14, 20, wspace=0.4, hspace=0.3)

    # plt.rcParams["figure.figsize"] = (5,3)
    # plt.figure(figsize=(1,1))
    font_sz = 7

    plt.rcParams["font.family"] = "Times New Roman"
    plt.subplot(gr[:6, :])
    # plt.subplot(gr[:, :])
    for i in range(1, NUM_MEMBERS+1):
        # for i in range(5, 6):
        plt.plot([j for j in range(len(_member_loads[0][i]))], _member_loads[0][i],
                 linestyle='-', linewidth=0.2, label='member[%d]' % i)
        # plt.plot([j for j in range(len(_member_loads[0][i]))], _member_loads[0][i],
        #          linestyle='-', linewidth=0.5, label='member[%d]' % i)

    plt.xlabel('Time (s)', fontsize=font_sz)
    plt.ylabel('Load (%s)'%("Kb" if POLICY==LL else "flows"), fontsize=font_sz)
    # plt.ylabel('Load (flows)', fontsize=font_sz)
    plt.grid(True, color='grey', linestyle=':', linewidth=0.25, alpha=0.25)
    plt.title(r"Member load over time (switch view for [10]) (%s flows)" % traffic_type, fontsize=font_sz)
    # plt.legend(fontsize=font_sz, loc='upper left')
    # plt.ylim(0, 1000)
    plt.xticks(fontsize=font_sz)
    # plt.yticks([100, 200, 300]+[i*2000 for i in range(8)], [100, 200, 300]+[i*2000 for i in range(8)], fontsize=font_sz)
    plt.yticks(fontsize=font_sz)

    # plot cdfs
    plt.subplot(gr[8:, :])
    for i in range(1, NUM_MEMBERS+1): # plot loads during attack
        sorted_loads = sorted(
            _member_loads[0][i][ATK_WINDOW_BEGIN:ATK_WINDOW_END])
        cdf_load = calc_cdf_fast(sorted_loads)
        plt.plot(sorted_loads, cdf_load, linewidth=0.5)
    for i in range(1, NUM_MEMBERS+1): # plot loads before attack
        sorted_loads = sorted(_member_loads[0][i][600:900])
        cdf_load = calc_cdf_fast(sorted_loads)
        plt.plot(sorted_loads, cdf_load, linewidth=0.75, label='Member[%d]' % i)
    
    # add another line for the adversary line _before_ attack to show what they are actually approximating and how the other members shift from this
    # sorted_loads = sorted(_member_loads[0][10][600:900])
    # cdf_load = calc_cdf_fast(sorted_loads)
    # plt.plot(sorted_loads, cdf_load, linewidth=0.5, color='red', label='attacker approximation')    
    # plt.xscale("log")
    # plt.xlim(10e-3, 10e2)
    # plt.xlim(-10, 200)
    # plt.xlim(-10, 5000)
    plt.ylim(0, 1)
    plt.xlabel('Load (%s)'%("Kb" if POLICY==LL else "flows"), fontsize=font_sz)
    # plt.xlabel('Load (flows)', fontsize=font_sz)
    plt.ylabel('Cumulative Probability', fontsize=font_sz)
    plt.grid(True, color='grey', linestyle=':', linewidth=0.5, alpha=0.25)
    # plt.title(r"$\bf{Load~distribution~over~time}$ (time %d-%d)" %
    #           (ATK_WINDOW_BEGIN, ATK_WINDOW_END), fontsize=font_sz)
    plt.title("Load distribution over time (switch view for [10]) (time %d-%d)" % (ATK_WINDOW_BEGIN, ATK_WINDOW_END), fontsize=font_sz)
    plt.legend(fontsize=font_sz, loc='best')
    plt.xticks(fontsize=font_sz)
    plt.yticks(fontsize=font_sz)

    # display plots
    plt.savefig('member_loads.pdf')
    # plt.savefig('loadspikes.pgf')
    # plt.savefig('loadsteady.pgf')
    # plt.show()


    # just plot load over time
    plt.figure()
    for i in range(1, NUM_MEMBERS+1):
        # for i in range(5, 6):
        plt.plot([j for j in range(len(_member_loads[0][i]))], _member_loads[0][i],
                 linestyle='-', linewidth=0.2, label='member[%d]' % i)
        # plt.plot([j for j in range(len(_member_loads[0][i]))], _member_loads[0][i],
        #          linestyle='-', linewidth=0.5, label='member[%d]' % i)

    plt.xlabel('Time (s)', fontsize=font_sz)
    plt.ylabel('Load (%s)'%("Kb" if POLICY==LL else "flows"), fontsize=font_sz)
    # plt.ylabel('Load (flows)', fontsize=font_sz)
    plt.grid(True, color='grey', linestyle=':', linewidth=0.25, alpha=0.25)
    plt.title(r"Member load over time (%s flows)" % traffic_type, fontsize=font_sz)
    # plt.legend(fontsize=font_sz, loc='upper left')
    # plt.ylim(0, 1000)
    plt.xticks(fontsize=font_sz)
    plt.yticks(fontsize=font_sz)
    plt.savefig('loads.pdf')

    # just plot the cumulative probability
    loaddist_fontsz = 15
    plt.figure()
    for i in range(1, NUM_MEMBERS+1):
        sorted_loads = sorted(_member_loads[0][i][200:800])
        cdf_load = calc_cdf_fast(sorted_loads)
        plt.plot(sorted_loads, cdf_load, linewidth=0.75, label='Member[%d]' % i)
        # plt.plot(sorted_loads, cdf_load, linewidth=0.5, marker = next(marker), markevery=[i*100 for i in range(10)], label='Member[%d]' % i)
    plt.ylim(0, 1)
    plt.xlabel('Load (%s)'%("Kb" if POLICY==LL else "flows"), fontsize=loaddist_fontsz)
    plt.ylabel('Cumulative Probability', fontsize=loaddist_fontsz)
    plt.grid(True, color='grey', linestyle=':', linewidth=0.25, alpha=0.25)
    # plt.title("Load distribution over time", fontsize=loaddist_fontsz)
    plt.xticks([i*500 for i in range(7)], [i*500 for i in range(7)], fontsize=loaddist_fontsz)
    plt.yticks(fontsize=loaddist_fontsz)

    # display plots
    plt.legend(fontsize=15, loc='lower right', ncol=2)
    # plt.xscale("log")
    plt.savefig('loaddist.pdf')

def calc_cdf_fast(arr):
    cdf = []
    for val in arr:
        count = 0
        for other_val in arr:
            if other_val <= val:
                count += 1
        cdf.append(float(count*1.0/len(arr)))
    return cdf


"""
NOTE: just plots the first experiment (index 0 in member loads)
"""
def plot_shift(_member_loads):
    # check distribution shift
    checkshift_fontsz = 15
    plt.figure()
    # p = 0.01
    ps = [0.01*i for i in range(98)]
    shifts = list()
    for p in ps:
        sorted_atker_loads_before_atk = sorted(_member_loads[0][10][600:900])
        pth_load_before_atk = sorted_atker_loads_before_atk[int(p*len(sorted_atker_loads_before_atk))] # what atker keeps estimating
        sorted_normal_mem_loads_during_atk = sorted(_member_loads[0][1][ATK_WINDOW_BEGIN:ATK_WINDOW_END]) # member 1
        stopped = 0.0
        for i in range(len(sorted_normal_mem_loads_during_atk)):
            if sorted_normal_mem_loads_during_atk[i] >= pth_load_before_atk:
                stopped = float(i)
                break
        # print("attacker (before atk): p=%.2f, load=%.2f" % (p, pth_load_before_atk)) # attacker misreports here thinking this threshold is pth load
        # print("member1 (during atk): i=%.2f, load=%.2f" % (stopped/len(sorted_normal_mem_loads_during_atk), sorted_normal_mem_loads_during_atk[int(stopped)])) # but for normal members that load should be a higher percentile during the attack
        # print("k: ", stopped/len(sorted_normal_mem_loads_during_atk))
        # shifts.append(stopped/len(sorted_normal_mem_loads_during_atk)-p)
        shifts.append(stopped/len(sorted_normal_mem_loads_during_atk))
   
    plt.plot(ps, shifts, linewidth=0.75)
    
    # display plots
    # plt.ylim(0, 1)
    plt.xlabel(r"Percentile ($p$)", fontsize=checkshift_fontsz)
    # plt.ylabel('Perceived percentile', fontsize=checkshift_fontsz)
    plt.ylabel('Perceived percentile', fontsize=checkshift_fontsz)
    plt.grid(True, color='grey', linestyle=':', linewidth=0.25, alpha=0.25)
    plt.xticks(fontsize=checkshift_fontsz)
    plt.yticks(fontsize=checkshift_fontsz)
    # plt.legend(fontsize=15, loc='lower right', ncol=2)
    plt.title('short/ll p=0.1', fontsize=14)
    plt.savefig('shift.pdf') # NOTE: need to turn controller_view off before doing this bc we want switch view of shift

    # plt.xlabel('Pool member number', fontsize=14)
    # plt.xticks(range(num_pool_members+1), tmp, fontsize=7)
    # plt.ylabel('Number of requests', fontsize=7)
    # plt.yticks(range(0, max(ylabels_arr)+10000+1, 10000), [str(int(lab/1e3))+"K" if lab%20e3==0 else '' for lab in ylabels_arr], fontsize=7)
    # plt.legend(fontsize=14, loc='upper left')
    # plt.grid(True, color='grey', linestyle=':', alpha=0.5)
    # plt.title(r"$\bf{Average~load}$", fontsize=14)


def get_qtp(utilization):
    service_rate = 100e6
    avg_waiting_time_in_system_per_bit = (
        1.0/service_rate) + (utilization / (2*service_rate*(1-utilization)))
    # avg_waiting_time_in_system_per_pkt = avg_waiting_time_in_system_per_bit * 8 * 1500
    # return avg_waiting_time_in_system_per_pkt
    return 1.0/avg_waiting_time_in_system_per_bit


def get_q_delay_per_ping(utilization):
    service_rate = 100e6
    avg_waiting_time_in_system_per_bit = (
        1.0/service_rate) + (utilization / (2*service_rate*(1-utilization)))
    # avg_waiting_time_in_system_per_pkt = avg_waiting_time_in_system_per_bit * 8 * 1500
    # return avg_waiting_time_in_system_per_pkt
    return avg_waiting_time_in_system_per_bit*98*8


def graph_tp_vs_goal():
    # experimental network TP
    font_sz = 15
    plt.rcParams["font.family"] = "Times New Roman"

    # tps3 = [100, 93.8, 84.8, 75.3, 63.5, 52.0, 42.6, 29.0, 10.8, 2.7, 0.0]

    # TP loss plot
    # goals1 = [0.1*u for u in range(1, 10)]
    # base_delay = 0.042 # 10% utilization (normal conditions)
    # delays = [0.0, 0.045, 0.047, 0.049, 0.049, 0.049, 0.049, 0.049, 0.049]
    # tp_losses = [0] + [1-(base_delay/delays[i]) for i in range(1, len(delays))]
    # plt.plot(goals1, tp_losses, linestyle='--', marker='^', linewidth=0.5, label='Experimental results', color='blue')

    # normal TP plot
    # goals1 = [0.1*u for u in range(1, 10)]
    goals1 = [0.1*u-.005 for u in range(0, 11)]
    tps = [93.9, 93.9, 83.9, 74.4, 60.5, 50.4, 40.9,
           23.1, 6.27, 2.7, 0]  # got 100 at 0 now
    plt.plot(goals1, tps, linestyle='--', marker='^', linewidth=0.5,
             label='Experimental results', color='blue')

    # queueing model TP

    # TP loss plot
    # goals2 = [0.1*u for u in range(1, 10)]
    # tp_losses2 = list()
    # for util in goals2:
    #     tp_losses2.append(1-(get_q_delay_per_ping(0.1)/get_q_delay_per_ping(util)))
    # plt.plot(goals2, tp_losses2, linestyle='--', marker='x', linewidth=0.5, label='Queuing model results', color='red')

    # normal TP plot
    goals2 = [0.01*u for u in range(0, 100)]
    tps2 = [get_qtp(util)/1e6 for util in goals2]+[0]
    plt.plot(goals2+[1], tps2, linestyle='--', marker='x', markevery=10, linewidth=0.5,
             label='Queuing model', color='red')

    avg_err = np.mean([abs(tps2[i*10]-tps[i]) for i in range(len(tps))])
    print("Avg err: %.2f%%" % (avg_err*1e6/100e6*100))

    # plt.title(r"$\bf{Throughput~vs.~Goal~load~(Long~flows)}$", fontsize=font_sz)
    # plt.title(
    #     r"Throughput vs. target utilization (Long flows/Least-loaded)", fontsize=font_sz)
    plt.xlabel(r"Target utilization ($\rho_{tar}$)", fontsize=font_sz)
    plt.ylabel('Throughput (Mb/s)', fontsize=font_sz)
    # plt.ylabel('Throughput loss (%)', fontsize=font_sz)
    plt.grid(True, color='grey', linestyle=':', alpha=0.5)
    plt.xticks(fontsize=font_sz)
    plt.yticks(fontsize=font_sz)
    plt.legend(fontsize=font_sz, loc='upper right')
    plt.savefig('qtp-ll.pgf')
    plt.show()

    # 1-(1/((1/100e6)+(0.2/(2*100e6*(1-0.2)))))/(1/((1/100e6)+(0.1/(2*100e6*(1-0.1)))))


def graph_tp_vs_goal_lc():
    # experimental network TP
    font_sz = 15
    plt.rcParams["font.family"] = "Times New Roman"

    # TP loss plot
    # goals1 = [0.1*u for u in range(1, 10)]
    # base_delay = 0.042 # 10% utilization (normal conditions)
    # delays = [0.0, 0.045, 0.047, 0.049, 0.049, 0.049, 0.049, 0.049, 0.049]
    # tp_losses = [0] + [1-(base_delay/delays[i]) for i in range(1, len(delays))]
    # plt.plot(goals1, tp_losses, linestyle='--', marker='^', linewidth=0.5, label='Experimental results', color='blue')

    # normal TP plot
    # goals1 = [0.1*u for u in range(1, 10)]
    goals1 = [0.1*u-.005 for u in range(0, 11)]
    tps = [93.9, 93.8, 84.8, 75.3, 63.5, 52.0, 42.6, 29.0, 10.8, 2.7, 0.0]
    plt.plot(goals1, tps, linestyle='--', marker='^', linewidth=0.5,
             label='Experimental results', color='blue')

    # queueing model TP

    # TP loss plot
    # goals2 = [0.1*u for u in range(1, 10)]
    # tp_losses2 = list()
    # for util in goals2:
    #     tp_losses2.append(1-(get_q_delay_per_ping(0.1)/get_q_delay_per_ping(util)))
    # plt.plot(goals2, tp_losses2, linestyle='--', marker='x', linewidth=0.5, label='Queuing model results', color='red')

    # normal TP plot
    goals2 = [0.01*u for u in range(0, 100)]
    tps2 = [get_qtp(util)/1e6 for util in goals2]+[0]
    plt.plot(goals2+[1], tps2, linestyle='--', marker='x', markevery=10, linewidth=0.5,
             label='Queuing model', color='red')

    avg_err = np.mean([abs(tps2[i*10]-tps[i]) for i in range(len(tps))])
    print("Avg err: %.2f%%" % (avg_err*1e6/100e6*100))

    # plt.title(r"$\bf{Throughput~vs.~Goal~load~(Long~flows)}$", fontsize=font_sz)
    # plt.title(
    #     r"Throughput vs. target utilization (Long flows/Least-connections)", fontsize=font_sz)
    plt.xlabel(r"Target utilization ($\rho_{tar}$)", fontsize=font_sz)
    plt.ylabel('Throughput (Mb/s)', fontsize=font_sz)
    # plt.ylabel('Throughput loss (%)', fontsize=font_sz)
    plt.grid(True, color='grey', linestyle=':', alpha=0.5)
    plt.xticks(fontsize=font_sz)
    plt.yticks(fontsize=font_sz)
    plt.legend(fontsize=font_sz, loc='upper right')
    plt.savefig('qtp-lc.pgf')
    plt.show()


def get_m_from_model(util, alg):
    service_rate = 100e6
    W = 300
    tlong = 10.5
    avg_pkt_len = 1500
    # arr_rate = 100*avg_pkt_len*8
    arr_rate = 900  # NOTE: (important): note that here the arrival rate is of ALL flows (active or new) which is about 1000, not 100; it is the total since we want to measure to average load in the network for each member
    # alg = 'lc'
    # alg = 'll'
    lbar = None
    if alg == 'lc':
        lbar = arr_rate*avg_pkt_len*8*tlong/NUM_MEMBERS
    elif alg == 'll':
        # lbar = 8*arr_rate*tlong*avg_pkt_len/NUM_MEMBERS
        lbar = 8*arr_rate*avg_pkt_len*tlong/NUM_MEMBERS
    else:
        print("bad")
        exit(1)

    # print('lbar: ', lbar)
    M = ((util*service_rate)*W)/(tlong*lbar)
    return M


def get_util_from_m(m, alg):
    service_rate = 100e6
    W = 300
    tlong = 10.5
    avg_pkt_len = 1500
    # arr_rate = 100*avg_pkt_len*8
    arr_rate = 900  # NOTE: (important): note that here the arrival rate is of ALL flows (active or new) which is about 1000, not 100; it is the total since we want to measure to average load in the network for each member
    # alg = 'lc'
    # alg = 'll'
    lbar = None
    if alg == 'lc':
        lbar = arr_rate*avg_pkt_len*8*tlong/NUM_MEMBERS
    elif alg == 'll':
        # lbar = 8*arr_rate*tlong*avg_pkt_len/NUM_MEMBERS
        lbar = 8*arr_rate*avg_pkt_len*tlong/NUM_MEMBERS
    else:
        print("bad")
        exit(1)

    # print('lbar: ', lbar)
    # M = ((util*service_rate)*W)/(tlong*lbar)
    util = m*(tlong*lbar)/(service_rate*W)
    return util


def graph_tp_vs_mis():
    # only do these plots for long flows
    font_sz = 15
    plt.rcParams["font.family"] = "Times New Roman"

    # experimental network TP
    # goals1 = [0.1*u-.005 for u in range(1, 10)]
    # m1 = [get_m_from_model(util) for util in goals1]
    # mis_percs = [0, .1, .198, .247, .397, .5, .6, .7, .8, .9]
    mis_percs_newtest = [0, .097, .198, .247, .35, .483, .55, .677, .778, .867]
    m1 = np.array(mis_percs_newtest) * \
        300  # actual number of times misreported
    tps = [93.9, 93.9, 83.9, 74.4, 60.5, 50.4, 40.9, 23.1, 6.27, 2.7]
    # print("m1: ", m1)
    # print("tps: ", tps)
    plt.plot(m1, tps, linestyle='--', marker='^', linewidth=0.5,
             label='Experimental results', color='blue')

    # queueing model TP vs # misreports
    # goals2 = [0.01*u-.005 for u in range(0, 100)]
    # goals2_short = [0.1*u for u in range(0, 10)]
    goals2_short = [get_util_from_m(m1[i], 'll') for i in range(len(m1))]
    # print(goals2_short)
    # goals2_short[len(m1)-1] = 0.99 # was higher than 1 but cant be
    # goals2 = [0.001*u for u in range(0, 1000)]
    m2 = [get_m_from_model(util, 'll') for util in goals2_short]
    tps2 = [get_qtp(util)/1e6 for util in goals2_short]
    # goals2_short for this element was higher than 1 but cant be; the TP was also negative
    tps2[len(m1)-1] = 0
    # TODO: here; wrong, this is mis rate not util...
    tps2_short = [get_qtp(util)/1e6 for util in goals2_short]
    # print("m2: ", m2)
    # print("tps2: ", tps2)

    errs = [0]*len(tps2_short)
    for i in range(len(tps2_short)):
        # errs[i] = tps2_short[i] - tps[i]
        errs[i] = abs(tps2_short[i] - tps[i])

    plt.plot(m2, tps2, linestyle='--', marker='x', markevery=1, linewidth=0.5,
             label='Queuing model', color='red')

    # errs = [tps2[int(get_util_from_m(mis_percs[i]*300)*100)]-tps[i] for i in range(len(tps))]
    # errs = [tps2[i*100]-tps[i] for i in range(len(tps))]
    # errs = [tps2[int(mis_percs[i]*100*10)]-tps[i] for i in range(len(tps))]
    # print("errs: ", errs)
    avg_err = np.mean(errs)
    print("Avg err: %.2f%%" % (avg_err*1e6/100e6*100))

    # plt.title(r"$\bf{Throughput~vs.~\#~misreports~(Long~flows)}$", fontsize=font_sz)
    # plt.title(
    #     r"Throughput vs. number of misreports (Long flows/Least-loaded)", fontsize=font_sz)
    plt.xlabel('Number of misreports ($M$)', fontsize=font_sz)
    plt.ylabel('Throughput (Mb/s)', fontsize=font_sz)
    plt.grid(True, color='grey', linestyle=':', alpha=0.5)
    plt.xticks(fontsize=font_sz)
    plt.yticks(fontsize=font_sz)
    plt.legend(fontsize=font_sz, loc='upper right')
    plt.savefig('tpvsnummis-ll.pgf')
    plt.show()


def graph_tp_vs_mis_lc():
    # only do these plots for long flows
    font_sz = 15
    plt.rcParams["font.family"] = "Times New Roman"

    # experimental network TP
    # goals1 = [0.1*u-.005 for u in range(1, 10)]
    # m1 = [get_m_from_model(util) for util in goals1]
    # mis_percs = [0, .1, .198, .236, .397, .5, .6, .7, .8, .9]
    mis_percs_newtest = [0, .097, .193, .29, .38, .483, .597, .673, .773, .898]
    m1 = np.array(mis_percs_newtest) * \
        300  # actual number of times misreported
    tps = [93.8, 93.8, 84.8, 75.3, 63.5, 52.0, 42.6, 29.0, 10.8, 2.7]
    # print("m1: ", m1)
    # print("tps: ", tps)
    plt.plot(m1, tps, linestyle='--', marker='^', linewidth=0.5,
             label='Experimental results', color='blue')

    # queueing model TP vs # misreports
    # goals2 = [0.01*u-.005 for u in range(0, 100)]
    # goals2_short = [0.1*u for u in range(0, 10)]
    goals2_short = [get_util_from_m(m1[i], 'lc') for i in range(len(m1))]
    # print(goals2_short)
    # goals2_short[len(m1)-1] = 0.99 # was higher than 1 but cant be
    # goals2 = [0.001*u for u in range(0, 1000)]
    m2 = [get_m_from_model(util, 'lc') for util in goals2_short]
    tps2 = [get_qtp(util)/1e6 for util in goals2_short]
    # goals2_short for this element was higher than 1 but cant be; the TP was also negative
    tps2[len(m1)-1] = 0
    # TODO: here; wrong, this is mis rate not util...
    tps2_short = [get_qtp(util)/1e6 for util in goals2_short]
    # print("m2: ", m2)
    # print("tps2: ", tps2)

    errs = [0]*len(tps2_short)
    for i in range(len(tps2_short)):
        # errs[i] = tps2_short[i] - tps[i]
        errs[i] = abs(tps2_short[i] - tps[i])

    plt.plot(m2, tps2, linestyle='--', marker='x', markevery=1, linewidth=0.5,
             label='Queuing model', color='red')

    # errs = [tps2[int(get_util_from_m(mis_percs[i]*300)*100)]-tps[i] for i in range(len(tps))]
    # errs = [tps2[i*100]-tps[i] for i in range(len(tps))]
    # errs = [tps2[int(mis_percs[i]*100*10)]-tps[i] for i in range(len(tps))]
    # print("errs: ", errs)
    avg_err = np.mean(errs)
    print("Avg err: %.2f%%" % (avg_err*1e6/100e6*100))

    # plt.title(r"$\bf{Throughput~vs.~\#~misreports~(Long~flows)}$", fontsize=font_sz)
    # plt.title(
    #     r"Throughput vs. number of misreports (Long flows/Least-connections)", fontsize=font_sz)
    plt.xlabel('Number of misreports ($M$)', fontsize=font_sz)
    plt.ylabel('Throughput (Mb/s)', fontsize=font_sz)
    plt.grid(True, color='grey', linestyle=':', alpha=0.5)
    plt.xticks(fontsize=font_sz)
    plt.yticks(fontsize=font_sz)
    plt.legend(fontsize=font_sz, loc='upper right')
    plt.savefig('tpvsnummis-lc.pgf')
    plt.show()


# def graph_nummis_vs_goal():
#     # only do these plots for long flows

#     # experimental network #mis vs goal
#     # goals1 = [0.1*u for u in range(1, 10)]
#     goals1 = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
#     mis1 = [0, 30, 60, 90, 120, 150, 180, 210, 240]
#     plt.plot(goals1, mis1, linestyle='--', marker='^', linewidth=0.5,
#              label='Experimental results', color='blue')

#     # queueing model # misreports vs goal
#     goals2 = [0.01*u for u in range(1, 100)]
#     m2 = [get_m_from_model(util, 'll') for util in goals2]
#     plt.plot(goals2, m2, linestyle='--', marker='x', markevery=10,
#              linewidth=0.5, label='Queuing model', color='red')

#     plt.title(r"$\bf{\#~misreports~vs.~utilization~(Long~flows)}$", fontsize=8)
#     plt.xlabel('Goal utilization', fontsize=8)
#     plt.ylabel('Number of misreports', fontsize=8)
#     plt.grid(True, color='grey', linestyle=':', alpha=0.5)
#     plt.xticks(fontsize=8)
#     plt.yticks(fontsize=8)
#     plt.legend(fontsize=8, loc='upper left')
#     plt.show()


if __name__ == '__main__':
    if sys.argv[2] == '1':
        plt.close()
        plt.clf()
        plt.cla()
        NUM_MEMBERS = int(sys.argv[1])
        parse()
    elif sys.argv[2] == '2':
        graph_tp_vs_goal()
    elif sys.argv[2] == '3':
        NUM_MEMBERS = int(sys.argv[1])
        graph_tp_vs_mis()
    elif sys.argv[2] == '4':
        graph_tp_vs_goal_lc()
    elif sys.argv[2] == '5':
        NUM_MEMBERS = int(sys.argv[1])
        graph_tp_vs_mis_lc()
    else:
        print("Invalid arg")
