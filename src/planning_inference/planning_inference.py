from .compilation import generate_model_representation_fluents
from .compilation import generate_programming_actions
from .compilation import generate_auxiliary_programming_fluents
from .compilation import generate_programmable_action
from .compilation import generate_extended_action

from .compilation import generate_reached_fluents
from .compilation import generate_plan_fluents
from .compilation import generate_validation_actions
from .compilation import generate_sense_actions
from .compilation import generate_dfa_actions

from .compilation import generate_step_type
from .compilation import generate_step_predicates

from .compilation import generate_goal
from .compilation import generate_initial_state
from .compilation import generate_domain_objects
from .compilation import generate_step_objects

from .compilation import get_model_space_size

from .compilation import ModelRecognitionSolution

from .pddl import Problem

from .parsers import parse_solution
from .parsers import parse_plan

import copy
import os

class DecodingTaskLTL(object):

    def __init__(self, planning_model, sensor_model, hypothesis, ordered=False):
        self.planning_model = planning_model
        self.sensor_model = sensor_model
        self.hypothesis = hypothesis

        self.compiled_model = self.__compile_model(ordered)
        self.compiled_problem = self.__compile_problem(ordered)

    def __compile_model(self, ordered):
        compiled_model = copy.deepcopy(self.planning_model)
        compiled_model.schemata = []

        if not ordered:
            dfa = self.hypothesis.get_dfa()
            indices = sorted(list(dfa.nodes))
        else:
            indices = sorted(
                set(self.hypothesis.observations.keys()).union(set(self.hypothesis.states.keys())))

        # Programming

        for scheme in self.planning_model.schemata:
            extended_action = generate_extended_action(scheme, False, False, False)
            compiled_model.schemata += [extended_action]

        auxiliary_programming_fluents = generate_auxiliary_programming_fluents()
        compiled_model.predicates += auxiliary_programming_fluents


        # Validation

        if not ordered:
            reached_fluents = generate_reached_fluents(indices, add_last=False)
        else:
            reached_fluents = generate_reached_fluents(indices)
        compiled_model.predicates += reached_fluents

        dfa_actions = generate_dfa_actions(self.hypothesis, self.sensor_model, ordered=ordered)

        compiled_model.schemata += dfa_actions

        return compiled_model


    def __compile_problem(self, ordered):

        if not ordered:
            init = generate_initial_state(self.hypothesis.states[0], first=1)
        else:
            init = generate_initial_state(self.hypothesis.states[0], first=0)

        dfa = self.hypothesis.get_dfa()
        for node in dfa.nodes:
            if dfa.nodes.get(node)["final"]:
                last = node

        if not ordered:
            goal = generate_goal(last=last)
        else:
            goal = generate_goal()

        objects = self.hypothesis.objects


        return Problem("compiled_problem", self.planning_model.domain_name, objects, init, goal, use_metric=False)


    def decode(self, clean=True, parallel=True, planner="madagascar", t=3000):
        problem_file = 'compiled_problem'
        domain_file = 'compiled_domain'
        solution_file = 'solution_plan'
        log_file = "planner_out"

        self.compiled_model.to_file(domain_file)
        self.compiled_problem.to_file(problem_file)

        # initial_model_propositional_encoding = self.initial_model.propositional_encoding()

        if planner == "madagascar":
            planner_path =  os.path.join(os.path.dirname(__file__), 'util/planners/madagascar/M')

            # min_horizon = sum([max(o.number_of_states*2 - 1, o.number_of_states+o.number_of_actions) for o in self.observations]) - len(self.observations) + 1
            min_horizon = len(set(self.observation_sequence.observations.keys()).union(self.hypothesis.states.keys()))*2 -1

            cmd_args = [planner_path, domain_file, problem_file, "-S 1", "-Q", "-o %s" % solution_file, "-F %s" % min_horizon]

            if not parallel:
                cmd_args += ["-P 0"]

            cmd_args += ["> %s" % log_file]

        elif planner == "downward":
            planner_path = "/home/dieaigar/PhD/downward/fast-downward.py"

            # cmd_args = [planner_path, '--plan-file %s' % solution_file, domain_file, problem_file, '--evaluator "lmc=lmcount(lm_rhw(),admissible=true)" --search "astar(lmc,lazy_evaluator=lmc)"']
            cmd_args = [planner_path, '--plan-file %s' % solution_file, domain_file, problem_file, '--evaluator "lmc=merge_and_shrink(shrink_strategy=shrink_bisimulation(greedy=false),merge_strategy=merge_sccs(order_of_sccs=topological,merge_selector=score_based_filtering(scoring_functions=[goal_relevance,dfp,total_order])),label_reduction=exact(before_shrinking=true,before_merging=false),max_states=50k,threshold_before_merge=1)" --search "astar(lmc,lazy_evaluator=lmc)"']

        elif planner == "downward2":
            planner_path = "/home/dieaigar/PhD/downward/fast-downward.py"

            cmd_args = [planner_path, '--plan-file %s' % solution_file, domain_file, problem_file, '--evaluator "lmc=lmcount(lm_rhw(),admissible=true)" --search "astar(lmc,lazy_evaluator=lmc)"']

        elif planner == "downward-sat":
            planner_path = "/home/dieaigar/PhD/downward/fast-downward.py"

            cmd_args = [planner_path, '--alias seq-sat-lama-2011', '--plan-file %s' % solution_file, domain_file, problem_file]



        elif planner == "metric-ff":
            planner_path = os.path.join(os.path.dirname(__file__), 'util/planners/metric-FF/ff')

            cmd_args = [planner_path, "-E", "-O", "-g 1", "-h 0", "-o %s" % domain_file, "-f %s" % problem_file, "-s %s" % solution_file]


        cmd = " ".join(cmd_args)
        cmd = "ulimit -t %d; " % t + cmd

        # print(cmd)
        os.system(cmd)

        solution = parse_plan(solution_file)


        if clean:
            cmd = "rm %s; rm %s; rm %s; rm %s" % (domain_file, problem_file, solution_file, log_file)
            os.system(cmd)




        return solution

class DecodingTask(object):

    def __init__(self, planning_model, sensor_model, observation_sequence, hypothesis):
        self.planning_model = planning_model
        self.sensor_model = sensor_model
        self.observation_sequence = observation_sequence
        self.hypothesis = hypothesis

        self.compiled_model = self.__compile_model()
        self.compiled_problem = self.__compile_problem()

    def __compile_model(self):
        compiled_model = copy.deepcopy(self.planning_model)
        compiled_model.schemata = []

        indices = sorted(set(self.observation_sequence.observations.keys()).union(set(self.hypothesis.states.keys())))

        # Programming

        for scheme in self.planning_model.schemata:

            extended_action = generate_extended_action(scheme, False, False, False)
            # if self.use_cost:
            #     extended_action.cost = scheme.cost

            compiled_model.schemata += [extended_action]

        auxiliary_programming_fluents = generate_auxiliary_programming_fluents()
        compiled_model.predicates += auxiliary_programming_fluents

        # effects_programming_action = generate_effects_programming_action()
        # compiled_model.schemata += [effects_programming_action]



        # Validation

        reached_fluents = generate_reached_fluents(indices)
        compiled_model.predicates += reached_fluents

        sense_actions = generate_sense_actions(self.observation_sequence, self.hypothesis, self.sensor_model)

        compiled_model.schemata += sense_actions

        return compiled_model


    def __compile_problem(self):

        init = generate_initial_state(self.hypothesis.states[0])

        goal = generate_goal()

        objects = self.hypothesis.objects


        return Problem("compiled_problem", self.planning_model.domain_name, objects, init, goal, use_metric=False)


    def decode(self, clean=True, parallel=True, planner="madagascar", t=3000):
        problem_file = 'compiled_problem'
        domain_file = 'compiled_domain'
        solution_file = 'solution_plan'
        log_file = "planner_out"

        self.compiled_model.to_file(domain_file)
        self.compiled_problem.to_file(problem_file)

        # initial_model_propositional_encoding = self.initial_model.propositional_encoding()

        if planner == "madagascar":
            planner_path =  os.path.join(os.path.dirname(__file__), 'util/planners/madagascar/M')

            # min_horizon = sum([max(o.number_of_states*2 - 1, o.number_of_states+o.number_of_actions) for o in self.observations]) - len(self.observations) + 1
            min_horizon = len(set(self.observation_sequence.observations.keys()).union(self.hypothesis.states.keys()))*2 -1

            cmd_args = [planner_path, domain_file, problem_file, "-S 1", "-Q", "-o %s" % solution_file, "-F %s" % min_horizon]

            if not parallel:
                cmd_args += ["-P 0"]

            cmd_args += ["> %s" % log_file]

        elif planner == "downward":
            planner_path = "/home/dieaigar/PhD/downward/fast-downward.py"

            # cmd_args = [planner_path, '--plan-file %s' % solution_file, domain_file, problem_file, '--evaluator "lmc=lmcount(lm_rhw(),admissible=true)" --search "astar(lmc,lazy_evaluator=lmc)"']
            cmd_args = [planner_path, '--plan-file %s' % solution_file, domain_file, problem_file, '--evaluator "lmc=merge_and_shrink(shrink_strategy=shrink_bisimulation(greedy=false),merge_strategy=merge_sccs(order_of_sccs=topological,merge_selector=score_based_filtering(scoring_functions=[goal_relevance,dfp,total_order])),label_reduction=exact(before_shrinking=true,before_merging=false),max_states=50k,threshold_before_merge=1)" --search "astar(lmc,lazy_evaluator=lmc)"']

        elif planner == "downward2":
            planner_path = "/home/dieaigar/PhD/downward/fast-downward.py"

            cmd_args = [planner_path, '--plan-file %s' % solution_file, domain_file, problem_file, '--evaluator "lmc=lmcount(lm_rhw(),admissible=true)" --search "astar(lmc,lazy_evaluator=lmc)"']

        elif planner == "downward-sat":
            planner_path = "/home/dieaigar/PhD/downward/fast-downward.py"

            cmd_args = [planner_path, '--alias seq-sat-lama-2011', '--plan-file %s' % solution_file, domain_file, problem_file]



        elif planner == "metric-ff":
            planner_path = os.path.join(os.path.dirname(__file__), 'util/planners/metric-FF/ff')

            cmd_args = [planner_path, "-E", "-O", "-g 1", "-h 0", "-o %s" % domain_file, "-f %s" % problem_file, "-s %s" % solution_file]


        cmd = " ".join(cmd_args)
        cmd = "ulimit -t %d; " % t + cmd

        # print(cmd)
        os.system(cmd)

        solution = parse_plan(solution_file)


        if clean:
            cmd = "rm %s; rm %s; rm %s; rm %s" % (domain_file, problem_file, solution_file, log_file)
            os.system(cmd)




        return solution