import numpy as np
import pandas as pd
##import matplotlib.pyplot as plt
##import glob
import datetime
import sys
import json




input_from_server = sys.argv[1]
input_list_from_server = json.loads(input_from_server)
duration = int(input_list_from_server["duration"])
time = int(input_list_from_server["time"])
status = input_list_from_server["status"]["stations"]
information = input_list_from_server["information"]["stations"]






##filenames = glob.glob(r"C:\Users\Lord Rayleigh\Documents\Projects\PolyHack2018\201701-hubway-tripdata.csv")

t0 = 0
dt = 60*60*24
day = 0
monthnum = 1

d_times = np.empty(0)
d_locs = np.empty(0)
a_times = np.empty(0)
a_locs = np.empty(0)

daydict = {0:"monday", 1:"tuesday", 2:"wednesday", 3:"thursday", 4:"friday", 5:"saturday", 6:"sunday"}
seasondict = {1:"winter",2:"winter",3:"spring",4:"spring",5:"spring",6:"summer",7:"summer",8:"summer",9:"fall",10:"fall",11:"fall",12:"winter"}


#Remember to change path!!!!!!
filename_d = "HistoricData/"+seasondict[monthnum]+"/"+daydict[day]+'_dep.csv'
filename_a = "HistoricData/"+seasondict[monthnum]+"/"+daydict[day]+'_arr.csv'




data_d = np.genfromtxt(filename_d, delimiter=',', names=True)
data_a = np.genfromtxt(filename_a, delimiter=',', names=True)

d_times = np.append(d_times, data_d['starttime'])
d_locs = np.append(d_locs, data_d['start_station_id'])
d_locs_dict = dict(zip(d_locs, np.zeros(len(d_locs))))

neg_inds = np.where(d_times<0)[0]

#splitting by week markers
d_times_split = [np.split(d_times, neg_inds)[0]]+[x[1:] for x in np.split(d_times, neg_inds)[1:]]
d_locs_split = [np.split(d_locs, neg_inds)[0]]+[x[1:] for x in np.split(d_locs, neg_inds)[1:]]


a_times = np.append(a_times, data_a['stoptime'])
a_locs = np.append(a_locs, data_a['end_station_id'])
a_locs_dict = dict(zip(a_locs, np.zeros(len(a_locs))))

neg_inds = np.where(a_times<0)[0]

#splitting by week markers
a_times_split = [np.split(a_times, neg_inds)[0]]+[x[1:] for x in np.split(a_times, neg_inds)[1:]]
a_locs_split = [np.split(a_locs, neg_inds)[0]]+[x[1:] for x in np.split(a_locs, neg_inds)[1:]]



locs_tot = np.unique(np.concatenate((d_locs, a_locs)))[1:]
locs_tot_dict_d = dict(zip(locs_tot, [[] for i in range(len(locs_tot))]))
locs_tot_dict_a = dict(zip(locs_tot, [[] for i in range(len(locs_tot))]))



#Splitting up arrivals and departures by week

d_times_by_loc_by_week = np.zeros(len(d_times_split), dtype=object)
departures_in_range_by_loc_by_week = np.zeros(len(d_times_split), dtype=object)
for i in range(len(d_times_split)):
    #Splitting up departures by station

    d_locs_i = d_locs_split[i]
    d_times_i = d_times_split[i]
    
    idsort_d = np.argsort(d_locs_i)
    d_times_by_loc = np.split(d_times_i[idsort_d], np.array(np.where(np.diff(d_locs_i[idsort_d]))[0]+1,dtype=int))
    d_locs_i_unique = np.unique(d_locs_i)

    for j in range(len(d_locs_i_unique)):
        d_times_j = d_times_by_loc[j]
        departures_i_j = np.sum((t0<=d_times_j)&(d_times_j<=(t0+dt)))
        locs_tot_dict_d[d_locs_i_unique[j]].append(departures_i_j)




    
##
##    d_times_by_loc_by_week[i] = d_times_by_loc
##
##    departures_i_in_range_by_loc = np.zeros(len(d_times_by_loc))
##    for j in range(len(d_times_by_loc)):
##        d_times_j = d_times_by_loc[j]
##        departures_i_j = np.sum((t0<=d_times_j)&(d_times_j<=(t0+dt)))
##        departures_i_in_range_by_loc[j] = departures_i_j
##    departures_in_range_by_loc_by_week[i] = departures_i_in_range_by_loc
##








    
a_times_by_loc_by_week = np.zeros(len(a_times_split), dtype=object)
arrivals_in_range_by_loc_by_week = np.zeros(len(a_times_split), dtype=object)
for i in range(len(a_times_split)):
    #Splitting up arrivals by station

    a_locs_i = a_locs_split[i]
    a_times_i = a_times_split[i]
    
    idsort_a = np.argsort(a_locs_i)
    a_times_by_loc = np.split(a_times_i[idsort_a], np.array(np.where(np.diff(a_locs_i[idsort_a]))[0]+1,dtype=int))
    a_locs_i_unique = np.unique(a_locs_i)

    for j in range(len(a_locs_i_unique)):
        a_times_j = a_times_by_loc[j]
        arrivals_i_j = np.sum((t0<=a_times_j)&(a_times_j<=(t0+dt)))
        locs_tot_dict_a[a_locs_i_unique[j]].append(arrivals_i_j)


means = dict(locs_tot, np.zeros(len(locs_tot)))
variance = dict(locs_tot, np.zeros(len(locs_tot)))
chi_sq = dict(locs_tot, np.zeros(len(locs_tot)))
for i in range(len(locs_tot)):
    loc = locs_tot[i]
    a_s = locs_tot_dict_a[loc]
    d_s = locs_tot_dict_d[loc]

    a_mean = np.mean(a_s)
    d_mean = np.mean(d_s)

    flux_mean = a_mean-d_mean


    chisq_as = np.sum((a_s-a_mean)**2/a_mean)
    chisq_ds = np.sum((d_s-d_mean)**2/d_mean)

        




##fluxes_by_week = 






