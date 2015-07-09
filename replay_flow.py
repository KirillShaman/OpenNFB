from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import scipy.signal

from PySide import QtCore
from bdf import BDFReader, BDFWriter
from acquisition import BDFThread, OpenBCIThread

import sys, imp

app = QtGui.QApplication([])
win = QtGui.QMainWindow()
win.setWindowTitle("OpenNFB")

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)


protocol_name = sys.argv[1]
replay_file = sys.argv[2]

import protocols
protocol = protocols.__dict__[protocol_name]

flow = protocol.flow()
context = flow.Context()
context.set_flow(flow)

widget = flow.widget()
win.setCentralWidget(widget)

win.show()

sourceThread = BDFThread(sys.argv[2])

from flow import Signal
channel1 = Signal()

def handlePacket(packet):
    data = {'Channel 1' : packet.channel_data[0]}
    context.append_channel_data(data)
    context.process()

sourceThread.newPacket.connect(handlePacket)
sourceThread.start()

def updateGUI():
    for child in widget.children():
        if hasattr(child, 'updateGUI'):
            child.updateGUI()

guiTimer = QtCore.QTimer()
guiTimer.timeout.connect(updateGUI)
guiTimer.start(0)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
       QtGui.QApplication.instance().exec_()

