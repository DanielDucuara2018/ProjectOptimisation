import os
from xml.dom import minidom


class processing:

    def __init__(self, horizon, satellites, file):
        self.horizon = horizon
        self.satellites = satellites
        self.file = file
        self.cur_path = os.path.dirname(__file__)
        self.volumens = {}
        self.volumen()

    def volumen(self):
        for nSat in range(int(self.satellites)):
            sat = "SAT" + str(nSat + 1)
            self.volumens[sat] = 0
            volumen = 0
            new_path = os.path.relpath('..//output//solutionAcqPlan_' + sat + '.txt', self.cur_path)
            f = open(new_path, "r")
            for x in f:
                volumen += int(x.split(" ")[4])
            self.volumens[sat] = volumen

        doc = minidom.parse(self.file + ".xml")
        recordedAcquisition = doc.getElementsByTagName("recordedAcquisition")
        for dw in recordedAcquisition:
            if dw.getAttribute("satellite") in self.volumens:
                self.volumens[dw.getAttribute("satellite")] += int(dw.getAttribute("volume"))
        print(self.volumens)
