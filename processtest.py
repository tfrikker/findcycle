import numpy as np
import sys
import json
import datetime
import scipy.stats as stats

input_list_from_server = json.loads(sys.argv[1])
dt = int(input_list_from_server["duration"])
timedate = int(input_list_from_server["time"])
status = input_list_from_server["status"]["stations"]
information = input_list_from_server["information"]["stations"]

statusarray = np.array([[x["num_bikes_available"],x["station_id"]]  for x in status])
bikes = np.array(statusarray[:,0], dtype=int)
stations_status = statusarray[:,1]

infoarray = np.array([[x["lat"],x["lon"],x["station_id"]] for x in information])
latitudes = infoarray[:,0]
longitudes = infoarray[:,1]
stations_info = infoarray[:,2]

status_sort = np.argsort(stations_status)
bikes = bikes[status_sort]
stations = np.array(stations_status[status_sort], dtype=np.float)

info_sort = np.argsort(stations_info)
latitudes = latitudes[info_sort]
longitudes = longitudes[info_sort]

timezoneshift = -4 #UTC-N
dstshift = 0

date_time = datetime.datetime.utcfromtimestamp(timedate)
t0 = (date_time - date_time.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()-60*60*(timezoneshift+dstshift)

day = date_time.weekday()
monthnum = date_time.month

d_times = np.empty(0)
d_locs = np.empty(0)
a_times = np.empty(0)
a_locs = np.empty(0)

daydict = {0:"monday", 1:"tuesday", 2:"wednesday", 3:"thursday", 4:"friday", 5:"saturday", 6:"sunday"}
seasondict = {1:"winter",2:"winter",3:"spring",4:"spring",5:"spring",6:"summer",7:"summer",8:"summer",9:"fall",10:"fall",11:"fall",12:"winter"}

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

chi_sq = dict(zip(locs_tot, np.zeros(len(locs_tot))))
flux_means = dict(zip(locs_tot, np.zeros(len(locs_tot))))
for i in range(len(locs_tot)):
    loc = locs_tot[i]
    a_s = locs_tot_dict_a[loc]
    d_s = locs_tot_dict_d[loc]

    try:
        a_mean = np.mean(a_s) if len(a_s)>0 else 0
        d_mean = np.mean(d_s) if len(d_s)>0 else 0

        flux_mean = a_mean-d_mean


        X_sq_as = np.sum((a_s-a_mean)**2/a_mean) if a_mean!=0 else 0
        X_sq_ds = np.sum((d_s-d_mean)**2/d_mean) if d_mean!=0 else 0

        chi_sq[loc] = stats.chi2.sf(X_sq_as+X_sq_ds, len(a_s)-1)

    except:
        flux_mean = 0
        chi_sq[loc] = 0

    flux_means[loc] = int(np.round(flux_mean))

final_return = {"points": []}

for i in range(len(stations)):
    station = stations[i]

    latitude = latitudes[i]
    longitude = longitudes[i]

    try:
        numBikes_expected = flux_means[station]+bikes[i]
        confidence = chi_sq[station]
    except KeyError:
        numBikes_expected = bikes[i]
        confidence = 0.5

    conf = np.round(confidence,3)
    conf = conf if not np.isnan(conf) else 0

    final_return["points"].append({"lat": latitude, "lon": longitude, "numBikes": numBikes_expected, "confidence": conf})

print(final_return)
