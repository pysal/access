import numpy as np
import numpy.ma as ma
import pandas as pd
import math
def makeAssignmentMatrix(tractPops, travel, tracts, docs): 

  assignment = np.zeros((len(tracts),len(tracts))) #Create assignment matrix

  supMask = ma.masked_values(docs,0) # Make mask for all no-doctor locations
  timeMask= ma.masked_array(travel, np.isnan(travel)) #make mask for all missing travel data 
  mask = np.logical_or(supMask.mask,timeMask.mask) # Create masked value if one or the other is masked

  travelMask = ma.masked_array(travel, mask=mask)
  # Put all ppl in lowest time location with doctor
  
  lowestTime = np.zeros((len(tracts),len(tracts)))
  lowestTime[np.arange(len(lowestTime)), travelMask.argmin(axis=1)] = 1

  assignment = (tractPops)*lowestTime 
  assignment = ma.masked_array(assignment, mask=mask)

  return assignment, tracts, travelMask, supMask


def numpyRaam(assignment, travelCost, docs, tracts, rho, tau):

  raamMatrix = np.zeros((len(tracts),len(tracts))) #Create raam matrix

  demand = assignment.sum(axis=0) # Get number of ppl going to each doctor location

  demandCost = demand/(docs*rho) #Congestion cost

  raamMatrix = demandCost + travelCost

  return raamMatrix, demand, travelCost

def numpyMaxMin(raamMatrix, assignment):

  #Find min
  minPos = raamMatrix.argmin(axis=1)

  # Find max which has ppl to move
  maxPos = ma.masked_array(raamMatrix, assignment == 0).argmax(axis = 1)

  return minPos, maxPos


def numpyMove(assignment,minPos,maxPos,quantity):

  #Remove from max and put to min
  assignment[np.arange(len(assignment)), maxPos] -= np.int32(quantity)
  assignment[np.arange(len(assignment)), minPos] += np.int32(quantity)
  return assignment


def numpyFindMovers(assignment, supply, tracts, minPos, maxPos, travel, demand, maxShift, rho, tau):

  movers = np.int32(np.zeros(shape=(len(tracts),3))) # Create movers matrix
  movers[:, 0] = maxShift #add in max shift
  movers[:, 1] = assignment[np.arange(len(assignment)), maxPos] # add in populations

  #Calculate people necessary to equilibrate
  notMe = demand - assignment

  drTot = assignment[np.arange(len(assignment)),maxPos] + assignment[np.arange(len(assignment)),minPos]


  #Each of these is one 'piece' of the equation to calculate drlmin. 
  p1 = (supply[minPos]*supply[maxPos])/(supply[minPos] +supply[maxPos])
  p2 = ((travel[np.arange(len(travel)),maxPos]) - (travel[np.arange(len(travel)),minPos]))*(rho/tau)
  p3 = ((drTot + notMe[np.arange(len(notMe)), maxPos])/supply[maxPos])
  p4 = (notMe[np.arange(len(notMe)), minPos]/supply[minPos])

  drlmin = p1*(p2+p3-p4)

  drlmininit = assignment[np.arange(len(assignment)),minPos]

  delta = drlmin - drlmininit

  delta[delta< 0] = 0 #When maxpos=minpos the value is negative

  # add in that 
  movers[:, 2] = delta

  minMovers = movers.min(axis=1)

  #Find number moving to each tract
  trackMove = pd.DataFrame([minMovers, tracts[minPos]]).transpose()
  trackMove.columns = ['movers', 'tract']
  arrivals = trackMove.groupby('tract').sum()
  arrivals.reset_index(level=0, inplace=True)
  #Find max movers allowed per tract

  tenth_sup = pd.DataFrame([supply[minPos]*(rho/10), tracts]).transpose()
  tenth_sup.columns = ['maxArrivals', 'tract']

  both = tenth_sup.merge(arrivals)

  both.movers = 527

  both = both.drop(both.loc[both.movers < both.maxArrivals].index)


  indeces = both.tract
  trackMove['newMovers'] = 0
  for index in indeces:
      new = trackMove['movers'][trackMove.tract == index].apply(lambda x: x*(both['maxArrivals'][both.tract==index]/both['movers'][both.tract==index]))
              
      trackMove = trackMove.join(new)
      trackMove.columns = ['movers','tract','newMovers','temp']
      trackMove['newMovers'] = trackMove['newMovers'] + trackMove['temp'].fillna(0)
      trackMove = trackMove[['movers','tract','newMovers']]


  trackMove['newMovers'] = np.where(trackMove['newMovers'] == 0, trackMove['movers'], trackMove['newMovers'])

  minMovers = np.array(trackMove['movers'])


  return minMovers, delta

def decay(number,i,decay = 100):
  # set decay
  number = number*.5**(i/decay)
  if number < 2:
      number = 2
  return (int(number))


def optimizationCycle(tractPops,travel,rho,tau,maxShift, tracts, docs, cycles = 150):
  startShift = maxShift
  tracts = np.array(tracts)
  quantity = [2]
  assignment, tracts, travelMatrix, supply = makeAssignmentMatrix(tractPops, travel, tracts, docs)
  travelCost = ((travelMatrix)/tau)

  #Performs iterations and movements
  print("Original start: ")

  print(assignment)
  i = 0
  #Loop around assignment matrix and move people around
  while max(quantity) > 1:
      raamMatrix, demand, travelCost = numpyRaam(assignment,travelCost,docs,tracts,rho,tau)
      #print("Raam: " + str(raamMatrix))
      #print("Demand: " + str(demand))
      minPos,maxPos = numpyMaxMin(raamMatrix, assignment)
      #print("min: " + str(minPos))
      #print("max: " + str(maxPos))
      quantity, needToEqualize = numpyFindMovers(assignment, supply, tracts, minPos, maxPos, travelMatrix, demand, maxShift, rho, tau)
      #print("Moved: " + str(quantity))
      #print("To equalize: " + str(needToEqualize))
      assignment = numpyMove(assignment,minPos,maxPos,quantity)
      #print("Assignment: "+ str(assignment))
      i +=1
      maxShift = decay(startShift,i)
      if i > cycles:
          break 
      
      print("The amount of cycles is: {0}. The mean amount of people moved is: {1}. The mean amount necessary to equalize is {2}\r".format(i,quantity.mean(),needToEqualize.mean()), end='')

  print("\n")


  traveled = (travelCost*assignment)/assignment
  finalRaam = (raamMatrix*assignment)/assignment
  demandForTract = finalRaam.mean(axis=1) - traveled.mean(axis=1)
  travelData = np.array([traveled.mean(axis=1),tracts])
  demandData = np.array([demandForTract, tracts])


  return assignment, finalRaam, demandData, travelData
def raam(demand_df, supply_df, cost_df,
         demand_origin = "geoid", demand_name   = "demand",
         supply_origin = "geoid",   supply_name   = "supply",
         cost_origin   = "origin", cost_dest     = "dest", cost_name = "cost",
         tau = 1, max_cost = None, weight_fn = None):
  """
  Calculate the rational agent access model's total cost -- 
    a weighted travel and congestion cost.
  The balance of the two costs is expressed by the
    $\tau$ parameter, which corresponds to the travel time 
    required to accept of congestion by 100% of the mean demand to supply ratio
    in the study area.

  Parameters
  ----------

  demand_df     : [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
                  The origins dataframe, containing a location index and a total demand.
  demand_origin : str
                  is the name of the column of `demand` that holds the origin ID.
  demand_value  : str
                  is the name of the column of `demand` that holds the aggregate demand at a location.
  supply_df     : [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
                  The origins dataframe, containing a location index and level of supply
  cost_df       : [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
                  This dataframe contains a link between neighboring demand locations, and a cost between them.
  cost_origin   : str
                  The column name of the locations of users or consumers.
  cost_dest     : str
                  The column name of the supply or resource locations.
  cost_name     : str
                  The column name of the travel cost between origins and destinations
  weight_fn  : function
                This fucntion will weight the value of resources/facilities,
                as a function of the raw cost.
  max_cost   : float
                This is the maximum cost to consider in the weighted sum;
                  note that it applies _along with_ the weight function.
  max_cost   : float
                This is the maximum cost to consider in the weighted sum;
                  note that it applies _along with_ the weight function.

  Returns
  -------
  access     : pandas.Series
      
                A -- potentially-weighted -- Rational Agent Access Model cost.
  """
  cost_df = cost_df.pivot(index=cost_origin, columns=cost_dest, values=cost_name)
  tracts = cost_df.index.values.tolist()
  travel = cost_df.to_sparse()
  travel = travel.to_numpy()

  supply_df = supply_df.drop(supply_df.loc[~supply_df[supply_origin].isin(tracts)].index)
  supply_df['destination'] = supply_df[supply_origin]
  docs = np.array(supply_df[supply_name].values.tolist())

  demand_df = demand_df.drop(demand_df.loc[~demand_df[demand_origin].isin(tracts)].index)
  demand_df['destination'] = demand_df[demand_origin]
  demand_df = demand_df.pivot(index=demand_origin,columns='destination',values=demand_name)
  demand_df.fillna(method='ffill', inplace=True)
  demand_df.fillna(method='bfill', inplace=True)
  demand_df = demand_df.transpose()
  demand_df = demand_df.to_sparse()
  tractPops = demand_df.to_numpy()

  rho = 1315
  tau = 60
  maxShift = 50
  assignment, raamMatrix, demandCost, travelCost = optimizationCycle(tractPops,travel,rho,tau,maxShift,tracts,docs,150)

  data = pd.DataFrame([tracts,raamMatrix.mean(axis=1),demandCost,travelCost]).transpose()

  return data



