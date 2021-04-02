from ..pddl import Literal, Action
from ..observations import State, Trajectory, ObservationSequence, LTLHypothesis

from .pddl_parsing import parse_pddl_file
from .parsing_functions import parse_typed_list, parse_state

from ..functions import generate_all_literals

import random
from pyparsing import nestedExpr

import itertools


def parenthesize(alist):
    i = 0
    while i < len(alist) and not isinstance(alist[i], list):
        i += 1

    if i < len(alist):
        return "{}({})".format(" ".join(alist[:i]), parenthesize(alist[i]))
    else:
        return " ".join(alist[:i])


def parse_observation_sequence(observation_file):

    random.seed(123)

    with open(observation_file, 'r') as f:
        observation_pddl = f.read().replace('\n', '')

    observation_pddl = nestedExpr('(',')').parseString(observation_pddl).asList()

    iterator = iter(observation_pddl[0])

    tag = next(iterator)
    assert tag == "observation"

    # objects_opt = next(iterator)
    # assert objects_opt[0] == ":objects"
    # object_list = parse_typed_list(objects_opt[1:])

    observations = dict()

    for token in iterator:
        aux = token[0].split(":")

        order = int(aux[0])
        type = aux[1]

        if type == 'state':
            new_state = parse_state(token[1:], [], autocomplete=False)
            observations[order] = new_state
        elif type == 'action':
            next_action = Action(token[1][0], token[1][1:])

            state = observations.get(order, State([], None))

            state.next_action = next_action

            observations[order] = new_state


    return ObservationSequence(observations, False, False)


def parse_hypothesis(hypothesis_file):

    random.seed(123)

    with open(hypothesis_file, 'r') as f:
        hypothesis_pddl = f.read().replace('\n', '')

    hypothesis_pddl = nestedExpr('(',')').parseString(hypothesis_pddl).asList()

    iterator = iter(hypothesis_pddl[0])

    tag = next(iterator)
    assert tag == "hypothesis"

    objects_opt = next(iterator)
    assert objects_opt[0] == ":objects"
    object_list = parse_typed_list(objects_opt[1:])

    states = dict()

    for token in iterator:
        aux = token[0].split(":")

        order = int(aux[0])
        type = aux[1]

        if type == 'state':
            new_state = parse_state(token[1:], [], autocomplete=False)
            states[order] = new_state
        elif type == 'action':
            next_action = Action(token[1][0], token[1][1:])

            state = states.get(order, State([], None))

            state.next_action = next_action

            states[order] = new_state



    return Trajectory(object_list, states)


def parse_LTLHypothesis(hypothesis_file):

    random.seed(123)

    with open(hypothesis_file, 'r') as f:
        hypothesis_pddl = f.read().replace('\n', '')

    hypothesis_pddl = nestedExpr('(',')').parseString(hypothesis_pddl).asList()


    iterator = iter(hypothesis_pddl[0])

    tag = next(iterator)
    assert tag == "hypothesis"

    objects_opt = next(iterator)
    assert objects_opt[0] == ":objects"
    object_list = parse_typed_list(objects_opt[1:])

    formula_opt = next(iterator)
    assert formula_opt[0] == ":formula"
    formula = parenthesize(formula_opt[1:])

    states = dict()
    observations = dict()

    for token in iterator:
        aux = token[0].split(":")

        order = int(aux[0])
        type = aux[1]

        if type == 'state':
            new_state = parse_state(token[1:], [], autocomplete=False)
            states[order] = new_state
        elif type == 'observation':
            new_state = parse_state(token[1:], [], autocomplete=False)
            observations[order] = new_state
        # elif type == 'action':
        #     next_action = Action(token[1][0], token[1][1:])
        #
        #     state = states.get(order, State([], None))
        #
        #     state.next_action = next_action
        #
        #     states[order] = new_state

    return LTLHypothesis(object_list, states, observations, formula)


def parse_trajectory(trajectory_file, model):

    predicates = model.predicates
    types = model.types

    random.seed(123)

    with open(trajectory_file, 'r') as f:
        trajectory_pddl = f.read().replace('\n', '')

    trajectory_pddl = nestedExpr('(',')').parseString(trajectory_pddl).asList()


    iterator = iter(trajectory_pddl[0])

    tag = next(iterator)
    assert tag == "trajectory"

    objects_opt = next(iterator)
    assert objects_opt[0] == ":objects"
    object_list = parse_typed_list(objects_opt[1:])

    all_literals = set(generate_all_literals(predicates, object_list, types))


    states = dict()

    for token in iterator:
        aux = token[0].split(":")

        order = int(aux[0])
        type = aux[1]

        if type == 'state':
            new_state = parse_state(token[1:], all_literals)
            states[order] = new_state
        elif type == 'action':
            next_action = Action(token[1][0], token[1][1:])

            state = states.get(order, State([], None))

            state.next_action = next_action

            states[order] = new_state



    return Trajectory(object_list, states)




# def parse_trajectory(trajectory_file, model):
#
#     predicates = model.predicates
#     types = model.types
#
#     trajectory_pddl = parse_pddl_file('trajectory', trajectory_file)
#
#     random.seed(123)
#
#     iterator = iter(trajectory_pddl)
#
#     tag = next(iterator)
#     assert tag == "trajectory"
#
#     objects_opt = next(iterator)
#     assert objects_opt[0] == ":objects"
#     object_list = parse_typed_list(objects_opt[1:])
#
#     all_literals = set(generate_all_literals(predicates, object_list, types))
#
#
#     states = []
#
#
#     init = next(iterator)
#     assert init[0] == ":init"
#     new_state = parse_state(init[1:], all_literals)
#
#
#     for token in iterator:
#         if token[0] == ':state':
#             new_state = parse_state(token[1:], all_literals)
#         elif token[0] == ':action':
#             next_action = Action(token[1][0], token[1][1:])
#             new_state.next_action = next_action
#
#             states.append(new_state)
#
#
#     states.append(new_state)
#
#
#     return Trajectory(object_list, states)