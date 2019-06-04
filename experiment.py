#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtGui, QtCore, QtWidgets
import json
from text_entry_speed_test import SuperText
# from text_input_technique import SuperText


class TextEditExperiment(QtWidgets.QWidget):

    def __init__(self, user_id, method, sentences):
        super(TextEditExperiment, self).__init__()
        self.user_id = user_id
        self.method = method
        self.sentences = sentences
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
        print(self.sentences)


def main():
    app = QtWidgets.QApplication(sys.argv)
    super_text = TextEditExperiment(*parse_setup(sys.argv[1]))
    sys.exit(app.exec_())


def parse_setup(filename):
    with open(filename) as f:
        contents = json.load(f)
    user_id = contents['user_id']
    method = contents['method']
    sentences = contents['sentences']
    return user_id, method, sentences


if __name__ == '__main__':
    main()