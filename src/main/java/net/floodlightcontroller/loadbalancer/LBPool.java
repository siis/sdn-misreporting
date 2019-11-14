package net.floodlightcontroller.loadbalancer;
///**

// *    Copyright 2013, Big Switch Networks, Inc.
// *
// *    Licensed under the Apache License, Version 2.0 (the "License"); you may
// *    not use this file except in compliance with the License. You may obtain
// *    a copy of the License at
// *
// *         http://www.apache.org/licenses/LICENSE-2.0
// *
// *    Unless required by applicable law or agreed to in writing, software
// *    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// *    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// *    License for the specific language governing permissions and limitations
// *    under the License.
// **/

import java.io.IOException;
import java.io.FileWriter;
import java.io.PrintWriter;

//package net.floodlightcontroller.loadbalancer;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
//import java.util.List;
import java.util.Random;
import java.util.concurrent.TimeUnit;

import org.projectfloodlight.openflow.types.U64;
//
//import org.slf4j.Logger;
//import org.slf4j.LoggerFactory;
//
//import com.fasterxml.jackson.databind.annotation.JsonSerialize;
//
//import net.floodlightcontroller.loadbalancer.LoadBalancer.IPClient;
//
///**
// * Data structure for Load Balancer based on
// * Quantum proposal http://wiki.openstack.org/LBaaS/CoreResourceModel/proposal 
// * 
// * @author KC Wang
// */
import java.util.Scanner;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.stream.IntStream;

//@JsonSerialize(using=LBPoolSerializer.class)
public class LBPool {
	// protected static Logger log = LoggerFactory.getLogger(LBPool.class);
	protected String id;
	protected String name;
	protected String tenantId;
	protected String netId;
	protected short lbMethod;
	protected byte protocol;
	// protected ArrayList<String> members;
	public ArrayList<String> members; // make this public so we can add members from the simualtor
	protected ArrayList<String> monitors;
	protected ArrayList<String> prevPicked;
	protected short adminState;
	protected short status;
	protected final static short ROUND_ROBIN = 1;
	protected final static short STATISTICS = 2;
	protected final static short WEIGHTED_RR = 3;
	protected Random rm;
	protected int robin;
	HashMap<String, U64> membersBandwidth_last;
	HashMap<String, U64> membersBandwidth_temp;
	int round_boundary;

	protected String vipId;

	protected int previousMemberIndex;

	protected LBStats poolStats;

	// QB: new
	ArrayList<U64> loads_since_last_chosen;
	// ArrayList<Float> total_loads_since_last_chosen;
	// ArrayList<Float> all_total_loads_since_last_chosen;
	// ArrayList<Float> interval_length_since_last_chosen;
	boolean first;
	int round_training_over;
	final int _attack_window_length = 300; // *****
	final int _burst_training_window = 1; // *****
	final int _rounds_traning = 60; // *****
	final int warmup_rounds_before_traning = 30;
	ArrayList<U64> observed_loads;
	final float PERCENTILE = (float) 0.99;
	float avg_under_report_amount = (float) 0.0;
	float avg_burst_size;
	boolean period_update_ready;
	float bursts_observed;
	ArrayList<U64> burst_list;
	int round; // incremented at the end of pickMember
	int period_for_goal_load;
	// final float GOAL_LOAD = (float) 5e3*8; // in bits
	final float GOAL_LOAD = (float) 75; // in bits
	double threshold = 0.01; // *****
	final int ATTACK_TYPE = 2; // 1 for dos, 2 for stealthy, 3 for control
	int delayed_ur_wll_50;
	int delayed_ur_wlc_50;
	int delayed_ur_wll_10;
	int delayed_ur_wlc_10;
	int batch_flag;
	final int batch_size = 1;
	final Random r4 = new Random();
	final int LL = 0; // least-loaded
	final int WLL = 1; // weighted least-loaded
	final int LC = 2; // least-conn
	final int WLC = 3; // weighted least-conn
	final int R = 4; // random
	final int RR = 5; // round-robin
	final int policy = 0; // QB: using this now instead of the arg for easier switching
	final int policy_on_multi_min = -1;
	int num_misreports;
	int num_times_bad_switch_chosen_after_mis;
	int num_times_bad_switch_chosen_overall;
	boolean misreported;
	int NUM_ROUNDS;
	long start_time;
	U64 adversary_current_load;
	double temp_arr[];
	ArrayList<U64> adversary_loads_overall;
	ArrayList<U64> adversary_loads_during_atk;
	long time_in_file_done;
	int SHORT_FLOWS_TRAFFIC = 0;
	int LONG_FLOWS_TRAFFIC = 1;
	int TRAFFIC_TYPE = LONG_FLOWS_TRAFFIC;
	// int TRAFFIC_TYPE = SHORT_FLOWS_TRAFFIC;

	public LBPool() {
		// QB: new
		loads_since_last_chosen = new ArrayList<U64>();
		// total_loads_since_last_chosen = new ArrayList();
		// all_total_loads_since_last_chosen = new ArrayList();
		// interval_length_since_last_chosen = new ArrayList();
		first = true;
		round_training_over = 0;
		observed_loads = new ArrayList<U64>();
		avg_burst_size = (float) 0;
		period_update_ready = false;
		bursts_observed = 0;
		burst_list = new ArrayList<U64>();
		adversary_loads_overall = new ArrayList<U64>();
		adversary_loads_during_atk = new ArrayList<U64>();
		round = 0;
		period_for_goal_load = 0;
		delayed_ur_wll_50 = 0;
		delayed_ur_wlc_50 = 0;
		delayed_ur_wll_10 = 0;
		delayed_ur_wlc_10 = 0;
		batch_flag = 0;
		num_misreports = 0;
		num_times_bad_switch_chosen_after_mis = 0;
		num_times_bad_switch_chosen_overall = 0;
		misreported = false;
		NUM_ROUNDS = 1800;
		start_time = 0;
		adversary_current_load = U64.of(0);
		time_in_file_done = 0;

		// id = String.valueOf((int) (Math.random()*10000));
		// name = null;
		// tenantId = null;
		// netId = null;
		lbMethod = 2;
		// protocol = 0;
		members = new ArrayList<String>();
		prevPicked = new ArrayList<String>();
		monitors = new ArrayList<String>();
		// adminState = 0;
		// status = 0;
		previousMemberIndex = -1;
		rm = new Random();
		robin = 0;

		membersBandwidth_last = new HashMap<String, U64>();
		membersBandwidth_temp = new HashMap<String, U64>();
		round_boundary = 0;

		poolStats = new LBStats();
	}

	public String lbMethodToString(short lbMethod) {
		if (lbMethod == 1) {
			return "Round-Robin";
		} else if (lbMethod == 2) {
			return "Statistics";
		} else if (lbMethod == 3) {
			return "Weighted Round-Robin";
		}
		return "Invalid Method";
	}

	public void setPoolStatistics(ArrayList<Long> bytesIn, ArrayList<Long> bytesOut, int activeFlows) {
		if (!bytesIn.isEmpty() && !bytesOut.isEmpty()) {
			long sumIn = 0;
			long sumOut = 0;

			for (Long bytes : bytesIn) {
				sumIn += bytes;
			}
			poolStats.bytesIn = sumIn;

			for (Long bytes : bytesOut) {
				sumOut += bytes;
			}
			poolStats.bytesOut = sumOut;
			poolStats.activeFlows = activeFlows;
		}
	}

	// QB: implement atk
	public U64 adversary_run(U64 current_load, int NUM_MEMBERS, int policy, long curr_time_in_file) {
		// dont need to do pre-processing for LC/WLC (Sim:773) because we assume that
		// the load balancer already has the proper statistics
		if (current_load == null) {
			return null;
		}
		// Phase 1 - Reconnaissance
		System.out.println("time: " + String.valueOf(System.nanoTime()));
		if (((System.nanoTime() - start_time) / 1e9) >= (warmup_rounds_before_traning + _rounds_traning)) { // if its been
																																																																																																						// 600s warmup;
																																																																																																						// lower this for
																																																																																																						// initial testing
			// if (loads_since_last_chosen.size() >= _rounds_traning) {
			System.out.println("loads_since_last_chosen: ");
			System.out.println(loads_since_last_chosen.toString());
			Collections.sort(loads_since_last_chosen);
			Collections.sort(observed_loads);
			// double temp_arr[] = new double[loads_since_last_chosen.size()];
			// double temp_arr[] = new double[observed_loads.size()];
			temp_arr = new double[observed_loads.size()];
			// for (int f = 0; f < loads_since_last_chosen.size(); f++) {
			// temp_arr[f] = (double) loads_since_last_chosen.get(f);
			// }
			for (int f = 0; f < observed_loads.size(); f++) {
				temp_arr[f] = (double) observed_loads.get(f).getValue();
			}
			Collections.sort(observed_loads);
			if (current_load.getValue() > temp_arr[(int) (PERCENTILE * observed_loads.size())]) {
				// consider it a burst
				bursts_observed++;
				burst_list.add(current_load);
				System.out.println("true (burst): " + String.valueOf(current_load));
				System.out.println("burst_list size: " + String.valueOf(burst_list.size()));
				period_update_ready = true;
			} else {
				// ignore
			}
		} else {
			// ignore
		}

		if ((bursts_observed == _burst_training_window + 1) && period_update_ready) {
			period_update_ready = false;
			// train on bursts now instead of picks

			// get average burst size
			avg_burst_size = 0;
			for (int l = 0; l < burst_list.size(); l++) {
				avg_burst_size += burst_list.get(l).getValue();
			}
			avg_burst_size = avg_burst_size / burst_list.size();

			// #######
			if (round_training_over == 0) {
				round_training_over = round;
				time_in_file_done = curr_time_in_file;
			}

			period_for_goal_load = (int) (Math.round(avg_burst_size / GOAL_LOAD));
			if (period_for_goal_load == 0) {
				period_for_goal_load = 1;
			}

			if (round > warmup_rounds_before_traning) {
				if (first) {
					first = false;
					observed_loads.add(current_load); // add this one last true_bw before we stop recording observed loads
				}
			}
		}

		if (round > warmup_rounds_before_traning) {
			loads_since_last_chosen.add(current_load);
			if (first) {
				observed_loads.add(current_load);
			}
		}

		// Phase 2 - Send misreport
		if (ATTACK_TYPE == 1) { // dos attack
			// membersBandwidth.put("member[" + String.valueOf(BAD_SWITCH) + "]", (float)
			// 0);
			misreported = true;
			num_misreports++;
			return U64.of(0);
		} else if (ATTACK_TYPE == 2) { // intelligent attack
			System.out.println((bursts_observed >= _burst_training_window + 1));
			System.out.println((round > round_training_over));
			System.out.println((round < (round_training_over + _attack_window_length)));
			System.out.println((period_for_goal_load > 0));
			if (period_for_goal_load > 0) {
				System.out.println((round % period_for_goal_load == 0));
			}

			if (TRAFFIC_TYPE == SHORT_FLOWS_TRAFFIC) {
				if (((bursts_observed >= _burst_training_window + 1) && (round > round_training_over)
						&& (round < (round_training_over + _attack_window_length)) && (period_for_goal_load > 0)
						&& (round % period_for_goal_load == 0)) || (delayed_ur_wll_50 >= 1) || (delayed_ur_wlc_50 >= 1)
						|| (delayed_ur_wll_10 >= 1) || (delayed_ur_wlc_10 == 1)) {
					System.out.println("up in here short");
					// double threshold = 0.01; // *****
					// double budget = 5e3;
					U64 updated_load = U64.of(0);
					Collections.sort(observed_loads);
					// System.out.println("\robserved_loads size: " +
					// String.valueOf(observed_loads.size()));
					// updated_load = (float) (observed_loads
					// .get(r4.nextInt((int) ((Math.ceil((double) (observed_loads.size() *
					// threshold))) - 1))));
					updated_load = observed_loads.get(r4.nextInt((int) (Math.ceil((double) (observed_loads.size() * threshold)))));
					// if (policy == LEAST_LOADED) {
					if (current_load.getValue() < observed_loads
							.get((int) ((Math.ceil((double) (observed_loads.size() * threshold))) - 1)).getValue()) {
						System.out.println("didnt use updated load");
						// membersBandwidth.put("member[" + String.valueOf(BAD_SWITCH) + "]",
						// bad_switch_true_bw);
						return current_load;
					} else {
						// if (updated_load > budget) {
						// System.out.println("didnt use updated load (under-report larger than
						// budget)");
						// } else {
						// if (NUM_MEMBERS == 50) { // ur twice more for pool 50
						// // if (policy == WEIGHTED_LEAST_CONNECTIONS) {
						// if (policy == WLC) {
						// if (delayed_ur_wlc_50 == 2) {
						// delayed_ur_wlc_50 = 0;
						// System.out.println("delayed it");
						// } else {
						// delayed_ur_wlc_50++;
						// }
						// // } else if (policy == WEIGHTED_LEAST_LOADED) {
						// } else if (policy == WLL) {
						// if (delayed_ur_wll_50 == 2) {
						// delayed_ur_wll_50 = 0;
						// System.out.println("delayed it");
						// } else {
						// delayed_ur_wll_50++;
						// }
						// }
						// } else if (NUM_MEMBERS == 10) { // only do it once more for pool 10
						// // if (policy == WEIGHTED_LEAST_CONNECTIONS) {
						// if (policy == WLC) {
						// if (delayed_ur_wlc_10 == 1) {
						// delayed_ur_wlc_10 = 0;
						// System.out.println("delayed it");
						// } else {
						// delayed_ur_wlc_10++;
						// }
						// // } else if (policy == WEIGHTED_LEAST_LOADED) {
						// } else if (policy == WLL) {
						// if (delayed_ur_wll_10 == 2) {
						// delayed_ur_wll_10 = 0;
						// System.out.println("delayed it");
						// } else {
						// delayed_ur_wll_10++;
						// }
						// }
						// }
						num_misreports++;
						misreported = true;

						double observed_loads_mean = 0;
						for (int j = 0; j < observed_loads.size(); j++) {
							observed_loads_mean += observed_loads.get(j).getValue();
						}
						observed_loads_mean /= observed_loads.size();

						double observed_loads_std = 0;
						for (int j = 0; j < observed_loads.size(); j++) {
							observed_loads_std += Math.pow(observed_loads.get(j).getValue() - observed_loads_mean, 2)
									/ observed_loads.size();
						}
						observed_loads_std = Math.sqrt(observed_loads_std);

						System.out.print("observed_loads: ");
						System.out.println(observed_loads);
						System.out.println("\robserved_loads size: " + String.valueOf(observed_loads.size()));
						System.out.println("observed_loads_mean: " + String.format("%.3f", observed_loads_mean));
						System.out.println("observed_loads_std: " + String.format("%.3f", observed_loads_std));
						System.out.println("policy: " + String.valueOf(policy));
						// System.out.println("misreporting amount (of total):
						// num_misreports/(NUM_ROUNDS) = " + String.valueOf(num_misreports) + "/" +
						// String.valueOf(NUM_ROUNDS) + " = " + String.format("%.3f", num_misreports *
						// 1.0 / (NUM_ROUNDS)));
						System.out.println("misreporting amount (of total): num_misreports/(round) = " + String.valueOf(num_misreports)
								+ "/" + String.valueOf(round) + " = " + String.format("%.3f", num_misreports * 1.0 / (round)));
						System.out.println("misreporting amount (during atk window): num_misreports/(_attack_window_length) = "
								+ String.valueOf(num_misreports) + "/" + String.valueOf(_attack_window_length) + " = "
								+ String.format("%.3f", num_misreports * 1.0 / (_attack_window_length)));
						System.out.println("num_times_bad_switch_chosen_overall: " + String.valueOf(num_times_bad_switch_chosen_overall));
						System.out.println("misreporting success: num_times_bad_switch_chosen_after_mis/num_misreports = "
								+ String.valueOf(num_times_bad_switch_chosen_after_mis) + "/" + String.valueOf(num_misreports) + " = "
								+ String.format("%.3f", num_times_bad_switch_chosen_after_mis * 1.0 / num_misreports));
						System.out.println(
								"Elapsed time: " + String.format("%.2f", (double) ((System.nanoTime() - start_time) / 1e9)) + " seconds");

						// membersBandwidth.put("member[" + String.valueOf(BAD_SWITCH) + "]",
						// updated_load);
						System.out.println("used updated load: " + updated_load.toString());
						return updated_load;
					}
				}
			} else if (TRAFFIC_TYPE == LONG_FLOWS_TRAFFIC) {
				// if (((bursts_observed >= _burst_training_window + 1) && (round >
				// round_training_over)
				// && (round < (round_training_over + _attack_window_length)) &&
				// (period_for_goal_load > 0)
				// && (round % period_for_goal_load == 0)) || (delayed_ur_wll_50 >= 1) ||
				// (delayed_ur_wlc_50 >= 1)
				// || (delayed_ur_wll_10 >= 1) || (delayed_ur_wlc_10 == 1)) {
				if (((round > (warmup_rounds_before_traning + _rounds_traning))
						&& (round < ((warmup_rounds_before_traning + _rounds_traning) + _attack_window_length))
						&& ((round - round_training_over) % 10 == 0)) || (batch_flag > 0)) { // every 10th round after training over
					// QB (1//18/2020: only check if training rounds over and between attack window
					System.out.println("up in here long");
					// if (batch_flag < (batch_size-1)) {
					// batch_flag++;
					// System.out.println("delayed next");
					// } else if (batch_flag == (batch_size-1)) {
					// // return current_load; // only send batch once for now, so once it hits 2,
					// just send current_load
					// batch_flag = 0; // reset for next batch in 10s
					// }
					if (batch_flag == (batch_size - 1)) {
						// return current_load; // only send batch once for now, so once it hits 2, just
						// send current_load
						batch_flag = 0; // reset for next batch in 10s
					} else {
						batch_flag++;
					}

					if (round_training_over == 0) {
						round_training_over = round;
						time_in_file_done = curr_time_in_file;
					}
					// double threshold = 0.01; // *****
					// double budget = 5e3;
					U64 updated_load = U64.of(0);
					Collections.sort(observed_loads);
					// System.out.println("\robserved_loads size: " +
					// String.valueOf(observed_loads.size()));
					// updated_load = (float) (observed_loads
					// .get(r4.nextInt((int) ((Math.ceil((double) (observed_loads.size() *
					// threshold))) - 1))));
					updated_load = observed_loads.get(r4.nextInt((int) (Math.ceil((double) (observed_loads.size() * threshold)))));
					// if (policy == LEAST_LOADED) {
					if (current_load.getValue() < observed_loads
							.get((int) ((Math.ceil((double) (observed_loads.size() * threshold))) - 1)).getValue()) {
						System.out.println("didnt use updated load");
						// membersBandwidth.put("member[" + String.valueOf(BAD_SWITCH) + "]",
						// bad_switch_true_bw);
						return current_load;
					} else {
						// if (updated_load > budget) {
						// System.out.println("didnt use updated load (under-report larger than
						// budget)");
						// } else {
						// if (NUM_MEMBERS == 50) { // ur twice more for pool 50
						// // if (policy == WEIGHTED_LEAST_CONNECTIONS) {
						// if (policy == WLC) {
						// if (delayed_ur_wlc_50 == 2) {
						// delayed_ur_wlc_50 = 0;
						// System.out.println("delayed it");
						// } else {
						// delayed_ur_wlc_50++;
						// }
						// // } else if (policy == WEIGHTED_LEAST_LOADED) {
						// } else if (policy == WLL) {
						// if (delayed_ur_wll_50 == 2) {
						// delayed_ur_wll_50 = 0;
						// System.out.println("delayed it");
						// } else {
						// delayed_ur_wll_50++;
						// }
						// }
						// } else if (NUM_MEMBERS == 10) { // only do it once more for pool 10
						// // if (policy == WEIGHTED_LEAST_CONNECTIONS) {
						// if (policy == WLC) {
						// if (delayed_ur_wlc_10 == 1) {
						// delayed_ur_wlc_10 = 0;
						// System.out.println("delayed it");
						// } else {
						// delayed_ur_wlc_10++;
						// }
						// // } else if (policy == WEIGHTED_LEAST_LOADED) {
						// } else if (policy == WLL) {
						// if (delayed_ur_wll_10 == 2) {
						// delayed_ur_wll_10 = 0;
						// System.out.println("delayed it");
						// } else {
						// delayed_ur_wll_10++;
						// }
						// }
						// }
						num_misreports++;
						misreported = true;

						double observed_loads_mean = 0;
						for (int j = 0; j < observed_loads.size(); j++) {
							observed_loads_mean += observed_loads.get(j).getValue();
						}
						observed_loads_mean /= observed_loads.size();

						double observed_loads_std = 0;
						for (int j = 0; j < observed_loads.size(); j++) {
							observed_loads_std += Math.pow(observed_loads.get(j).getValue() - observed_loads_mean, 2)
									/ observed_loads.size();
						}
						observed_loads_std = Math.sqrt(observed_loads_std);

						System.out.print("observed_loads: ");
						System.out.println(observed_loads);
						System.out.println("\robserved_loads size: " + String.valueOf(observed_loads.size()));
						System.out.println("observed_loads_mean: " + String.format("%.3f", observed_loads_mean));
						System.out.println("observed_loads_std: " + String.format("%.3f", observed_loads_std));
						System.out.println("policy: " + String.valueOf(policy));
						// System.out.println("misreporting amount (of total):
						// num_misreports/(NUM_ROUNDS) = " + String.valueOf(num_misreports) + "/" +
						// String.valueOf(NUM_ROUNDS) + " = " + String.format("%.3f", num_misreports *
						// 1.0 / (NUM_ROUNDS)));
						System.out.println("misreporting amount (of total): num_misreports/(round) = " + String.valueOf(num_misreports)
								+ "/" + String.valueOf(round) + " = " + String.format("%.3f", num_misreports * 1.0 / (round)));
						System.out.println("misreporting amount (during atk window): num_misreports/(_attack_window_length) = "
								+ String.valueOf(num_misreports) + "/" + String.valueOf(_attack_window_length) + " = "
								+ String.format("%.3f", num_misreports * 1.0 / (_attack_window_length)));
						System.out.println("num_times_bad_switch_chosen_overall: " + String.valueOf(num_times_bad_switch_chosen_overall));
						System.out.println("misreporting success: num_times_bad_switch_chosen_after_mis/num_misreports = "
								+ String.valueOf(num_times_bad_switch_chosen_after_mis) + "/" + String.valueOf(num_misreports) + " = "
								+ String.format("%.3f", num_times_bad_switch_chosen_after_mis * 1.0 / num_misreports));
						System.out.println(
								"Elapsed time: " + String.format("%.2f", (double) ((System.nanoTime() - start_time) / 1e9)) + " seconds");

						// membersBandwidth.put("member[" + String.valueOf(BAD_SWITCH) + "]",
						// updated_load);
						System.out.println("used updated load: " + updated_load.toString());
						avg_under_report_amount = (avg_under_report_amount * (num_misreports - 1)
								+ (current_load.getValue() - updated_load.getValue())) / num_misreports;
						return updated_load;
					}
				}
			}
		}
		return current_load;
	}

	// public String pickMember(IPClient client, HashMap<String,U64>
	// membersBandwidth,HashMap<String,Short> membersWeight,HashMap<String, Short>
	// memberStatus) {
	public String pickMember(/* IPClient client, */ HashMap<String, U64> membersBandwidth,
			HashMap<String, Short> memberStatus, int policy_unused, boolean new_round, long curr_time_in_file) { // ipclient not
																																																																																																								// used,
																																																																																																								// membersweight
																																																																																																								// not used for
																																																																																																								// statistics,
																																																																																																								// and we assume
																																																																																																								// all members
																																																																																																								// are active
		if (new_round) {
			if (start_time == 0) { // QB: start warmup and burst training
				start_time = System.nanoTime();
			}
		}

		// from Simulator.java
		// LEAST_LOADED = 0;
		// WEIGHTED_LEAST_LOADED = 1;
		// LEAST_CONNECTIONS = 2;
		// WEIGHTED_LEAST_CONNECTIONS = 3;
		// int LL = 0; // least-loaded
		// int WLL = 1; // weighted least-loaded
		// int LC = 2; // least-conn
		// int WLC = 3; // weighted least-conn
		// int R = 4; // random
		// int RR = 5; // round-robin
		// int policy = 1; // QB: using this now instead of the arg for easier switching
		// int policy_on_multi_min = -1;

		// System.out.println("adversary is member [" +
		// String.valueOf(membersBandwidth.size()-1) + "]");
		System.out.println("adversary is member [" + String.valueOf(membersBandwidth.size()) + "]");
		if (new_round) {
			// let adversary do stuff first; ONLY ON NEW COLLECTION ROUNDS, otherwise dont
			// call this for just new clients
			// System.out.println("adversary is member [" +
			// String.valueOf(membersBandwidth.size()-1) + "]");
			// System.out.println("this is it: " +
			// String.valueOf(membersBandwidth.get(String.valueOf(membersBandwidth.size()-1))));
			System.out.println("this is it: " + String.valueOf(membersBandwidth.get(String.valueOf(membersBandwidth.size()))));
			System.out.println(membersBandwidth);
			// U64 load =
			// adversary_run(membersBandwidth.get(String.valueOf(membersBandwidth.size()-1)),
			// membersBandwidth.size(), policy); // QB: get last one
			U64 load = adversary_run(membersBandwidth.get(String.valueOf(membersBandwidth.size())), membersBandwidth.size(),
					policy, curr_time_in_file);
			if (load == null) {
				System.out.println("load is null");
				return null;
			}
			// membersBandwidth.put(String.valueOf(membersBandwidth.size()-1), load);
			membersBandwidth.put(String.valueOf(membersBandwidth.size()), load);
			adversary_current_load = load;
			// System.out.println("this is after: " +
			// String.valueOf(membersBandwidth.get(String.valueOf(membersBandwidth.size()-1))));
			System.out
					.println("this is after: " + String.valueOf(membersBandwidth.get(String.valueOf(membersBandwidth.size()))));
			System.out.println("and this is all: " + membersBandwidth.toString());
			round++; // QB: moved this here to only update whenver its a new round; attack looked
												// like it wasnt lasting the full 600 for some reason
		} else {
			membersBandwidth.put(String.valueOf(membersBandwidth.size()), adversary_current_load); // gets updated every
																																																																																										// new_round
		}

		if (members.size() > 0) {
			if (lbMethod == STATISTICS && !membersBandwidth.isEmpty() && membersBandwidth.values() != null) {
				ArrayList<String> poolMembersId = new ArrayList<String>();
				// Get the members that belong to this pool and the statistics for them
				System.out.println("membersBandwidth.keySet().size(): " + String.valueOf(membersBandwidth.keySet().size()));
				for (String memberId : membersBandwidth.keySet()) {
					for (int i = 0; i < members.size(); i++) {
						// if(LoadBalancer.isMonitoringEnabled && !monitors.isEmpty() &&
						// !memberStatus.isEmpty()){ // if health monitors active (my note: floodlight
						// just checks port_desc msg to see if port is up/down, and toggles lbmember
						// up/down; if up, send ICMP to further investigate/validate
						if (true && true && !memberStatus.isEmpty()) { // ***always assume health monitors are active
							// for better simulation of dynamic behavior of
							// the load balancer***
							if (members.get(i).equals(memberId) && memberStatus.get(memberId) != -1) {
								poolMembersId.add(memberId);
							}
						} else { // no health monitors active
							if (members.get(i).equals(memberId)) {
								// System.out.println("member: " + members.get(i));
								poolMembersId.add(memberId);
							}
						}
					}
				}

				// // QB: testing
				// return "1";

				// return the member which has the minimum bandwidth usage, out of this pool
				// members
				if (!poolMembersId.isEmpty()) {
					System.out.println("poolMembersId not empty");
					System.out.println(poolMembersId.toString());

					if (new_round) { // edit (1/30/2020): only update the loads with weighting on a new_round; was
																						// prob just repeating same weight for every flow (100 or 1000) before the next
																						// new_round, essentially driving the load toward membersBandwidth faster
																						// (basically makes the hisorical load obsolete); this will drive the attackers
																						// load to 0 (or within the 1 percentile) before the next new_round, so the
																						// second underreport is successful (?)
						if ((policy == WLC) || (policy == WLL)) {
							float weight_for_latest = (float) 0.5;
							U64 new_load = U64.of((long) 0);
							for (String memberId : membersBandwidth.keySet()) {
								if (membersBandwidth_last.keySet().contains(memberId)) {
									new_load = U64.of((long) ((weight_for_latest * membersBandwidth_last.get(memberId).getValue())
											+ ((1 - weight_for_latest) * membersBandwidth.get(memberId).getValue())));
									// membersBandwidth.put(memberId, new_load);
									// membersBandwidth_last.put(memberId, new_load);
									// if ("9".compareTo(memberId) == 0) {
									// if ("10".compareTo(memberId) == 0) {
									if (String.valueOf(membersBandwidth.size()).compareTo(memberId) == 0) {
										// System.out.println("get: " + String.valueOf(membersBandwidth.get(memberId)));
										// System.out.println("last: " +
										// String.valueOf(membersBandwidth_last.get(memberId)));
										// System.out.println("new: " + String.valueOf(new_load));
									}
									membersBandwidth.put(memberId, new_load);
									membersBandwidth_last.put(memberId, new_load);
								} else { // should only hit for 1st round
									membersBandwidth_last.put(memberId, membersBandwidth.get(memberId));
								}
							}
						}
					}

					// ArrayList<U64> bandwidthValues = new ArrayList<U64>();
					ArrayList<U64> bandwidthValues = new ArrayList<U64>();
					ArrayList<String> membersWithMin = new ArrayList<String>();
					Collections.sort(poolMembersId);

					for (int j = 0; j < poolMembersId.size(); j++) {
						// System.out.println("member[" + String.valueOf(j) + "]: " +
						// String.valueOf(membersBandwidth.get(poolMembersId.get(j))));
						bandwidthValues.add(membersBandwidth.get(poolMembersId.get(j)));
						// if ("9".compareTo(poolMembersId.get(j)) == 0) {
						// if ("10".compareTo(poolMembersId.get(j)) == 0) {
						if (String.valueOf(membersBandwidth.size()).compareTo(poolMembersId.get(j)) == 0) {
							System.out
									.println("setting attacker bw value to: " + String.valueOf(membersBandwidth.get(poolMembersId.get(j))));
							if (new_round) {
								adversary_loads_overall.add(membersBandwidth.get(poolMembersId.get(j)));

								if (TRAFFIC_TYPE == SHORT_FLOWS_TRAFFIC) {
									if (((bursts_observed >= _burst_training_window + 1) && (round > round_training_over)
											&& (round < (round_training_over + _attack_window_length)) && (period_for_goal_load > 0))) {
										// && (round % period_for_goal_load == 0))) {
										adversary_loads_during_atk.add(membersBandwidth.get(poolMembersId.get(j)));
									}
								} else if (TRAFFIC_TYPE == LONG_FLOWS_TRAFFIC) {
									if ((round > (warmup_rounds_before_traning + _rounds_traning))
											&& (round < ((warmup_rounds_before_traning + _rounds_traning) + _attack_window_length))) {
										// if (((bursts_observed >= _burst_training_window + 1) && (round > round_training_over)
										// 		&& (round < (round_training_over + _attack_window_length)) && (period_for_goal_load > 0))) {
											if (((round > round_training_over) && (round < (round_training_over + _attack_window_length)) && (period_for_goal_load > 0))) { // shouldnt need bursts_observed for long flows; was causing weird problems in the load dist plot
											// && (round % period_for_goal_load == 0))) {
											adversary_loads_during_atk.add(membersBandwidth.get(poolMembersId.get(j)));
										}
									}
								}
							}
						}
					}
					// U64 minBW = Collections.min(bandwidthValues);
					System.out.println("bandwidthValues: " + bandwidthValues.toString());
					System.out.println("ATTACK_TYPE: " + String.valueOf(ATTACK_TYPE));
					System.out.println("policy: " + String.valueOf(policy));
					System.out.println("round_training_over: " + String.valueOf(round_training_over));
					System.out.println("time_in_file_done: " + String.valueOf(time_in_file_done));
					System.out.println("PERCENTILE: " + String.valueOf(PERCENTILE));
					System.out.println("bursts_observed: " + String.valueOf(bursts_observed));
					System.out.println("period_for_goal_load: " + String.valueOf(period_for_goal_load));
					System.out.println("round: " + String.valueOf(round));
					System.out.println("avg_burst_size: " + String.valueOf(avg_burst_size / 8.0 / 1e3) + " KB");
					System.out.println("GOAL_LOAD: " + String.valueOf(GOAL_LOAD / 8.0 / 1e3) + " KB");
					System.out.println("misreporting amount (of total): num_misreports/(round) = " + String.valueOf(num_misreports)
							+ "/" + String.valueOf(round) + " = " + String.format("%.3f", num_misreports * 1.0 / (round)));
					System.out.println("misreporting amount (during atk window): num_misreports/(_attack_window_length) = "
							+ String.valueOf(num_misreports) + "/" + String.valueOf(_attack_window_length) + " = "
							+ String.format("%.3f", num_misreports * 1.0 / (_attack_window_length)));
					System.out.println("num_times_bad_switch_chosen_overall: " + String.valueOf(num_times_bad_switch_chosen_overall));
					System.out.println("misreporting success: num_times_bad_switch_chosen_after_mis/num_misreports = "
							+ String.valueOf(num_times_bad_switch_chosen_after_mis) + "/" + String.valueOf(num_misreports) + " = "
							+ String.format("%.3f", num_times_bad_switch_chosen_after_mis * 1.0 / num_misreports));
					System.out.println("avg_under_report_amount: " + String.valueOf(avg_under_report_amount / 1e3) + " Kb");
					if (observed_loads.size() > 0) {
						if (temp_arr != null && temp_arr.length > 0) {
							System.out.println("burst threshold: "
									+ String.valueOf(temp_arr[(int) (PERCENTILE * observed_loads.size())] / 8.0 / 1e3) + " KB");
						}
						System.out.println("low threshold load: " + String
								.valueOf(observed_loads.get((int) ((Math.ceil((double) (observed_loads.size() * threshold))) - 1)).getValue()
										/ 8.0 / 1e3)
								+ " KB");
					}

					// ########### more prints
					double ov_loads_mean = 0;
					if (adversary_loads_overall.size() > 0) {
						for (int j = 0; j < adversary_loads_overall.size(); j++) {
							ov_loads_mean += adversary_loads_overall.get(j).getValue();
						}
						ov_loads_mean /= adversary_loads_overall.size();
					}
					System.out.println("ov_loads_mean: " + String.format("%.3f", ov_loads_mean / 8.0 / 1e3) + " KB");

					double da_loads_mean = 0;
					if (adversary_loads_during_atk.size() > 0) {
						for (int j = 0; j < adversary_loads_during_atk.size(); j++) {
							da_loads_mean += adversary_loads_during_atk.get(j).getValue();
						}
						da_loads_mean /= adversary_loads_during_atk.size();
					}
					System.out.println("da_loads_mean: " + String.format("%.3f", da_loads_mean / 8.0 / 1e3) + " KB");
					// ###########

					U64 minBW = Collections.min(bandwidthValues);
					String memberToPick = poolMembersId.get(bandwidthValues.indexOf(minBW));

					for (Integer i = 0; i < bandwidthValues.size(); i++) {
						if (bandwidthValues.get(i).equals(minBW)) {
							membersWithMin.add(poolMembersId.get(i));
							// return poolMembersId.get(i);
						}
					}
					System.out.println("membersWithMin: " + membersWithMin.toString());

					// my code
					if (policy == RR) {
						memberToPick = members.get(robin % (members.size() - 1));
						robin++;
					} else if ((policy == LC) || (policy == WLC) || (policy == LL) || (policy == WLL)) {
						if (policy_on_multi_min == RR) { // RR on multiple min
							if (membersWithMin.size() > 1) {
								memberToPick = membersWithMin.get(robin % (membersWithMin.size() - 1));
								robin++;
							} else {
								System.out.println("good to go");
								memberToPick = membersWithMin.get(0);
							}
						} else { // random on multiple min
							memberToPick = membersWithMin.get(rm.nextInt(membersWithMin.size()));
						}
					} else { // random
						memberToPick = members.get(rm.nextInt(members.size()));
					}

					// #################################################################################
					// #################################################################################
					// #################################################################################
					// size of the prev list is half of the number of available members
					// int sizeOfPrevPicked = bandwidthValues.size()/2;

					// if (membersWithMin.size() > 1) {
					// System.err.println("Multiple members with min: " + String.valueOf(minBW));
					// }

					// // memberToPick = membersWithMin.get(rm.nextInt(membersWithMin.size())); //
					// ***** remove this; pick from above code

					// // Remove previously picked members from being eligible for being picked now
					// for (Iterator<String> it = membersWithMin.iterator(); it.hasNext();){
					// String memberMin = it.next();
					// if(prevPicked.contains(memberMin)){
					// it.remove();
					// }
					// }
					// // Keep the previously picked list to a size based on the members of the pool
					// if(prevPicked.size() > sizeOfPrevPicked) {
					// // System.err.println("adjust prevPicked");
					// prevPicked.remove(prevPicked.size()-1);
					// }

					// // If there is only one member with min BW value and membersWithMin is empty
					// if(membersWithMin.isEmpty()){
					// memberToPick = prevPicked.get(prevPicked.size()-1); // means that the min
					// member has been prevs picked
					// }else
					// memberToPick = membersWithMin.get(0);

					// prevPicked.add(0, memberToPick); //set the first memberId of prevPicked to be
					// // the last member picked

					// log.debug("Member {} picked using Statistics",memberToPick);
					System.out.println("Member [" + memberToPick + "] has been picked by the load balancer.");
					// round++; // moved this up; shouldnt be updating if its not a new round
					// if (memberToPick.equals(String.valueOf(membersBandwidth.size()-1))) {
					if (memberToPick.equals(String.valueOf(membersBandwidth.size()))) {
						num_times_bad_switch_chosen_overall++;
						if (misreported) {
							num_times_bad_switch_chosen_after_mis++;
							misreported = false;
						}
					}
					return memberToPick;
				}
				return null;
			}
			// else if(lbMethod == WEIGHTED_RR && !membersWeight.isEmpty()){
			//
			// HashMap<String, Short> activeMembers = new HashMap<String, Short>();
			//
			// if(LoadBalancer.isMonitoringEnabled && !monitors.isEmpty() &&
			// !memberStatus.isEmpty()){ // if health monitors active
			// for(String memberId: membersWeight.keySet()){
			// if(memberStatus.get(memberId) != -1){
			// activeMembers.put(memberId, membersWeight.get(memberId));
			// }
			// }
			// return weightsToMember(activeMembers); // only members with status != -1
			//
			// } else
			// return weightsToMember(membersWeight); // all members in membersWeight are
			// considered
			// }else {
			// if(LoadBalancer.isMonitoringEnabled && !monitors.isEmpty() &&
			// !memberStatus.isEmpty()){ // if health monitors active
			// for(int i=0;i<members.size();){
			// previousMemberIndex = (previousMemberIndex + 1) % members.size();
			// if(memberStatus.get(members.get(previousMemberIndex)) != -1)
			// return members.get((previousMemberIndex));
			// }
			// return null;
			// } else{
			// // simple round robin
			// previousMemberIndex = (previousMemberIndex + 1) % members.size();
			// return members.get(previousMemberIndex);
			// }
			// }
		} else {
			System.out.println("members has 0 size");
		}
		return null;
	}

	// /**
	// * helper function to pick a member
	// * @param weights - hashmap with memberId and weight of the member
	// * @return member picked by Weighted Round Robin
	// */
	// private String weightsToMember(HashMap<String, Short> weights){
	// Random randomNumb = new Random();
	// short totalWeight = 0;
	//
	// for(Short weight: weights.values()){
	// totalWeight += weight;
	// }
	//
	// int rand = randomNumb.nextInt(totalWeight);
	// short val = 0;
	// for(String memberId: weights.keySet()){
	// val += weights.get(memberId);
	// if(val > rand){
	// log.debug("Member {} picked using WRR",memberId);
	// return memberId;
	// }
	// }
	// return null;
	// }
}
