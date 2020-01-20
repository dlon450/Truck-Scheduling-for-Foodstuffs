import numpy as np
import pandas as pd

# Copied the classes from the 233 Dijkstra's lab, so the naming is from that labs

class Node(object):
    def __init__(self):
        self.name = None # name of the store
        self.value = None # number of pallets
        self.weekday = None # median weekday pallets
        self.saturday = None # median saturday pallets
        self.visited = False
        # not sure if this is needed:
        self.arcs_in = []
        self.arcs_out = []
        #self.location = [] # in the form [lat,long]

    def __repr__(self):
        return "nd: {}".format(self.name)

    def get_pallets(self, weekday = True):
        if weekday:
            return self.weekday
        return self.saturday



class Arc(object):
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
    def __init__(self):
        self.nodes = []
        self.arcs = []
    def __repr__(self):
        name = 'route: Warehouse'
        for node in self.nodes:
            name = name + ' -> ' + node.name
        return name
    def get_total_pallets(self, weekday = True):
        total_pallets = 0
        for node in self.nodes:
            total_pallets += node.get_pallets(weekday)
        return total_pallets
    def get_total_time(self, weekday = True):
        total_time = 0

        # travel time
        for arc in self.arcs:
            total_time += arc.get_time()

        # pallet unloading time
        total_time += 300 * self.get_total_pallets(weekday)

        return total_time # in seconds

    def route_cost(self, weekday= True):

        if self.get_total_time(weekday) <= 4 * 3600:
            cost = 150 / 3600 * self.get_total_time(weekday)
        else:
            cost = (self.get_total_time(weekday) - 4*3600)*200/3600 + 600

        return cost

    def add_node(self, node):
        '''Adds a Node with NAME and VALUE to the route.

            Parameters:
            -----------
            node : node
                node to add


            Notes:
            ------
            Examples of what the value parameter can represent are locations, ratings etc.
        '''

        # append node to the list of nodes
        self.nodes.append(node)

    def add_arc(self, arc):
        '''Adds a arc with tonode and fromnode and weight to the route.

            Parameters:
            -----------
            arc : arc
                arc to add


            Notes:
            ------
            Examples of what the value parameter can represent are locations, ratings etc.
        '''

        # append arc to the list of arcs
        self.arcs.append(arc)		



# class Route(object):
#     def __init__(self):
#         self.nodes = []
#         self.arcs = []

#     def get_total_pallets(self):
#         total_pallets = 0
#         for node in self.nodes:
#             total_pallets += node.get_pallets()

#         return total_pallets

#     def get_total_time(self):
#         total_time = 0
#         for arc in self.arcs:
#             total_time += arc.get_time()

#         return total_time

#     def get_nodes(self):
#         return self.nodes

#     def get_arcs(self):
#         return self.arcs

#         # Append arc info to affected nodes
#         node_from.arcs_out.append(arc)
#         node_to.arcs_in.append(arc)

#         # Append arc info to network
#         self.arcs.append(arc)

        
#     def read_network(self, filename):
#         '''Read data from FILENAME and construct the network.
        
#             Each line of FILENAME contains
#              - the name of an origin node (first entry)
#              - and destination;weight pairs (each pair separated by a comma)
             
#         '''

#         fp = open(filename, 'r')

#         # get first line (a string)
#         ln = fp.readline().strip()
#         while ln is not '':        # keep looping to the end of the file
#             # divide the string using the split() method for strings
#             split_line = ln.split(",")
#             # - extract the source node
#             from_node_name = split_line[0]
#             # - extract the remaining arcs
#             arcs = split_line[1:]

#             # YOU WILL NEED TO THINK CAREFULLY ABOUT WHAT THIS TRY/EXCEPT BLOCK DOES
#             # if node doesn't exist, add to network
#             try:
#                 # the output is a node object, the input is a string
#                 # this command raises an ERROR if the node DOESN'T exist
#                 from_node = self.get_node(from_node_name)           
#             except NetworkError:
#                 # this command gets executed if an error is raised above
#                 self.add_node(from_node_name)
                
#             # get the source node OBJECT, using the source node STRING
#             from_node = self.get_node(from_node_name)
                
#             # read the arc information and add it to network
#             for arc in arcs:
#                 # parse arc information
#                 [to_node_name, weight] = arc.split(";")
#                 try:
#                     # the output is a node object, the input is a string
#                     # this command raises an ERROR if the node DOESN'T exist
#                     to_node = self.get_node(to_node_name)           
#                 except NetworkError:
#                     # this command gets executed if an error is raised above
#                     self.add_node(to_node_name)
                
#                 # get destination node object and link it to source node
#                 to_node = self.get_node(to_node_name)
#                 self.join_nodes(from_node,to_node,weight)

#             # get next line
#             ln = fp.readline()
        
