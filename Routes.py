import folium
from ModelFunctions import*
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
                node.arcs_out
            if node.name == from_node_name:
                arc.from_node = node

        if (arc.from_node != None) & (arc.to_node  != None):
            arcs.append(arc)

    return arcs

def isValid(route, arcs, weekday = True):
    
    #Check constraints of route making
    sumPallets = 0
    sumTime = 0

    #Pallet Constraint
    if weekday:  
        for j in route: #calculate total pallets of current route
            sumPallets += j.weekday
            if sumPallets > 12:
                return False

    if not weekday:
        for j in route: #calculate total pallets of current route
            sumPallets += j.saturday
            if sumPallets > 12:
                return False
    return True

def findAllRoutes(nodes, arcs, currentNode, destinationNode, visited, route, routes, weekday = True): 
    '''
    Recursive helper function to find all paths from warehouse to warehouse
    visited[] keeps track of vertices in current route. 
    route[] stores actual vertices and path_index is current index in route[]
    
    RETURNS
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
            if isValid(route, arcs):
                if visited[i].visited==False: 
                    routes = findAllRoutes(nodes, arcs, visited[i], destinationNode, visited, route, routes, weekday)

    # Remove current node from route[] and mark it as unvisited 
    route.pop() 
    currentNode.visited= False

    return routes

 
def getRoutes(areas, solve = True, weekday = True): 
    '''
    Gets all routes from origin to destination (in this case warehouse to warehouse)
    Parameters
    ----------
    areas: list
        names of areas to get nodes from
    solve: BOOL
        whether or not to resolve routes
    RETURNS
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
            
                routes = routes + findAllRoutes(nodes, arcs, originNode, destinationNode, visited, route, routesBase, weekday)
            
        np.save('RoutesFile.npy', routes)
        return routes
    else:
        routes = np.load('RoutesFile.npy')
        return routes
        

def GetRoutesWeekday():
    ''' 
    Finds time taken for all the possible routes on weekdays
    RETURNS
    -------
        time: array of time taken for each route
    
    '''
    coords = locations[['Long', 'Lat']]
    coords = coords.values


if __name__ == "__main__":
    LocationsMap()
    # northroutes = getRoutes('north', True)
    # southroutes = getRoutes('south')
    # centralroutes = getRoutes('central')
    # westroutes = getRoutes('west')
    #allroutes = getRoutes('all')

    routes = getRoutes(['north', 'south', 'central', 'west'], True)
    routes


