import functools
from xml.dom import minidom
import numpy as np
import matplotlib.pyplot as plt
from decimal import Decimal
import math


def f(x, y):
    for t in y:
        if math.floor(float(t[0])) <= x <= math.ceil(float(t[1])):
            return 1
    return 0


horizon = "04"
satellites = "18"
file = "planning_data_" + satellites + "sat_" + horizon + "h"
doc = minidom.parse(file + "_modified.xml")
totalTime = int(horizon) * 60 * 60
downloadWindow = doc.getElementsByTagName("downloadWindow")
stations = {}

for dw in downloadWindow:
    sid = dw.getAttribute("id")
    satellite = dw.getAttribute("satellite")
    station = dw.getAttribute("station")
    startTime = dw.getAttribute("startTime")
    endTime = dw.getAttribute("endTime")
    print("id:%s " % sid)
    print("satellite:%s" % satellite)
    print("station:%s" % station)
    print("startTime:%s " % startTime)
    print("endTime:%s" % endTime)

for dw in downloadWindow:
    stations[dw.getAttribute("station")] = {}

for st in stations:
    for dw in downloadWindow:
        if st == dw.getAttribute("station"):
            stations[st][dw.getAttribute("satellite")] = []

for st in stations:
    for dw in downloadWindow:
        if st == dw.getAttribute("station"):
            stations[st][dw.getAttribute("satellite")].append(
                [dw.getAttribute("startTime"), dw.getAttribute("endTime")])

print(stations)

for st in stations:
    sats = []
    listTime = []
    for sat in stations[st]:
        # a = float(stations[st][sat][-1][-1])
        np.xvals = np.linspace(0, totalTime, totalTime)  # 100 points from 0 to 6 in ndarray
        sats.append(sat)
        np.yvals = [f(x, stations[st][sat]) for x in np.xvals]
        listTime.append(np.yvals)
        plt.plot(np.xvals, np.yvals)
    plt.title(st)
    plt.legend(sats)
    plt.xlabel('Time(s)')
    plt.ylabel('Download Windows')
    plt.show()
    comparison = np.zeros((totalTime,), dtype=int)
    for lt in listTime:
        comparison = [a+b for a, b in zip(comparison, lt)]
    plt.plot(np.xvals, comparison)
    plt.show()




