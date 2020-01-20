import numpy as np
import pandas as pd

def importAllData():
    ''' 
    Returns Demands of each supermarket and the dates of each demand

    Returns
    -------
    Data: reshaped-dataframe
    with demands of each supermarket and the dates of each demand

    '''
    #import and reshape the data
    df = pd.read_csv('demandData.csv')
    Data = pd.melt(df,id_vars=['Supermarket','Type of Supermarket'], var_name='date', value_name='demand')
    #create a weekdays column
    Data.loc[:,'date'] = pd.to_datetime(Data['date'], format='%d/%m/%Y')
    Data['weekdays'] = Data.loc[:,'date'].dt.weekday_name
    #create a day type column
    conditions = [(Data['weekdays'] == 'Saturday'),(Data['weekdays'] == 'Sunday'),]
    choices = ['Saturday', 'Sunday']
    Data['dayType'] = np.select(conditions, choices, default='Weekday')

    return Data

def importDemandData(area):
    ''' 
    Returns Demands of each supermarket and the dates of each demand

    Parameters
    ----------
    area: string
        name of area to get nodes from

    Returns
    -------
    DemandData : reshaped-dataframe
    with demands of each supermarket and the days of each demand

    '''
    string = area + '.csv'
    DemandData = pd.read_csv(string)
    return DemandData

def importFoodstuffLocations():
    ''' 
    Returns Foodstuff Location data of warehouses and supermarkets along with their types

    Returns
    -------

    
    '''
    return pd.read_csv('FoodstuffLocations.csv')

def importFoodstuffDistances():
    ''' 
    Returns Foodstuff Distances between  warehouses and supermarkets

    Returns
    -------

    
    '''
    #import data
    df = pd.read_csv('FoodstuffDistances.csv')
    #reshape data
    td = pd.melt(df,id_vars=['Unnamed: 0'], var_name='to', value_name='Distances')
    td = td.rename(columns = {'Unnamed: 0':'from'})
    return td

def importFoodstuffTravelTimes():
    ''' 
    Returns Foodstuff Travel Times between  warehouses and supermarkets

    Returns
    -------

    
    '''
    #import data
    df = pd.read_csv('FoodstuffTravelTimes.csv')
    #reshape data
    tt = pd.melt(df,id_vars=['Unnamed: 0'], var_name='to', value_name='TravelTimes')
    tt = tt.rename(columns = {'Unnamed: 0':'from'})

    return tt

if __name__ == "__main__":
    #data = importAllData()
    demands = importDemandData('all')
    #locs = importFoodstuffLocations()
    arcData = importFoodstuffTravelTimes()
    #b = importFoodstuffDistances()

    nodes = getNodes('central')
    #print(nodes)
    arcs = getArcs(arcData, 'central')
    print(arcs)
    