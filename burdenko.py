import numpy as np
from pyomo.environ import *

# ----- PARAMS -----

solver_name = 'scip'
len_items = 100
capacity = 10
item_max_weight = 5

display_solution = True

# ======= BODY =======

items = range(len_items)
model = ConcreteModel()
model.w = np.random.uniform(0, item_max_weight, size=(len(items),))
model.x1 = Var(items, within=Binary)
model.x2 = Var(items, within=Binary)
model.x3 = Var(items, within=Binary)
model.x4 = Var(items, within=Binary)


def calc_value(model):
    return sum([(model.x1[i]*model.w[i] - capacity) for i in items]) + \
           sum([(model.x2[i]*model.w[i] - capacity) for i in items]) +\
           sum([(model.x3[i]*model.w[i] - capacity) for i in items]) +\
           sum([(model.x4[i]*model.w[i] - capacity) for i in items])

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
model.target = Objective(rule=calc_value, sense=minimize)
model.wlimit1 = Constraint(rule=check_weight1)
model.wlimit2 = Constraint(rule=check_weight2)
model.wlimit3 = Constraint(rule=check_weight3)
model.wlimit4 = Constraint(rule=check_weight4)
for i in range(len(items)):
    model.con = Constraint(rule=con(model, i))
opt = SolverFactory(solver_name)
results = opt.solve(model, tee=True)
#model.solutions.load_from(results)
#print(model.solutions)
#print(results)
if display_solution: print(model.x.pprint())