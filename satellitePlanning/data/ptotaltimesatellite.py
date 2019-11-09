from xml.dom import minidom


class ptotaltimesatellite:

    def __init__(self, horizon, satellites, file):
        self.horizon = horizon
        self.satellites = satellites
        self.file = file
        self.doc = minidom.parse(file + "_modified.xml")
        self.totalTime = int(horizon) * 60 * 60
        self.satellites = {}

    def calcul(self):
        downloadWindow = self.doc.getElementsByTagName("downloadWindow")

        for dw in downloadWindow:
            self.satellites[dw.getAttribute("satellite")] = {}

        for sat in self.satellites:
            total_time_sat = 0
            for dw in downloadWindow:
                if sat == dw.getAttribute("satellite"):
                    total_time_sat += float(dw.getAttribute("endTime")) - float(dw.getAttribute("startTime"))
            self.satellites[sat] = total_time_sat

        for sat in self.satellites:
            print(sat, self.satellites[sat], "Mb")
