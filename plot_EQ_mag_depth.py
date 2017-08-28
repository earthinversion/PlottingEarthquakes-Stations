from pylab import rcParams
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
import time


def get_marker_color(depth):
  # Returns green for small earthquakes, yellow for moderate
  #  earthquakes, and red for significant earthquakes.
  if depth < 100.0:
    return ('ro')
  elif 100.0 < depth < 200.0:
    return ('go')
  else:
    return ('yo')


rcParams['figure.figsize'] = (10, 6)

f = plt.figure()
t1 = time.clock()
# make sure the value of resolution is a lowercase L,
#  for 'low', not a numeral 1
my_map = Basemap(projection='robin', lat_0=0, lon_0=71,
                 resolution='l', area_thresh=1000.0)

print(time.clock() - t1, ' secs to create original Basemap instance')

# pickle to speed up the run
pickle.dump(my_map, open('map.pickle', 'wb'), -1)
# clear the figure
plt.clf()
# read pickle back in and plot it again (should be much faster).
t1 = time.clock()
m2 = pickle.load(open('map.pickle', 'rb'))

# Anotating the figure
my_map.drawcoastlines()
my_map.fillcontinents(color='w')
my_map.drawmapboundary(fill_color='#99ffff')

my_map.drawmeridians(np.arange(0, 360, 60), labels=[0, 0, 1, 0])
my_map.drawparallels(np.arange(-90, 90, 30), labels=[1, 1, 0, 0])


# reading the stations data
header1 = ["longS", "latS"]
df1 = pd.read_csv("all_stations.txt", sep="\s+", names=header1)
lons = list(df1["longS"])
lats = list(df1["latS"])


# plotting the stations data
x, y = my_map(lons, lats)
my_map.plot(x, y, 'b^', markersize=3)


# reading event magnitude and depth
with open("eventData.txt", 'r') as evfile:
  data = evfile.readlines()[1:]  # ignore the first line
with open("eventfile.txt", 'w') as ef:
  for i in range(len(data)):
    ef.write(data[i])
df3 = pd.read_csv("eventfile.txt", sep='\s+', header=None)
latE = list(df3.iloc[:, 9])
longE = list(df3.iloc[:, 10])
depE = list(df3.iloc[:, 11])
M0 = np.array(df3.iloc[:, 12]) * 10**7
Mw = np.array([2 / 3 * np.log10(x) - 10.7 for x in M0])
Mwn = 2 * (Mw - np.amin(Mw) + 1)  # amplify the data
min_marker_size = 2
for lon, lat, dep, mag in zip(longE, latE, depE, Mwn):
  x, y = my_map(lon, lat)
  msize = mag * min_marker_size
  marker_string = get_marker_color(dep)
  my_map.plot(x, y, marker_string, markersize=msize)

# plotting labels for depth and  EQ size
EQmag1 = 2 * (5 - np.amin(Mw) + 1) * min_marker_size  # eq magnitude 5
EQmag2 = 2 * (6 - np.amin(Mw) + 1) * min_marker_size  # eq magnitude 6
EQmag3 = 2 * (7 - np.amin(Mw) + 1) * min_marker_size  # eq magnitude 7
eq1 = my_map.plot([], [], 'ro',
                  markersize=10, label='EQ (depth < 100 km)')
eqm1 = my_map.plot([], [], 'ro',
                   markersize=EQmag1, label='EQ (Mag = 5)')
eq2 = my_map.plot([], [], 'go',
                  markersize=10, label='EQ (100 km < depth < 200 km)')
eqm2 = my_map.plot([], [], 'ro',
                   markersize=EQmag2, label='EQ (Mag = 6)')
eq3 = my_map.plot([], [], 'yo',
                  markersize=10, label='EQ (depth > 200 km)')
eqm3 = my_map.plot([], [], 'ro',
                   markersize=EQmag3, label='EQ (Mag = 7)')


#
plt.legend(loc=8, ncol=3, prop={'size': 11}, bbox_to_anchor=(0.32, -0.2, 0.32, -0.4))

#
f.savefig('EQ_distr.pdf', bbox_inches='tight', dpi=200)
# plt.show()
