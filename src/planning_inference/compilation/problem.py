from ..pddl import TypedObject, Literal, Conjunction
from ..observations import State

def generate_goal(last=None):

    if last is not None:
        return Conjunction([Literal("reached" + str(last), [], True), Literal("disabled", [], False)])
    else:
        return Conjunction([Literal("reached_last", [], True), Literal("disabled", [], False)])


def generate_domain_objects(observations):
    objects = []
    for observation in observations:
        objects += observation.objects
    objects = list(set(objects))

    return objects


def generate_step_objects(max_actions):

    return [TypedObject("i" + str(i), "step") for i in range(max_actions+1)]


def generate_initial_state(initial_state, allow_editing=False, first=0):

    init = [Literal("modeProg", [], allow_editing)]
    init += [Literal("action_applied", [], True)]
    init += [Literal("reached" + str(first), [], True)]

    init += initial_state.literals



    return State(init, None)

