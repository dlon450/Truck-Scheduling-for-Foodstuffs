'''
Group 16: Graph object classes.
Author: Karl Zhu
'''

import numpy as np
import pandas as pd
import random

class Node(object):
    '''
    Node object used to represent supermarket.
    '''
    def __init__(self):
        self.name = None # name of the store
        self.weekday = 0 # median weekday pallets
        self.saturday = 0 # median saturday pallets
        self.visited = False # used in getRoutes()
        self.wd_prob = None # weekday probabilities 
        self.Lat = None
        self.Long = None
        self.area = None

    def __repr__(self):
        return "nd: {}".format(self.name)

    def get_pallets(self, weekday = True):
        if weekday:
            return self.weekday
        return self.saturday

class Arc(object):
    '''
    Arc object used to represent the travel between two supermarkets.
    '''
    def __init__(self):
        self.weight = None # time of travel
        self.to_node = None
        self.from_node = None

    def __repr__(self):
        if self.to_node is None:
            to_nd = 'None'
        else:
            to_nd = self.to_node.name
        if self.from_node is None:
            from_nd = 'None'
        else:
            from_nd = self.from_node.name
        return "arc: {}->{}".format(from_nd, to_nd)

    def get_time(self):
        return self.weight

class Route(object):
    '''
    Route object used to represent the trucking routes considered in the LP formulation
    '''
    def __init__(self):
        self.nodes = []
        self.arcs = []
        self.wetleased = False
        self.shift = 1 # Morning shift by default

    def __repr__(self):
        name = 'route: Warehouse'
        for node in self.nodes[1:]:
            name = name + ' -> ' + node.name
        return name

    def get_total_pallets(self, weekday = True):
        '''
        Total pallets demanded by the route.
        Note : Weekday and Saturday have different demands. 
        '''
        total_pallets = 0
        for node in self.nodes:
            total_pallets += node.get_pallets(weekday)
        return total_pallets

    def get_total_time(self, weekday = True):
        '''
        Total estimated travel and unloading time of the route.
        '''
        total_time = 0
        
        # travel time
        for arc in self.arcs:
            total_time += arc.get_time()

        # pallet unloading time
        total_time += 300 * self.get_total_pallets(weekday)

        return total_time # in seconds

    def time_with_traffic(self):
        '''
        Get the time of a specific route with traffic conditions.
        Parameters
        ----------
        route: 
            route to retrieve time from.
        shift: int
            1 if shift of route starts in morning, 2 if shift of route starts in afternoon
        Returns
        --------
            time: int
                time taken to traverse route (in seconds)
        '''
        # Initialise time taken and traffic multipliers
        time = 0

        # Get the route time without traffic
        route_current_time = self.get_total_time()

        # Check if route is in the morning shift
        if self.shift == 1:
            
            # Set the multipliers for each hour
            m1 = random.uniform(1.8,2.2) # multiplier is around 2.0 during 8 to 9am
            m2 = random.uniform(0.9,1.1) # multiplier around 1.0 during 9 to 10am
            m3 = random.uniform(0.72,0.88) # multiplier around 0.8 during 10 to 11am
            m4 = random.uniform(0.9,1.1) # multiplier around 1.0 during 11am to 12pm

            # Check how long the route takes and change multiplier
            if route_current_time <= 3600:    
                time += route_current_time * m1

            elif route_current_time <= 2*3600 and route_current_time > 3600: 
                time += m1*3600 + (route_current_time - 3600) * m2

            elif route_current_time <= 3*3600 and route_current_time > 2*3600: 
                time += m1*3600 + m2*3600 + (route_current_time - 2*3600) * m3

            elif route_current_time <= 4*3600 and route_current_time > 3*3600: 
                time += m1*3600 + m2*3600 + m3*3600 + (route_current_time - 3*3600) * m4

        # check if route is in the afternoon shift
        elif self.shift == 2:

            # Set multipliers for each hour
            m1 = random.uniform(0.99,1.21) # multiplier during 2-3
            m2 = random.uniform(1.25*0.9,1.25*1.1) # multiplier during 3-4
            m3 = random.uniform(1.75*0.9,1.75*1.1) # multiplier during 4-5
            m4 = random.uniform(2.25*0.9,2.25*1.1) # multiplier during 5-6

            # Check how long the route takes and change multiplier
            if route_current_time <= 3600: 
                time += route_current_time * m1
            elif route_current_time <= 2*3600 and route_current_time > 3600: 
                time += m1*3600 + (route_current_time - 3600) * m2
            elif route_current_time <= 3*3600 and route_current_time > 2*3600: 
                time += m1*3600 + m2*3600 + (route_current_time - 2*3600) * m3
            elif route_current_time <= 4*3600 and route_current_time > 3*3600: 
                time += m1*3600 + m2*3600 + m3*3600 + (route_current_time - 3*3600) * m4
        return time
        
    def route_cost(self, weekday= True, traffic = False):
        '''
        Estimated cost of performing the route.
        '''
        if traffic and weekday:
            if self.time_with_traffic() <= 4 * 3600:
                cost = 150 / 3600 * self.time_with_traffic() # $150/hr trucking cost
            else:
                cost = (self.time_with_traffic() - 4*3600)*200/3600 + 600   #$200/hr overtime trucking cost
            return cost
     
        else:
            if self.get_total_time(weekday) <= 4 * 3600:
                cost = 150 / 3600 * self.get_total_time(weekday) # $150/hr trucking cost
            else:
                cost = (self.get_total_time(weekday) - 4*3600)*200/3600 + 600   #$200/hr overtime trucking cost
            return cost

    def add_node(self, node):
        '''Adds a Node object to the Route object
        '''
        self.nodes.append(node)

    def add_arc(self, arc):
        '''Adds an Arc object to the Route object
        '''
        self.arcs.append(arc)		