from xml.dom import minidom
import numpy as np
import matplotlib.pyplot as plt
import math
import xml.etree.ElementTree as ET
import processing


class prepocessingbyid:

    def __init__(self):
        self.horizon = "04"
        self.satellites = "18"
        self.file = "planning_data_" + self.satellites + "sat_" + self.horizon + "h"
        self.doc = minidom.parse(self.file + ".xml")
        self.totalTime = int(self.horizon) * 60 * 60
        self.stations = {}
        self.processing = processing.processing(self.horizon, self.satellites, self.file)

    def update(self, vectorTime1, vectorTime2):
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

    def f(self, x, y):
        for t in y:
            if math.floor(float(t[0])) <= x <= math.ceil(float(t[1])):
                return 1
        return 0

    def calcul(self):
        downloadWindow = self.doc.getElementsByTagName("downloadWindow")
        for dw in downloadWindow:
            self.stations[dw.getAttribute("station")] = {}

        for st in self.stations:
            for dw in downloadWindow:
                if st == dw.getAttribute("station"):
                    self.stations[st][dw.getAttribute("id")] = []

        for st in self.stations:
            for dw in downloadWindow:
                if st == dw.getAttribute("station"):
                    self.stations[st][dw.getAttribute("id")].append(
                        [dw.getAttribute("startTime"), dw.getAttribute("endTime")])
        print(self.stations)

        np.xvals = np.linspace(0, self.totalTime, self.totalTime)  # 100 points from 0 to 6 in ndarray

        tree = ET.parse(self.file + "_modified.xml")
        root = tree.getroot()

        for st in self.stations:
            ids = []
            listTime = {}
            for id in self.stations[st]:
                np.yvals = [self.f(x, self.stations[st][id]) for x in np.xvals]
                listTime[id] = np.yvals
                plt.plot(np.xvals, np.yvals)
            plt.title(st)
            plt.legend(ids)
            plt.show()
            comparison = np.zeros((self.totalTime,), dtype=int)
            for lt in listTime:
                comparison = [a + b for a, b in zip(comparison, listTime[lt])]
            plt.plot(np.xvals, comparison)
            plt.show()

            vectorzeros = np.zeros((self.totalTime,), dtype=int)
            for lt1 in listTime:
                for lt2 in listTime:
                    if lt1 != lt2:
                        comparison = [a * b for a, b in zip(listTime[lt1], listTime[lt2])]
                        if not np.array_equal(comparison, vectorzeros):
                            sT, mT, eT, w = self.update(self.stations[st][lt1][0], self.stations[st][lt2][0])
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
        tree.write(self.file + "_modified.xml")


prepocessingbyid = prepocessingbyid()
prepocessingbyid.calcul()
