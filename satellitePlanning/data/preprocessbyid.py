import functools
from xml.dom import minidom
import numpy as np
import matplotlib.pyplot as plt
from decimal import Decimal
import math
import xml.etree.ElementTree as ET


def update(vectorTime1, vectorTime2):
    print(vectorTime1)
    print(vectorTime2)
    if float(vectorTime1[0]) < float(vectorTime2[0]):
        mT = (float(vectorTime1[1]) + float(vectorTime2[0])) / 2
        sT = float(vectorTime1[0])
        eT = float(vectorTime2[1])
        w = 1
    else:
        mT = (float(vectorTime1[0]) + float(vectorTime2[1])) / 2
        sT = float(vectorTime2[0])
        eT = float(vectorTime1[1])
        w = 2
    return sT, mT, eT, w


def f(x, y):
    for t in y:
        if math.floor(float(t[0])) <= x <= math.ceil(float(t[1])):
            return 1
    return 0


horizon = "24"
satellites = "18"
file = "planning_data_" + satellites + "sat_" + horizon + "h"
doc = minidom.parse(file + ".xml")
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
            stations[st][dw.getAttribute("id")] = []

for st in stations:
    for dw in downloadWindow:
        if st == dw.getAttribute("station"):
            stations[st][dw.getAttribute("id")].append(
                [dw.getAttribute("startTime"), dw.getAttribute("endTime")])

print(stations)

np.xvals = np.linspace(0, totalTime, totalTime)  # 100 points from 0 to 6 in ndarray

tree = ET.parse(file + "_modified.xml")
root = tree.getroot()

for st in stations:
    ids = []
    listTime = {}
    for id in stations[st]:
        np.yvals = [f(x, stations[st][id]) for x in np.xvals]
        listTime[id] = np.yvals
        plt.plot(np.xvals, np.yvals)
    plt.title(st)
    plt.legend(ids)
    plt.show()
    comparison = np.zeros((totalTime,), dtype=int)
    for lt in listTime:
        comparison = [a + b for a, b in zip(comparison, listTime[lt])]
    plt.plot(np.xvals, comparison)
    plt.show()

    vectorzeros = np.zeros((totalTime,), dtype=int)
    for lt1 in listTime:
        for lt2 in listTime:
            if lt1 != lt2:
                comparison = [a * b for a, b in zip(listTime[lt1], listTime[lt2])]
                if not np.array_equal(comparison, vectorzeros):
                    sT, mT, eT, w = update(stations[st][lt1][0], stations[st][lt2][0])
                    for dws in root.findall("downloadWindows"):
                        for dw in dws.findall("downloadWindow"):
                            if dw.get("id") == lt1 and w == 1:
                                dw.set('startTime', str(sT))
                                dw.set('endTime', str(mT))
                            elif dw.get("id") == lt2 and w == 1:
                                dw.set('startTime', str(mT + 1))
                                dw.set('endTime', str(eT))
                            elif dw.get("id") == lt2 and w == 2:
                                dw.set('startTime', str(sT))
                                dw.set('endTime', str(mT + 1))
                            elif dw.get("id") == lt1 and w == 2:
                                dw.set('startTime', str(mT))
tree.write(file + "_modified.xml")
