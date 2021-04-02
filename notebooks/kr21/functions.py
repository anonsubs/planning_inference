from planning_inference.parsers import parse_model, parse_problem, parse_plan, parse_trajectory, parse_LTLHypothesis
from planning_inference.generator import generate_trajectory
from planning_inference.functions import generate_all_literals, get_matching_literals

from planning_inference.pddl import Conjunction, Literal, Type, TypedObject, Effect, Truth, NumericConstant, PrimitiveNumericExpression, Increase
from planning_inference.pddl import SensorModel

from planning_inference.observations import Trajectory, Hypothesis, State

from planning_inference import DecodingTaskLTL

from sensor_models import load_sensor_model

import os
import copy
from collections import defaultdict
from itertools import combinations
from random import choice, choices, shuffle
from statistics import mean
import glob
import time


def launch_experiments(domain, task, timeout):
    Ms = load_sensor_model(domain)
    
    observabilities = [30, 50, 70]
       
    for observability in observabilities:
        base_path = "benchmark/%s/%s/%s/" % (domain, task, str(observability))

        problems = sorted(glob.glob(base_path + "*"))

        for problem in problems:
            costs = []
            times = []

            print(problem)

            # Planning Model
            Mp = parse_model(problem + "/domain")
            
            # Real Hypothesis
            with open(problem + "/sol", "r") as f:
                correct_h = int(f.read())

            print("Correct hypothesis: %d" % correct_h)

            # Observation sequence
#             obs = parse_observation_sequence(problem + "/obs")

            # Hypotheses
            h_files = sorted(glob.glob(problem + "/hyp*"))

            for i in range(len(h_files)):
                h = parse_LTLHypothesis(h_files[i])

                #Build a decoding problem for each hypothesis
                T = DecodingTaskLTL(Mp,Ms,h, ordered=True)

                tic = time.time()
                sol = T.decode(clean=True, planner="downward", t=timeout)
                toc = time.time()


                if len(sol.actions) == 0:
                    cost = 1000
                else:
                    cost = len(sol.actions)
                    sol.to_file(problem + "/plan.%s" % str(i).zfill(2))

                duration = toc - tic

                print("Hypothesis %d: %d, %.2f" % (i, cost, duration))

                costs.append(cost)
                times.append(duration)

            with open(problem + "/costs", "w") as f:
                f.write(" ".join(map(str, costs)))

            with open(problem + "/times", "w") as f:
                f.write(" ".join(map(str, times)))
                
                
def evaluate(domain, task, table_format=False):

    observabilities = [30, 50, 70]       
    for observability in observabilities:
        base_path = "benchmark/%s/%s/%s/" % (domain, task, str(observability))

        problems = sorted(glob.glob(base_path + "*"))

        H_sizes = []
        H_star_sizes = []
        found_correct = []
        times = []

        for problem in problems:
            h_costs = []
            h_times = []

            with open(problem + "/costs", "r") as f:
                h_costs = [int(c) for c in f.read().strip().split(" ")]

            with open(problem + "/times", "r") as f:
                h_times = [float(t) for t in f.read().strip().split(" ")]

            # Real Hypothesis
            with open(problem + "/sol", "r") as f:
                correct_h = int(f.read())

            # Hypotheses
            h_files = sorted(glob.glob(problem + "/hyp*"))

            H_sizes += [len(h_files)]

            min_cost = min(h_costs)
            H_star = [i for i in range(len(h_costs)) if h_costs[i] == min_cost]

            H_star_sizes += [len(H_star)]

            found_correct += [correct_h in H_star]

            times += [sum(h_times)]

        quality = len([found for found in found_correct if found])/len(found_correct)
        
        if table_format:
            print("%.2f & %.2f & %.2f & %.2f" % (mean(H_sizes), mean(H_star_sizes), quality, mean(times)))
        else:
            print("%s: %s at %s%%" % (domain, task, str(observability)))
            print("|H| = %.2f, |H*| = %.2f, Q = %.2f, T = %.2f" % (mean(H_sizes), mean(H_star_sizes), quality, mean(times)))
