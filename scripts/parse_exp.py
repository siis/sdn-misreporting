#!/usr/bin/env python3.7
#
# File: parse_exp.py
#
# Description   : parse experimental results
# Created by    : Quinn Burke (qkb5007@psu.edu)
# Date          : November 2019
# Last Modified : November 2019


### Imports ###
import matplotlib.pyplot as plt
import numpy as np
import sys

### Globals ###
NUM_MEMBERS = None
ATK_WINDOW_BEGIN = 203
ATK_WINDOW_END = 403

### Functions ###


def parse():
    member_loads = {i: list() for i in range(1, NUM_MEMBERS+1)
                    }  # loads over time (in BPS)!!!
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
                                ' bps')[0], 16)/1000.0  # Kb/s (using bits now)
                            # print("\nline: %s" %lines[i][:-1])
                            # print("test: ", lines[i].strip().strip('\n').split('): ')[1].split(' bps')[0])
                            # print("member: %s, load: %d" % (member, load))
                            if int(member) in member_loads.keys():
                                member_loads[int(member)].append(load)
                            i += 1
                        else:
                            break
        finally:
            f.close()

    print("Overall: ")
    member_avgs = dict()
    for member in member_loads.keys():
        # print("member[%d] loads: " % key, member_loads[key])
        member_avgs[member] = np.mean(member_loads[member])
        # print("member[%s] average: %.3f KB" % (member, member_avgs[member]))
        print("member[%s] average: %.3f Kb" % (member, member_avgs[member]))
    overall_avg = np.mean([member_avgs[member]
                           for member in member_avgs.keys()])
    # print("overall average: %.3f KB" % (overall_avg))
    print("overall average: %.3f Kb" % (overall_avg))

    print("==============")

    print("During atk: ")
    member_avgs_during_atk = dict()
    for member in member_loads.keys():
        # print("member[%d] loads: " % key, member_loads[key])
        member_avgs_during_atk[member] = np.mean(
            member_loads[member][ATK_WINDOW_BEGIN:ATK_WINDOW_END])
        # print("member[%s] average_during_atk: %.3f KB" % (member, member_avgs_during_atk[member]))
        print("member[%s] average_during_atk: %.3f Kb" %
              (member, member_avgs_during_atk[member]))
    overall_avg_during_atk = np.mean(
        [member_avgs_during_atk[member] for member in member_avgs_during_atk.keys()])
    # print("overall average_during_atk: %.3f KB" % (overall_avg_during_atk))
    print("overall average_during_atk: %.3f Kb" % (overall_avg_during_atk))

    return member_loads


def calc_cdf_fast(arr):
    cdf = []
    for val in arr:
        count = 0
        for other_val in arr:
            if other_val <= val:
                count += 1
        cdf.append(float(count*1.0/len(arr)))
    return cdf


def graph(_member_loads):
    # plot time series
    gr = plt.GridSpec(14, 20, wspace=0.4, hspace=0.3)

    # plt.rcParams["figure.figsize"] = (5,3)
    # plt.figure(figsize=(1,1))
    font_sz = 12


    # plt.subplot(gr[:6, :])
    # plt.subplot(gr[:, :])
    for i in range(1, NUM_MEMBERS+1):
    # for i in range(5, 6):
        plt.plot([j for j in range(len(_member_loads[i]))], _member_loads[i],
                 linestyle='-', linewidth=0.5, label='member[%d]' % i)
        # plt.plot([j for j in range(len(_member_loads[i]))], _member_loads[i],
        #          linestyle='-', linewidth=0.5, label='member[%d]' % i)

    plt.xlabel('Time (s)', fontsize=font_sz)
    # plt.ylabel('Load (KB)', fontsize=font_sz)
    plt.ylabel('Load (Kb)', fontsize=font_sz)
    plt.grid(True, color='grey', linestyle=':', alpha=0.5)
    plt.title(r"Member load over time (Short flows)", fontsize=font_sz)
    plt.legend(fontsize=font_sz, loc='upper left')
    # plt.ylim(0, 1000)
    plt.xticks(fontsize=font_sz)
    plt.yticks(fontsize=font_sz)

    # plot cdfs
    # plt.subplot(gr[8:, :])
    # for i in range(1, NUM_MEMBERS+1):
    #     sorted_loads = sorted(_member_loads[i])
    #     cdf_load = calc_cdf_fast(sorted_loads)
    #     plt.plot(sorted_loads, cdf_load, linewidth=0.5)
    # # plt.xscale("log")
    # # plt.xlim(10e-3, 10e2)
    # # plt.xlim(-10, 200)
    # plt.xlim(-10, 5000)
    # # plt.xlabel('Load (KB)', fontsize=8)
    # plt.xlabel('Load (Kb)', fontsize=8)
    # plt.ylabel('Cumulative Probability', fontsize=8)
    # plt.grid(True, color='grey', linestyle=':', alpha=0.5)
    # plt.title(r"$\bf{Load~distribution~over~time}$", fontsize=8)
    # plt.xticks(fontsize=8)
    # plt.yticks(fontsize=8)

    # display plots
    # plt.savefig('loadspikes.pgf')
    # plt.savefig('loadsteady.pgf')
    plt.show()

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
    font_sz = 13


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
    plt.title(r"Throughput vs. target utilization (Long flows/Least-loaded)", fontsize=font_sz)
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
    font_sz = 13

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
    plt.title(r"Throughput vs. target utilization (Long flows/Least-connections)", fontsize=font_sz)
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
    font_sz = 13

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
    tps2[len(m1)-1] = 0 # goals2_short for this element was higher than 1 but cant be; the TP was also negative
    tps2_short = [get_qtp(util)/1e6 for util in goals2_short] # TODO: here; wrong, this is mis rate not util...
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
    plt.title(r"Throughput vs. number of misreports (Long flows/Least-loaded)", fontsize=font_sz)
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
    font_sz = 13

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
    tps2[len(m1)-1] = 0 # goals2_short for this element was higher than 1 but cant be; the TP was also negative
    tps2_short = [get_qtp(util)/1e6 for util in goals2_short] # TODO: here; wrong, this is mis rate not util...
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
    plt.title(r"Throughput vs. number of misreports (Long flows/Least-connections)", fontsize=font_sz)
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
        loads = parse()
        graph(loads)
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
