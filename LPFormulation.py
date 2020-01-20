"""
LP Formulation of Supermarket shipping problem
@author: Nicholas Whitlock
"""

import numpy as np
import pandas as pd # We will discuss this more next week!
from pulp import *
from importData import *
from Routes import *
from ModelFunctions import *

# Pandas DataFrame construction
areas = ['north', 'south', 'central', 'west']
nodes = getNodes('all')
routes = getRoutes(areas, False)
#Number of routes longer than 4 hours
count = 0
for route in routes:
    if (route.get_total_time() > 4*60*60):
        count += 1
print(count)
# routes = routes.Transpose()

nodeNames = []
for node in nodes:
    nodeNames.append(node.name)
routeIndex = np.arange(len(routes))

#Form dictionaries
Data = {}
nodeDemand = {}
for node in nodes:
    nodeDemand[node.name] = 1
    passing_routes = []
    for route in routes:
        passing_routes.append(0)
        for route_node in route.nodes:
            if node.name == route_node.name:
                passing_routes[-1] = 1
                break
    Data[node.name] = passing_routes

routePatterns = list(Data.values())

VariableData = pd.DataFrame(Data)


# The pattern data is made into a dictionary
routePatterns = makeDict([nodeNames,routeIndex],routePatterns,0)


# The variable 'prob' is created
prob = LpProblem("Supermarket shipping problem",LpMinimize)

# The problem variables of whether the routes are used or not
vars = LpVariable.dicts("Route",routeIndex,0,None, LpBinary)

# The objective function is entered: the total number of large rolls used * the fixed cost of each
prob += lpSum([vars[i]*routes[i].route_cost() for i in routeIndex]),"Shipping Cost"

# The demand minimum constraint is entered
for i in nodeNames:
    prob += lpSum([vars[j]*routePatterns[i][j] for j in routeIndex])>=nodeDemand[i],("Ensuring "+ i +"is visited") 

#Write to File
prob.writeLP("FoodStuffsModel.lp")

#Solve linear programme
prob.solve()

#Print Status of solution
print("Status: ", LpStatus[prob.status])

# Each of the variables is printed with it's resolved optimum value
for v in prob.variables():
    if v.varValue == 1:
        print(v.name, "was used")
# The optimised objective function value is printed to the screen
print("Shipping Costs = ", value(prob.objective))