'''
Group 16: Simulation functions.
Author: Derek Long and Karl Zhu
'''

import numpy as np
import pandas as pd # We will discuss this more next week!
import copy
from pulp import *
from importData import *
from RoutesFunctions import *
from GraphObjects import *
from LPFormulation import *

def simulateDemands(saturday = False):
    # Import weekday data as df and weekend data as we
    if not saturday:
        df, we = importProbabilities()
    if saturday:
        we, df = importProbabilities()

    # Using weekday data probabilities for the rest of code below
    row, col = df.shape
    nodes = [0] * (row-1)

    # Loop through each row (except Supermarket) in data
    for i in range(1,row):
        node = Node()                                               # Initialise node
        node.name = df.iloc[i][0]                                   # Set the name
        node.wd_prob = [float(df.iloc[i][1])] + [0.] * (col-2)      # Initialise weekday probability array
        num = random.uniform(0,1)
        
        # Loop through each column in row to get probabilities
        j = 2
        while node.wd_prob[j-2] != 1.0 and j < col: # If the sum of previous probabilities is not 1
            node.wd_prob[j-1] = float(df.iloc[i][j]) + node.wd_prob[j-2]    # Add column value and previous
            if num <= node.wd_prob[j-1] and num >= node.wd_prob[j-2] and not saturday: # Check where the probability value lies
                node.weekday = j-1                  # Set weekday value to be pallet demand
            elif num <= node.wd_prob[j-1] and num >= node.wd_prob[j-2] and saturday: # Check where the probability value lies
                node.saturday = j-1  
            j += 1

        # Add to nodes
        nodes[i-1] = node
    return nodes
    
def simulateCost(n,saturday = False):
    '''
    Simulates the variation of objective cost due to variations in demands and traffic times.
    n : Number of simulations
    '''
    obj_routes = LpSolve(solveRoutes = False, saturday = saturday)
    routes = getRoutes(areas = ['north', 'south', 'central', 'west'], solve = False, saturday = saturday)
    total_cost = [0] * n

    print('obtained routes, starting simulations...')
    for s in range(n):
        sim_nodes = simulateDemands(saturday)

        # nodes that haven't been satisfied
        unsat_nodes = []

        # Go through each route and node to change demands
        for route in obj_routes:
            for node in route.nodes:
                for sim_node in sim_nodes:
                    if (node.name == sim_node.name):
                        # why not just change to:
                        #node = sim_node ------- sim_node doesnt have lat,long, which i thought we might've use
                        node.weekday = sim_node.weekday
                        node.saturday = sim_node.saturday
                        break

            while route.get_total_pallets(not saturday) > 12:
                # add last store (last node is warehouse) to unsatisfied nodes
                unsat_nodes.append(route.nodes.pop(-2))
                route.arcs.pop(-1)  # get rid of last arc

                # assign to_node of last arc to warehouse
                route.arcs[-1].to_node = route.nodes[-1]

                # assign to_node second to last arc to last store
                route.arcs[-2].to_node = route.nodes[-2]

            total_cost[s] += route.route_cost(weekday= not saturday, traffic = True)

        
        
        unsat_nodes.insert(0,routes[0].nodes[0])
        unsat_nodes.append(routes[0].nodes[0])
        rs = routes_from_nodes(nodes = unsat_nodes, saturday = saturday)
        unsat_nodes.pop(0)
        unsat_nodes.pop(-1)
        # Set the current number of routes used
        num_routes = len(obj_routes)

        # Go through all unsatisfied nodes and go to them individually
        for node in unsat_nodes:
            
            # Go through all the routes to find the one needed
            i = 0
            while (rs[i].nodes != [routes[i].nodes[0],node,routes[i].nodes[-1]] and i < len(rs)-1):
                i += 1

            # Check if we can still use Foodstuffs trucks
            if num_routes < 20:
                # Add cost of Foodstuffs truck to total
                total_cost[s] += routes[i].route_cost(weekday= not saturday, traffic = True)
                num_routes += 1

            # Else we need to use mainfreight
            else:
                # Add cost of mainfreight truck to total
                total_cost[s] += 1200
        
        print(f"{s}: {total_cost[s]}") # print for each simulation for sanity


    if saturday:
        np.savetxt("obj_cost_simulation_sat.csv", total_cost, delimiter=",", fmt='%s')
    if not saturday:
        np.savetxt("obj_cost_simulation.csv", total_cost, delimiter=",", fmt='%s')
    return total_cost

def plot_simulateCost(n, saturday = False):

    if saturday:
        costs = pd.read_csv('obj_cost_simulation_sat.csv')
        string = "Saturday"
    if not saturday:
        costs = pd.read_csv('obj_cost_simulation.csv')
        string = "weekday"

    # Plot a histogram
    costs = costs.values.tolist()
    total_cost = [0] * len(costs)
    for i in range(len(costs)):
        total_cost[i] = costs[i][0]
    total_cost.sort()

    conf_index = int(np.ceil(0.025*n))  # 5% significance level
    confint_values = [total_cost[conf_index],total_cost[-conf_index]] 
    y = np.linspace(0,110,1000)
    x1 = [confint_values[0]] * len(y)
    x2 = [confint_values[1]] * len(y)
    total_cost = pd.Series(total_cost)
    total_cost.plot.hist(grid=True, bins=100, rwidth=0.9, color='#607c8e')
    plt.title(f'Objective Costs for {n} Simulations for {string}')
    plt.xlabel('Objective Cost')
    plt.ylabel('Count')
    plt.grid(axis='y', alpha=0.75)
    plt.plot(x1,y,color='red',linewidth=2)
    if saturday: plt.ylim(top=45)
    plt.plot(x2,y,color='red',linewidth=2)
    plt.ylim(0,45)
    plt.show()

if __name__ == "__main__":
    # Run this to simulate - will overwrite existing simulation!!
    #total_cost = simulateCost(n = 500, saturday = True)

    # Only run this to produce simulation plot from existing simulation
    plot_simulateCost(500,saturday=True)