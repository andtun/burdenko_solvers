import numpy as np
from pyomo.environ import *

# ----- PARAMS -----

solver_name = 'scip'
len_items = 10000
capacity = 250000
item_max_value = 100
item_max_weight = 100

display_solution = True

# ======= BODY =======

items = range(len_items)
model = ConcreteModel()
model.v = np.random.uniform(0, item_max_value, size=(len(items),))
model.w = np.random.uniform(0, item_max_weight, size=(len(items),))
model.x = Var(items, within=Binary)

def calc_value(model):
    return sum([model.x[i]*model.v[i] for i in items])

def check_weight(model):
    return sum([model.x[i]*model.w[i] for i in items]) <= capacity

model.target = Objective(rule=calc_value, sense=maximize)
model.wlimit = Constraint(rule=check_weight)
opt = SolverFactory(solver_name)
results = opt.solve(model, tee=True)
#model.solutions.load_from(results)
#print(model.solutions)
#print(results)
if display_solution: print(model.x.pprint())
