import folium
import pandas as pd
import matplotlib.pyplot as plt
from GraphObjects import*
from importData import*

#Global Variables
#5b3ce3597851110001cf624838bf1bf2c9084e03a6a1346c10b3c128
ORSkey = '5b3ce3597851110001cf624838bf1bf2c9084e03a6a1346c10b3c128'
locations = pd.read_csv("FoodstuffLocations.csv")

def LocationsMap():
    ''' 
    Creates a map of all the supermarkets and the warehouse and saves it to HTML file

    Returns
    -------
    HTML file called locationmap
    '''
    coords = locations[['Long', 'Lat']]
    coords = coords.values

    m = folium.Map(location = list(reversed(coords[0])), zoom_start=10)

    folium.Marker(location = list(reversed(coords[0])), popup = locations.Supermarket[0], icon = folium.Icon(color='black')).add_to(m)

    for i in range(1, len(coords)):
        if locations.Type[i] == "New World":
            iconCol = "blue"
        elif locations.Type[i] == "Pak 'n Save":
            iconCol = "yellow"
        elif locations.Type[i] == "Fresh Collective":
            iconCol = "purple"
        else:
            iconCol = "green"
        folium.Marker(list(reversed(coords[i])), popup = locations.Supermarket[i], icon = folium.Icon(color = iconCol)).add_to(m)

    m.save("locationmap.html")

def getNodes(area):
    ''' 
    Finds a list of possible nodes for trucks to go through

    Parameters
    ----------
    area: string
        name of area to get nodes from

    RETURNS
    -------
    nodes: set of possible nodes
    '''
    demands = importDemandData(area)
    row, col = demands.shape        # get number of rows and columns from demands
    warehouse_node = Node()
    warehouse_node.name = "Warehouse"  
    warehouse_node.saturday = 0
    warehouse_node.weekday = 0   
    nodes = [warehouse_node]+[0]*row                 # initialise set of nodes    

    # add each node to nodes
    for i in range(row):
        node = Node()
        node.name = demands.iloc[i][0]      # retrieve name
        node.weekday = demands.iloc[i][2]   # retrieve median weekday pallets
        node.saturday = demands.iloc[i][3]  # retrieve median saturday pallets
        nodes[i+1] = node

    # we should add the node.area attribute either on the for loop above, or below using Lat-Long.
    # we can then use that area attribute to group the nodes into one route if they're in the same area.

    locations = pd.read_csv("FoodstuffLocations.csv")
    for i in range(0, len(locations)):
        for node in nodes:
            if locations['Supermarket'][i] == node.name:
                node.Lat = locations['Lat'][i]
                node.Long = locations['Long'][i]

    return nodes

def getArcs(arcData, area):
    ''' 
    Finds a list of possible arcs for trucks to take between notes
    RETURNS
    -------
        arcs: list of possible arcs
    '''
    nodes = getNodes(area)
    row, col = arcData.shape        # get number of rows and columns from demands     
    arcs = []                  # initialise set of arcs   

    # add each arc to arcs
    for i in range(row):
        arc = Arc()
        arc.weight = arcData.iloc[i][2]         # retrieve weight
        to_node_name = arcData.iloc[i][1]        # retrieve to_node name
        from_node_name = arcData.iloc[i][0]      # retrieve from_node name

        for node in nodes:
            if node.name == to_node_name:
                arc.to_node = node
            if node.name == from_node_name:
                arc.from_node = node

        if (arc.from_node != None) & (arc.to_node  != None):
            arcs.append(arc)

    return arcs

def isValid(route, arcs, saturday = False):
    '''
    Verifies if the route satisfies the given constraints.

    Returns True if Route is satisfactory.

    Note: Max pallets is 12 per truck as given.
    '''
    
    # Pallet constraint
    maxPallet = 12    
    sumPallets = 0

    if not saturday:  
        for j in route: #calculate total pallets of current route
            sumPallets += j.weekday
            if sumPallets > maxPallet:
                return False

    if saturday:
        for j in route: #calculate total pallets of current route
            sumPallets += j.saturday
            if sumPallets > maxPallet:
                return False
            if len(route) > 4:
                return False
    return True

def findAllRoutes(nodes, arcs, currentNode, destinationNode, visited, route, routes, saturday = False): 
    '''
    Recursive helper function to find all paths from warehouse to warehouse
    visited[] keeps track of vertices in current route. 
    route[] stores actual vertices and path_index is current index in route[]
    
    Returns
    ---------
        routes: array or viable routes
    '''
    # Mark the current node as visited and store in path 
    currentNode.visited= True
    route.append(currentNode)    

    # If current node is same as destination, then append current route to list of routes
    if route[-1] == destinationNode: 
        newRoute = route[:] #shallow copy of route
        newRoute.insert(0, destinationNode)
        r = Route()
        r.add_node(newRoute[0])
        for n in range(1, len(newRoute)):
            r.add_node(newRoute[n])
            for arc in arcs:
                if (arc.from_node.name == newRoute[n-1].name) & (arc.to_node.name == newRoute[n].name):
                    r.add_arc(arc)
        routes.append(r)

    else: 
        # If current node is not destination 
        #Recur for all the nodes adjacent to this node 
        
        for i in range(0,len(nodes)): 
            if isValid(route, arcs, saturday):
                if visited[i].visited==False: 
                    routes = findAllRoutes(nodes, arcs, visited[i], destinationNode, visited, route, routes, saturday)

    # Remove current node from route[] and mark it as unvisited 
    route.pop() 
    currentNode.visited= False

    return routes

def getRoutes(areas, solve = True, saturday = False): 
    '''
    Gets all routes from origin to destination (in this case warehouse to warehouse)
    Parameters
    ----------
    areas: list
        names of areas to get nodes from
    solve: BOOL
        whether or not to resolve routes
    Returns
    --------
        routes: array-like
            array of feasible routes
    '''
    if solve:
        
        # Create an array to store routes 
        routes = [] 
        for area in areas:
            #get all nodes
            nodes = getNodes(area)
            # Mark all the vertices as not visited 
            visited = nodes #false by default

            #get all arcs
            arcs = getArcs(importFoodstuffTravelTimes(), area)

            #Set destination and origin
            originNode = nodes[1] #First node that is not warehouse - will add warehouse as origin node later
            destinationNode = nodes[0] #Last node is warehouse
            
            # Call the recursive helper function to print all paths  
            for originNode in nodes[1:]:
                # Create an array to store routes 
                routesBase = [] 
                
                # Create an array to store nodes 
                route = []
            
                routes = routes + findAllRoutes(nodes, arcs, originNode, destinationNode, visited, route, routesBase, saturday)
        
        if not saturday:  
            np.save('WeekdayRoutesFile.npy', routes)
        if saturday:
            np.save('SaturdayRoutesFile.npy', routes)
        return routes
    else:
        if not saturday:  
            routes = np.load('WeekdayRoutesFile.npy')
        if saturday:
            routes = np.load('SaturdayRoutesFile.npy')
        return routes

def routes_from_nodes(nodes, area = 'all', saturday = False):
    '''
    Gets all routes from origin to destination (in this case warehouse to warehouse)
    Parameters
    ----------
    areas: list
        names of areas to get nodes from
    solve: BOOL
        whether or not to resolve routes
    Returns
    --------
        routes: array-like
            array of feasible routes
    '''
    routes = []
    # Mark all the vertices as not visited 
    visited = nodes #false by default

    #get all arcs
    arcs = getArcs(importFoodstuffTravelTimes(), area)

    #Set destination and origin
    originNode = nodes[1] #First node that is not warehouse - will add warehouse as origin node later
    destinationNode = nodes[0] #Last node is warehouse
    
    # Call the recursive helper function to print all paths  
    for originNode in nodes[1:]:
        # Create an array to store routes 
        routesBase = [] 
        
        # Create an array to store nodes 
        route = []
    
        routes = routes + findAllRoutes(nodes, arcs, originNode, destinationNode, visited, route, routesBase, saturday)
    return routes