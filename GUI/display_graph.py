from pyqtgraph import QtCore, QtGui
import csv
import pyqtgraph as pg
from datetime import datetime
import sys
import numpy as np
import sched, time
import threading


NORMAL_FILE = "../Data/cs01_no_ls.csv"
RAS_FILE = "../Data/cs01_with_dufls_[VR].csv"

PLOT_SIZE = 500
TIMEOUT = 0.005

RANGE_MIN = 45
RANGE_MAX = 65

class Slider(QtGui.QWidget):
    def __init__(self, minimum, maximum, parent=None):
        super(Slider, self).__init__(parent=parent)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.label = QtGui.QLabel(self)
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtGui.QHBoxLayout()
        spacerItem = QtGui.QSpacerItem(0, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.slider = QtGui.QSlider(self)
        self.slider.setOrientation(QtCore.Qt.Vertical)
        self.horizontalLayout.addWidget(self.slider)
        spacerItem1 = QtGui.QSpacerItem(0, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.resize(self.sizeHint())

        self.minimum = minimum
        self.maximum = maximum
        self.slider.valueChanged.connect(self.setLabelValue)
        self.x = None
        self.setLabelValue(self.slider.value())

    def setLabelValue(self, value):
        self.x = self.minimum + (float(value) / (self.slider.maximum() - self.slider.minimum())) * (
        self.maximum - self.minimum)
        self.label.setText("{0:.4g}".format(self.x))

class Widget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent=parent)

        self.interval = 1
        self.index = 0

        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.w1 = Slider(0, 10)

#        self.w2 = Slider(-1, 1)
#        self.horizontalLayout.addWidget(self.w2)

#        self.w3 = Slider(-10, 10)
#        self.horizontalLayout.addWidget(self.w3)

#        self.w4 = Slider(-10, 10)
#        self.horizontalLayout.addWidget(self.w4)

        self.win = pg.GraphicsWindow(title="UFLS Demo")
        self.horizontalLayout.addWidget(self.win)
        #self.update()

        self.w1.slider.valueChanged.connect(self.setInterval)

        self.normalReadings, self.rasReadings, self.normalTimes, self.rasTimes = self.parse_files()

        #Print the difference between times and see if there's any hope, or else take the average of times

        #time_list = [(self.normalTimes[i+1] - self.normalTimes[i]).microseconds for i in range(len(self.normalTimes) - 1) ]
        #print float(sum(time_list)/1000)/float(len(time_list))

        self.win.resize(1000, 600)

        pg.setConfigOptions(antialias = True)

        self.normalPlot = self.win.addPlot(title = "Without RAS")
        self.normalCurve = self.normalPlot.plot(pen = pg.mkPen('r', width = 3))
        self.normalPlot.setYRange(RANGE_MIN, RANGE_MAX, padding = 0.1, update = False)

        self.rasPlot = self.win.addPlot(title = "With RAS")
        self.rasCurve = self.rasPlot.plot(pen = pg.mkPen('b', width = 3))
        self.rasPlot.setYRange(RANGE_MIN, RANGE_MAX, padding = 0.1, update = False)

        self.horizontalLayout.addWidget(self.w1)

        self.button = QtGui.QPushButton('Start', self)
        self.button.clicked.connect(self.startGraph)
        self.horizontalLayout.addWidget(self.button)

        self.updateThread = threading.Thread(target = self.update)
        

    def startGraph(self):
        print "STARTING ANIMATION"
        self.updateThread.start()


    def update(self):
        while True:
            if self.index + PLOT_SIZE >= len(self.normalReadings):
                self.index = 0
            self.normalCurve.setData(self.normalReadings[self.index : self.index+PLOT_SIZE])
            self.rasCurve.setData(self.rasReadings[self.index : self.index+PLOT_SIZE])
            self.index += 1
            time.sleep(TIMEOUT * self.interval)
        

    def setInterval(self):
        self.interval = self.w1.x

    def parse_files(self):

        normalFile = open(NORMAL_FILE, 'r') 
        rasFile = open(RAS_FILE, 'r')

        normalReader = csv.reader(normalFile)
        rasReader = csv.reader(rasFile)

        normalReadings = list()
        rasReadings = list()

        normalTimes = list()
        rasTimes = list()

        for row in normalReader:
            normalReadings.append(float(row[1].strip()))
        
            #Get all the dates and times and then display them
            #normalTimes.append(datetime.strptime(row[0].strip(), '%m/%d/%Y %X.%f'))
        
        for row in rasReader:
            rasReadings.append(float(row[1].strip()))
            #rasTimes.append(datetime.strptime(row[0].strip(), '%m/%d/%Y %X.%f'))


        normalFile.close()
        rasFile.close()

        print len(normalReadings)
        print len(rasReadings)

        return normalReadings, rasReadings, normalTimes, rasTimes




if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())


