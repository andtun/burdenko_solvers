from __future__ import division
import numpy as np
from pyomo.environ import *
from pyomo.opt import SolverFactory
from pyomo.opt.parallel import SolverManagerFactory
import sys

# ----- PARAMS -----

solver_name = 'scip'
len_items = 20
capacity = 5
item_max_weight = 5

display_solution = True

# ======= BODY =======

items = np.arange(len_items)
action_handle_map = {} # maps action handles to instances
model_map = {}
opt = SolverFactory(solver_name)
opt.options["threads"] = 4

solver_manager = SolverManagerFactory('pyro')
if solver_manager is None:
    print("Failed to create solver manager.")
    sys.exit(1)

def calc_value(model):
    return sum([model.x1[i]*model.w[i] for i in items]) + \
           sum([model.x2[i]*model.w[i] for i in items]) +\
           sum([model.x3[i]*model.w[i] for i in items]) +\
           sum([model.x4[i]*model.w[i] for i in items])

def check_weight1(model):
    return sum([model.x1[i]*model.w[i] for i in items]) <= capacity

def check_weight2(model):
    return sum([model.x2[i]*model.w[i] for i in items]) <= capacity

def check_weight3(model):
    return sum([model.x3[i]*model.w[i] for i in items]) <= capacity

def check_weight4(model):
    return sum([model.x4[i]*model.w[i] for i in items]) <= capacity

def con(model, i):
    return model.x1[i] + model.x2[i] + model.x3[i] + model.x4[i] <= 1

def display(model):
    print(model.x1.pprint(),
          model.x2.pprint(),
          model.x3.pprint(),
          model.x4.pprint(), sep="\n")

class Model:

    def __init__(self, **kwargs):
        items = np.arange(len_items)
        model = ConcreteModel()
        model.w = np.random.uniform(0, item_max_weight, size=(len(items),))
        model.x1 = Var(items, within=Binary)
        model.x2 = Var(items, within=Binary)
        model.x3 = Var(items, within=Binary)
        model.x4 = Var(items, within=Binary)
        model.target = Objective(rule=calc_value, sense=maximize)
        model.wlimit1 = Constraint(rule=check_weight1)
        model.wlimit2 = Constraint(rule=check_weight2)
        model.wlimit3 = Constraint(rule=check_weight3)
        model.wlimit4 = Constraint(rule=check_weight4)

        model.con = list()
        for i in range(len(items)):
            model.con.append(Constraint(rule=con(model, i)))

        self.model = model
        self.items = items

    def solve(self, **kwargs):
        model = self.model
        results = opt.solve(model, tee=True, logfile="some_file_name.log")
        #model.solutions.load_from(results)
        #print(model.solutions)
        #print(results)
        if display_solution: print(model.x1.pprint(),
                                   model.x2.pprint(),
                                   model.x3.pprint(),
                                   model.x4.pprint(), sep="\n")

    def display(self):
        model = self.model
        print(model.x1.pprint(),
              model.x2.pprint(),
              model.x3.pprint(),
              model.x4.pprint(), sep="\n")
        


model1 = Model()
model2 = Model()

#model1.solve()


action_handle = solver_manager.queue(model1.model, opt=opt, tee=True)
action_handle_map[action_handle] = "Random uniform 1"
model_map[action_handle] = model1.model
action_handle = solver_manager.queue(model2.model, opt=opt, tee=True)
action_handle_map[action_handle] = "Random uniform 2"
model_map[action_handle] = model2.model

# retrieve the solutions
for i in range(2): # we know there are two instances
    this_action_handle = solver_manager.wait_any()
    solved_name = action_handle_map[this_action_handle]
    results = solver_manager.get_results(this_action_handle)
    print("Results for", solved_name)
    model = model_map[this_action_handle]
    display(model)
    print("1 done")


