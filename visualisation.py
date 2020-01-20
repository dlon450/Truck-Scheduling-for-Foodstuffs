"""
Group 16: Visualisation functions.
Author: Nicholas Whitlock
"""

import numpy as np
import pandas as pd
import folium
import openrouteservice as ors
from pulp import *
from importData import *
from RoutesFunctions import *
from GraphObjects import *
from LPFormulation import *

def ORSroutes(LProutes):
    '''
    Returns a list of all the routes required to visualise our plots
    Parameters
    ----------
    LProutes - list of routes used by the LP
    Returns
    LPsol - Information from the LP, including which routes were chosen
    --------
    routes - List ORS data of routes used by the LP
    '''
    ORSkey = '5b3ce3597851110001cf624838bf1bf2c9084e03a6a1346c10b3c128'
    client = ors.Client(key=ORSkey)
    nodes = getNodes('all')
    locations = pd.read_csv("FoodstuffLocations.csv")
    coords = locations[['Long', 'Lat']]
    coords = coords.values
    
    #Initialise list of ORSroutes
    routes = []
    for r in LProutes:
        nodecords = []
        for node in r.nodes:
            nodecords.append([node.Long,node.Lat])
        nodecords = tuple(map(tuple, nodecords))
        route = client.directions(coordinates = nodecords, profile ='driving-hgv', format='geojson', validate = False)
        routes.append(route)
    
    return routes

def visualise(solve = False, saturday = False):
    '''
    Visualises the chosen routes for the LP model
    Parameters
    ----------
    saturday: BOOL
        whether to visualise saturday or weekday
    solve: BOOL
        whether or not to resolve LP
    Returns
    --------
    '''
    areas = ['north', 'south', 'central', 'west']
    if solve:
        if not saturday:
            LProutes = LpSolve() 
            np.save('WeekdayLP', LProutes)
        if saturday:
            LProutes = LpSolve(False, True)
            np.save('SaturdayLP', LProutes)
    else:
        if not saturday:
            LProutes = np.load('WeekdayLP.npy')
        if saturday:
            LProutes = np.load('SaturdayLP.npy')
    #Get formatted routes for mapping
    routes = ORSroutes(LProutes)
    locations = pd.read_csv("FoodstuffLocations.csv")
    coords = locations[['Long', 'Lat']]
    coords = coords.values

    colors = ['#000000', '#FF33FF', '#FFFF99', '#00B3E6', 
		  '#E6B333', '#3366E6', '#999966', '#99FF99', '#B34D4D',
		  '#80B300', '#809900', '#E6B3B3', '#6680B3', '#66991A', 
		  '#FF99E6', '#CCFF1A', '#FF1A66', '#E6331A', '#33FFCC',
		  '#66994D', '#B366CC', '#4D8000', '#B33300', '#CC80CC', 
		  '#66664D', '#991AFF', '#E666FF', '#4DB3FF', '#1AB399',
		  '#E666B3', '#33991A', '#CC9999', '#B3B31A', '#00E680', 
		  '#4D8066', '#809980', '#E6FF80', '#1AFF33', '#999933',
		  '#FF3380', '#CCCC00', '#66E64D', '#4D80CC', '#9900B3', 
		  '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF']
    
    #initialise maps
    m = folium.Map(location = [-36.912146, 174.713481],  zoom_start=14,)
    mFStuffs = folium.Map(location = [-36.912146, 174.713481],  zoom_start=14,)
    mLeased = folium.Map(location = [-36.912146, 174.713481],  zoom_start=14,)
    abstract = folium.Map(location = [-36.912146, 174.713481],  zoom_start=14,)

    for map in [m, mFStuffs, mLeased, abstract]:
        #map locations
        folium.Marker(location = list(reversed(coords[0])), popup = locations.Supermarket[0], icon = folium.Icon(color='black')).add_to(map)
        for i in range(1, len(coords)):
            if locations.Type[i] == "New World":
                iconCol = "blue"
            elif locations.Type[i] == "Pak 'n Save":
                iconCol = "yellow"
            elif locations.Type[i] == "Fresh Collective":
                iconCol = "purple"
            else:
                iconCol = "green"
            folium.Marker(list(reversed(coords[i])), popup = locations.Supermarket[i], icon = folium.Icon(color = iconCol)).add_to(map)
        
        #Change Tile type
        folium.TileLayer('cartodbpositron').add_to(map) 

    #map routes
    for i in range(0, len(routes)):
        color = colors[i+1]
        if LProutes[i].wetleased == True:
            color = colors[0]
            #MainFreight Trucks map only
            routeinfo = ("Cost = $%.2f <br> Pallets Delivered = %d <br> Wetleased = %r" % (LProutes[i].route_cost(not saturday), LProutes[i].get_total_pallets(not saturday), LProutes[i].wetleased)) 
            folium.PolyLine(locations = [list(reversed(coord))for coord in routes[i]['features'][0]['geometry']['coordinates']], tooltip=routeinfo, color = colors[len(colors)-i]).add_to(mLeased)
        
        if LProutes[i].wetleased == False:
            routeinfo = ("Cost = $%.2f <br> Pallets Delivered = %d <br> Wetleased = %r" % (LProutes[i].route_cost(not saturday), LProutes[i].get_total_pallets(not saturday), LProutes[i].wetleased)) 
            folium.PolyLine(locations = [list(reversed(coord))for coord in routes[i]['features'][0]['geometry']['coordinates']], tooltip=routeinfo, color = colors[len(colors)-i-1]).add_to(mFStuffs)
        
        routeinfo = ("Cost = $%.2f <br> Pallets Delivered = %d <br> Wetleased = %r" % (LProutes[i].route_cost(not saturday), LProutes[i].get_total_pallets(not saturday), LProutes[i].wetleased)) 
        folium.PolyLine(locations = [list(reversed(coord))for coord in routes[i]['features'][0]['geometry']['coordinates']], tooltip=routeinfo, color = color).add_to(m)

    

    if not saturday:  
            m.save("WeekdayVisualMap.html")
            mLeased.save("WeekdayWetleasedMap.html")
            mFStuffs.save("WeekdayTrucksMap.html")
    if saturday:
            m.save("SaturdayVisualMap.html")
            mLeased.save("SaurdayWetleasedMap.html")
            mFStuffs.save("SaurdayTrucksMap.html")

    #AbstractMap
    
    for i in range(0, len(LProutes)):
        color = colors[i+1]
        if LProutes[i].wetleased == True:
            color = colors[0]
        coord = [0,0]
        coords = []
        for j in range(0, len(LProutes[i].nodes)):
            coord[1] = LProutes[i].nodes[j].Long
            coord[0] = LProutes[i].nodes[j].Lat
            newcoord = coord[:]
            coords.append(newcoord)
        routeinfo = ("Cost = $%.2f <br> Pallets Delivered = %d <br> Wetleased = %r" % (LProutes[i].route_cost(not saturday), LProutes[i].get_total_pallets(not saturday), LProutes[i].wetleased)) 
        folium.PolyLine(locations = [list(coord)for coord in coords], tooltip=routeinfo, color = color).add_to(abstract)
    
    if not saturday:          
        abstract.save("abstractWeekdays.html")

    if saturday:
        abstract.save("abstractSaturday.html")
    
    return LProutes


if __name__ == "__main__":
    Week = visualise(False,False)
    Week
    Sat = visualise(False,True)
    Sat