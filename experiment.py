#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtGui, QtCore, QtWidgets
import csv
from text_entry_speed_test import SuperText
# from text_input_technique import SuperText

class TextEditExperiment(QtWidgets.QWidget):

    def __init__(self):
        super(TextEditExperiment, self).__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 400, 400)
        self.setWindowTitle("TextEditExperiment")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(QtWidgets.QLabel())
        self.layout.addWidget(SuperText())
        self.setLayout(self.layout)
        self.show()

def main():
    app = QtWidgets.QApplication(sys.argv)
    super_text = TextEditExperiment()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()