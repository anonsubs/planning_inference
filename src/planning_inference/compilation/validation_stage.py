from ..functions import generate_all_literals

from ..pddl import Predicate, TypedObject, Literal, Effect, Scheme
from ..pddl import Truth, Conjunction
from ..pddl import Increase, PrimitiveNumericExpression, NumericConstant

from .problem import generate_domain_objects

import numpy as np


def generate_test_fluents(indices):
    test_fluents = [Predicate("test" + str(i), []) for i in indices]
    return test_fluents

def generate_reached_fluents(indices, add_last=True):
    reached_fluents = [Predicate("reached" + str(i), []) for i in indices]
    if add_last:
        reached_fluents += [Predicate("reached_last", [])]
    return reached_fluents


def generate_plan_fluents(schemata):
    # Define action validation predicates
    # Example (plan-pickup ?i - step ?x - block)

    plan_fluents = []
    for scheme in schemata:
        plan_fluents += [Predicate("plan-" + scheme.name, [TypedObject("?i", "step")] + scheme.parameters)]

    return plan_fluents


def generate_validation_action(literals, new_actions, old_actions, count, observations_contain_actions, additional_effects=[], additional_preconditions=[]):
    pre = additional_preconditions
    eff = additional_effects

    pre += literals

    pre += [Literal("disabled", [], False)]

    if count != 0:
        pre += [Literal("test"+ str(count-1), [], True)]
        eff += [Effect([], Truth(), Literal("test"+ str(count-1), [], False))]

    eff += [Effect([], Truth(), Literal("test" + str(count), [], True))]

    if observations_contain_actions:
        if count != 0:
            pre += [Literal("current", ["i"+str(len(old_actions))], True)]
        eff += [Effect([], Truth(), Literal("current", ["i"+str(len(old_actions))], False))]
        eff += [Effect([], Truth(), Literal("current", ["i0"], True))]

    for i in range(len(new_actions)):
        action = new_actions[i]
        eff += [Effect([], Truth(), Literal("plan-" + action.name, ["i" + str(i)] + action.arguments, True))]

    for i in range(len(old_actions)):
        action = old_actions[i]
        eff += [Effect([], Truth(), Literal("plan-" + action.name, ["i" + str(i)] + action.arguments, False))]

    return Scheme("validate_" + str(count), [], 0, Conjunction(pre), eff, None)



def generate_validation_actions(observations, observations_contain_actions, predicates, types):
    validation_actions = []

    all_objects = generate_domain_objects(observations)
    all_literals = generate_all_literals(predicates, all_objects, types)

    last_state_validations = []
    # First validate action
    pre = [Literal("modeProg", [], True)]
    eff = [Effect([], Truth(), Literal("modeProg", [], False))]
    # eff += [Effect([], Truth(), l) for l in observations[0].states[0].literals if l.valuation]


    old_actions = []
    new_actions = []
    states_seen = 0
    literals = []

    for observation in observations:

        init_literals = observation.states[0].literals
        eff += [Effect([], Truth(), l) for l in init_literals if l.valuation and l not in literals] # add the literals of the initial state
        # eff += [Effect([], Truth(), l.negate()) for l in all_literals if l not in init_literals and l.negate() not in literals] # delete the goal state of the last observation
        eff += [Effect([], Truth(), l.negate()) for l in all_literals if
                l.valuation and l not in init_literals and l in literals]


        if observation.states[0].next_action is not None:
            new_actions += [observation.states[0].next_action]


        for state in observation.states[1:]:
            if state.literals != []:
                validation_action = generate_validation_action(literals, new_actions, old_actions, states_seen, observations_contain_actions, additional_preconditions=pre, additional_effects=eff)
                validation_actions += [validation_action]

                states_seen += 1
                literals = state.literals
                old_actions = new_actions
                new_actions = []
                pre = []
                eff = []

                pre += [Literal("action_applied", [], True)]
                eff += [Effect([], Truth(), Literal("action_applied", [], False))]

            if state.next_action is not None:
                new_actions += [state.next_action]

    validation_action = generate_validation_action(literals, new_actions, old_actions, states_seen,
                                                   observations_contain_actions, additional_preconditions=pre,
                                                   additional_effects=eff)
    validation_actions += [validation_action]




    return validation_actions


def generate_dfa_action(index, next_index, observation, partial_state, sensor_model):
    pre = []
    eff = []

    pre += [Literal("disabled", [], False)]
    pre += [Literal("action_applied", [], True)]
    eff += [Effect([], Truth(), Literal("action_applied", [], False))]

    pre += [Literal("reached"+ str(index), [], True)]
    eff += [Effect([], Truth(), Literal("reached"+ str(index), [], False))]

    if next_index != -1:
        eff += [Effect([], Truth(), Literal("reached"+ str(next_index), [], True))]
    else:
        eff += [Effect([], Truth(), Literal("reached_last", [], True))]

    if partial_state is not None:
        pre += partial_state.literals

    if observation is not None:
        for observable in observation.literals:
            for condition,probability in sensor_model.get_state_variables(observable).items():

                if probability == 0:
                    eff += [
                        Effect([], Conjunction(condition), Literal("disabled", [], True))]
                elif sensor_model.probabilistic and probability > 0 and probability < 1:
                    cost = -round(np.log(probability) * 100)
                    eff += [
                        Effect([], Conjunction(condition), Increase(PrimitiveNumericExpression("total-cost", []), NumericConstant(cost)))]


    return Scheme("validate" + str(index), [], 0, Conjunction(pre), eff, None)


def generate_sense_action(index, next_index, observation, partial_state, sensor_model):
    pre = []
    eff = []

    pre += [Literal("disabled", [], False)]
    pre += [Literal("action_applied", [], True)]
    eff += [Effect([], Truth(), Literal("action_applied", [], False))]

    pre += [Literal("reached"+ str(index), [], True)]
    eff += [Effect([], Truth(), Literal("reached"+ str(index), [], False))]

    if next_index != -1:
        eff += [Effect([], Truth(), Literal("reached"+ str(next_index), [], True))]
    else:
        eff += [Effect([], Truth(), Literal("reached_last", [], True))]

    if partial_state is not None:
        pre += partial_state.literals

    # if partial_state is not None and index != 0:
    #     pre += partial_state.literals

    if observation is not None:
        for observable in observation.literals:
            for condition,probability in sensor_model.get_state_variables(observable).items():

                if probability == 0:
                    eff += [
                        Effect([], Conjunction(condition), Literal("disabled", [], True))]
                elif sensor_model.probabilistic and probability > 0 and probability < 1:
                    cost = -round(np.log(probability) * 100)
                    eff += [
                        Effect([], Conjunction(condition), Increase(PrimitiveNumericExpression("total-cost", []), NumericConstant(cost)))]


    return Scheme("sense" + str(index), [], 0, Conjunction(pre), eff, None)





def generate_sense_missing_action(sensor_model):
    pre = []
    eff = []

    pre += [Literal("disabled", [], False)]

    pre += [Literal("action_applied", [], True)]
    eff += [Effect([], Truth(), Literal("action_applied", [], False))]

    o_to_s = sensor_model.get_o_to_s()

    for literal in sensor_model.get_observable_fluents():
        s_literal = o_to_s[literal]
        # Missing
        probability = sensor_model.observability_table[s_literal][2]
        if probability == 0:
            eff += [
                Effect([], s_literal, Literal("disabled", [], True))]
        elif probability > 0 and probability < 1:
            cost = -round(np.log(probability) * 100)
            eff += [
                Effect([], s_literal, Increase(PrimitiveNumericExpression("total-cost", []), NumericConstant(cost)))]
            # eff += [
            #     Effect([], s_literal.negate(),
            #            Increase(PrimitiveNumericExpression("total-cost", []), NumericConstant(cost)))]

    return Scheme("sense_missing", [], 0, Conjunction(pre), eff, None)


def generate_sense_actions(observation_sequence, hypothesis, sensor_model):
    sense_actions = []

    indices = sorted(set(observation_sequence.observations.keys()).union(set(hypothesis.states.keys())))

    for i in range(len(indices)):

        index = indices[i]

        next_index = -1
        if index != indices[-1]:
            next_index = indices[i + 1]


        observation = observation_sequence.observations.get(index, None)
        partial_state = hypothesis.states.get(index, None)

        sense_action = generate_sense_action(index, next_index, observation, partial_state, sensor_model)

        sense_actions += [sense_action]


    # Sense missing
    # sense_action = generate_sense_missing_action(sensor_model)
    # sense_actions += [sense_action]



    return sense_actions


def generate_dfa_actions(hypothesis, sensor_model, ordered=False):
    dfa_actions = []

    if not ordered:
        dfa = hypothesis.get_dfa()

        edges = list(dfa.edges)
        for edge in edges:
            source = edge[0]
            target = edge[1]
            condition = dfa.edges.get(edge)['condition']

            partial_state = None
            observation = None

            if "&" in condition:
                condition_parts = condition.replace(" ", "").split("&")
            else:
                condition_parts = [condition]

            for c in condition_parts:
                if c[0] == "s":
                    index = int(c[1:])
                    partial_state = hypothesis.states[index]
                elif c[0] == "o":
                    index = int(c[1:])
                    observation = hypothesis.observations[index]



            pre = []
            eff = []

            pre += [Literal("disabled", [], False)]
            pre += [Literal("action_applied", [], True)]
            eff += [Effect([], Truth(), Literal("action_applied", [], False))]

            pre += [Literal("reached" + str(source), [], True)]
            eff += [Effect([], Truth(), Literal("reached" + str(source), [], False))]

            eff += [Effect([], Truth(), Literal("reached" + str(target), [], True))]

            if partial_state is not None:
                pre += partial_state.literals


            if observation is not None:
                for observable in observation.literals:
                    for condition, probability in sensor_model.get_state_variables(observable).items():

                        if probability == 0:
                            eff += [
                                Effect([], Conjunction(condition), Literal("disabled", [], True))]
                        elif sensor_model.probabilistic and probability > 0 and probability < 1:
                            cost = -round(np.log(probability) * 100)
                            eff += [
                                Effect([], Conjunction(condition),
                                       Increase(PrimitiveNumericExpression("total-cost", []), NumericConstant(cost)))]

            dfa_actions += [Scheme("sense" + str(target), [], 0, Conjunction(pre), eff, None)]

    else:

        indices = sorted(set(hypothesis.observations.keys()).union(set(hypothesis.states.keys())))

        for i in range(len(indices)):

            index = indices[i]

            next_index = -1
            if index != indices[-1]:
                next_index = indices[i + 1]


            observation = hypothesis.observations.get(index, None)
            partial_state = hypothesis.states.get(index, None)

            dfa_action = generate_dfa_action(index, next_index, observation, partial_state, sensor_model)

            dfa_actions += [dfa_action]


    return dfa_actions