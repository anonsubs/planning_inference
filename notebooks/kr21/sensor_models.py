from planning_inference.pddl import Literal
from planning_inference.pddl import SensorModel

import copy
from collections import defaultdict
from itertools import combinations, permutations, product, chain





def load_blocks_sensor_model():
    #### SENSOR MODEL DEFINITION ####
    d = defaultdict(dict)

    colors = {"red" : ["b1","b2","b3"], "green" : ["b4","b5","b6"], "blue" : ["b7","b8","b9"]}


    for color,blocks in colors.items():
        # clear   
        clear_blocks = [Literal("clear", [block], False) for block in blocks]

        for num_clear in range(len(clear_blocks)+1):
            for comb in list(combinations(range(len(clear_blocks)), num_clear)):
                condition = copy.deepcopy(clear_blocks)
                for i in comb:
                    condition[i] = condition[i].positive()

                d[frozenset(condition)][Literal("num_clear_%s" % color, [str(num_clear)], True)] = 1

                for i in range(len(clear_blocks)+1):
                    if i != num_clear:
                        d[frozenset(condition)][Literal("num_clear_%s" % color, [str(i)], True)] = 0


        # ontable
        ontable_blocks = [Literal("ontable", [block], False) for block in blocks]

        for num_ontable in range(len(ontable_blocks)+1):
            for comb in list(combinations(range(len(ontable_blocks)), num_ontable)):
                condition = copy.deepcopy(ontable_blocks)
                for i in comb:
                    condition[i] = condition[i].positive()

                d[frozenset(condition)][Literal("num_ontable_%s" % color, [str(num_ontable)], True)] = 1

                for i in range(len(ontable_blocks)+1):
                    if i != num_ontable:
                        d[frozenset(condition)][Literal("num_ontable_%s" % color, [str(i)], True)] = 0


    Ms = SensorModel(d)
    
    return Ms




def load_miconic_sensor_model():
    #### SENSOR MODEL DEFINITION ####
    d = defaultdict(dict)


#     persons = ["p0", "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"]
    persons = ["p0", "p1", "p2", "p3", "p4", "p5", "p6", "p7"]
#     persons = ["p0", "p1", "p2", "p3", "p4", "p5"]
    floors = ["f0", "f1", "f2", "f3", "f4"]
    lifts = ["l0", "l1"]



    # num_lifts
    for floor in floors:

        lift_positions = [Literal("lift-at", [lift, floor], False) for lift in lifts]

        for num_lifts in range(len(lift_positions)+1):
            for comb in list(combinations(range(len(lift_positions)), num_lifts)):
                condition = copy.deepcopy(lift_positions)
                for i in comb:
                    condition[i] = condition[i].positive()

                d[frozenset(condition)][Literal("num_lifts_%s" % floor, [str(num_lifts)], True)] = 1

                for i in range(len(lift_positions)+1):
                    if i != num_lifts:
                        d[frozenset(condition)][Literal("num_lifts_%s" % floor, [str(i)], True)] = 0

    # num_boarded                    
    for lift in lifts:

        boarded = [Literal("boarded", [person, lift], False) for person in persons]

        for num_boarded in range(len(boarded)+1):
            for comb in list(combinations(range(len(boarded)), num_boarded)):
                condition = copy.deepcopy(boarded)
                for i in comb:
                    condition[i] = condition[i].positive()

                d[frozenset(condition)][Literal("num_boarded_%s" % lift, [str(num_boarded)], True)] = 1

                for i in range(len(boarded)+1):
                    if i != num_boarded:
                        d[frozenset(condition)][Literal("num_boarded_%s" % lift, [str(i)], True)] = 0



    served = [Literal("served", [person], False) for person in persons]

    for num_served in range(len(served)+1):
        for comb in list(combinations(range(len(served)), num_served)):
            condition = copy.deepcopy(served)
            for i in comb:
                condition[i] = condition[i].positive()

            d[frozenset(condition)][Literal("num_served", [str(num_served)], True)] = 1

            for i in range(len(served)+1):
                if i != num_served:
                    d[frozenset(condition)][Literal("num_served", [str(i)], True)] = 0



    Ms = SensorModel(d)
    
    return Ms


def load_openstacks_sensor_model():
    #### SENSOR MODEL DEFINITION ####
    d = defaultdict(dict)

#     sizes = {"small":["o1", "o2", "o3", "o4"], "medium": ["o5", "o6", "o7"], "big": ["o8", "o9", "o10"]}
    sizes = {"small":["o1", "o2", "o3"], "medium": ["o4", "o5", "o6"], "big": ["o7", "o8", "o9"]}



    # num_waiting

    for size,orders in sizes.items():

        waiting_orders = [Literal("waiting", [order], False) for order in orders]

        for num_orders in range(len(waiting_orders)+1):
            for comb in list(combinations(range(len(waiting_orders)), num_orders)):
                condition = copy.deepcopy(waiting_orders)
                for i in comb:
                    condition[i] = condition[i].positive()

                d[frozenset(condition)][Literal("num_waiting_%s" % size, [str(num_orders)], True)] = 1

                for i in range(len(waiting_orders)+1):
                    if i != num_orders:
                        d[frozenset(condition)][Literal("num_waiting_%s" % size, [str(i)], True)] = 0


    # num_started

    for size,orders in sizes.items():

        started_orders = [Literal("started", [order], False) for order in orders]

        for num_orders in range(len(started_orders)+1):
            for comb in list(combinations(range(len(started_orders)), num_orders)):
                condition = copy.deepcopy(started_orders)
                for i in comb:
                    condition[i] = condition[i].positive()

                d[frozenset(condition)][Literal("num_started_%s" % size, [str(num_orders)], True)] = 1

                for i in range(len(started_orders)+1):
                    if i != num_orders:
                        d[frozenset(condition)][Literal("num_started_%s" % size, [str(i)], True)] = 0

    Ms = SensorModel(d)
    
    return Ms


def load_grid_sensor_model():
    #### SENSOR MODEL DEFINITION ####
    d = defaultdict(dict)

    shapes = {"triangle" : ["node44","node23","node32"], "circle" : ["node34","node33","node43"], "square" : ["node24","node22","node42"]}


    for shape,nodes in shapes.items():
        # locked

        locked_nodes = [Literal("locked", [n], False) for n in nodes]
        node_shape = [Literal("lock-shape", [n,shape], True) for n in nodes]

        for num_locked in range(len(locked_nodes)+1):
            for comb in list(combinations(range(len(locked_nodes)), num_locked)):
                condition = copy.deepcopy(locked_nodes)
                for i in comb:
                    condition[i] = condition[i].positive()

                condition += copy.deepcopy(node_shape)

                d[frozenset(condition)][Literal("num_locked_%s" % shape, [str(num_locked)], True)] = 1

                for i in range(len(locked_nodes)+1):
                    if i != num_locked:
                        d[frozenset(condition)][Literal("num_locked_%s" % shape, [str(i)], True)] = 0

    

    Ms = SensorModel(d)
    
    return Ms


def load_driverlog_sensor_model():
    #### SENSOR MODEL DEFINITION ####
    d = defaultdict(dict)

    trucks = ["truck1"]
    packages = ["package%s" % str(i+1) for i in range(4)]
    cities = {"t": ["t1", "t2", "t3"], "s": ["s1", "s2", "s3", "s4"], "d": ["d1", "d2", "d3", "d4"], "h": ["h1", "h2", "h3", "h4", "h5", "h6"]}
    locations = [loc for sublist in cities.values() for loc in sublist]

    # TRUCK CITY
    at_trucks = [Literal("at", [truck, loc], True) for loc in locations for truck in trucks]

    for at_truck in at_trucks:
        at_city = at_truck.args[1][0]
        for city in cities.keys():         
            if at_city == city:  
                d[frozenset([at_truck])][Literal("city", [city], True)] = 1
            else:
                d[frozenset([at_truck])][Literal("city", [city], True)] = 0        

    # NUM PACKAGES
    for city,locations in cities.items():

        at_packages = [Literal("at", [package, loc], False) for package in packages for loc in locations]

        groups = [range(len(locations)) for _ in range(len(packages))]

        for num_packages in range(len(packages)+1):
#             print(num_packages, city)
            package_combs = combinations(range(len(packages)), num_packages)
            for package_comb in package_combs:
                counts = [1 for _ in range(len(package_comb))]
    #             print("packages", package_comb)

                selections = [combinations(g, c) for g, c in zip(groups, counts)]    
                combs = list(product(*selections))
                for comb in combs:

                    condition = copy.deepcopy(at_packages)
                    indices = tuple(chain.from_iterable(comb))
    #                 print("location", indices)
                    for j in range(len(package_comb)):
                        condition[package_comb[j]*len(locations)+indices[j]] = condition[package_comb[j]*len(locations)+indices[j]].positive()
    #                 print(condition)
                    d[frozenset(condition)][Literal("num_packages_%s" % city, [str(num_packages)], True)] = 1

                    for i in range(len(packages)+1):
                        if i != num_packages:
                            d[frozenset(condition)][Literal("num_packages_%s" % city, [str(i)], True)] = 0


    Ms = SensorModel(d)
    
    return Ms


def load_floortile_sensor_model():
    #### SENSOR MODEL DEFINITION ####
    d = defaultdict(dict)


    rows = {"r0": ["tile_0-1", "tile_0-2", "tile_0-3"], "r1": ["tile_1-1", "tile_1-2", "tile_1-3"], "r2": ["tile_2-1", "tile_2-2", "tile_2-3"], "r3": ["tile_3-1", "tile_3-2", "tile_3-3"] }
    colors = ["white", "black"]


    # num_color_row
    for row,tiles in rows.items():
        for color in colors:

            painted_tiles = [Literal("painted", [tile, color], False) for tile in tiles]

            for num_tiles in range(len(tiles)+1):
                for comb in list(combinations(range(len(tiles)), num_tiles)):
                    condition = copy.deepcopy(painted_tiles)
                    for i in comb:
                        condition[i] = condition[i].positive()

                    d[frozenset(condition)][Literal("num_%s_%s" % (color, row), [str(num_tiles)], True)] = 1

                    for i in range(len(tiles)+1):
                        if i != num_tiles:
                            d[frozenset(condition)][Literal("num_%s_%s" % (color, row), [str(i)], True)] = 0



    Ms = SensorModel(d)
    
    return Ms


def load_sensor_model(domain):
    
    if domain == "blocks":
        return load_blocks_sensor_model()
    elif domain == "miconic":
        return load_miconic_sensor_model()
    elif domain == "grid":
        return load_grid_sensor_model()
    elif domain == "openstacks":
        return load_openstacks_sensor_model()
    elif domain == "driverlog":
        return load_driverlog_sensor_model()
    elif domain == "floortile":
        return load_floortile_sensor_model()