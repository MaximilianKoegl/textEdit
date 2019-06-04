#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtGui, QtCore, QtWidgets
import re
import csv
import io
# from table_logger import TableLogger


class SuperText(QtWidgets.QTextEdit):

    def __init__(self):
        super(SuperText, self).__init__()

        # method to print logs to console in a nice formatted tabular way.
        # easier to read, but not valid csv. disabled by default
        # self.tbl = TableLogger(columns="timestamp,event,input,time")

        self.word_timer = QtCore.QTime()
        self.sentence_timer = QtCore.QTime()
        self.is_running_word = False
        self.is_running_sentence = False
        self.sentence = ""
        self.current_word = ""
        self.prev_content = ""

        self.textChanged.connect(self.changedText)

        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 400, 400)
        self.setWindowTitle("SuperText")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)
        self.show()

    def changedText(self):
        self.handleTimer()
        # Delete last char and prevent measurement from errors
        if not len(self.prev_content) > len(self.toPlainText()):
            self.handleText()
        self.prev_content = self.toPlainText()

    def handleText(self):
        last_char = self.toPlainText()[-1:]

        # Stop word measuring and add word to sentence
        if last_char == " ":
            self.pressedSpacebar(last_char)
        elif last_char == "\n":
            self.pressedEnter(last_char)
        # Add latest character to word
        else:
            self.current_word += last_char

            # self.tbl(self.timestamp(), "character typed", last_char, 0)

            self.log_csv([self.timestamp(), "character typed", last_char, 0])

    def pressedSpacebar(self, last_char):
        self.is_running_word = False
        self.sentence += self.current_word + " "

        # self.tbl(self.timestamp(), "word typed", self.current_word, self.stop_measurement(self.word_timer))
        if re.search('[a-zA-Z]', self.current_word):
            self.log_csv([
                        self.timestamp(),
                        "word typed",
                        self.current_word,
                        self.stop_measurement(self.word_timer)
                        ])
        self.current_word = ""
    
    def pressedEnter(self, last_char):
        self.is_running_sentence = False
        self.is_running_word = False
        self.sentence += self.current_word

        # self.tbl(self.timestamp(), "sentence typed", self.sentence, self.stop_measurement(self.sentence_timer))
        if self.current_word != "":
            self.log_csv([
                            self.timestamp(),
                            "word typed",
                            self.current_word,
                            self.stop_measurement(self.word_timer)
                        ])
        if self.sentence != "":
            self.log_csv([
                            self.timestamp(),
                            "sentence typed",
                            self.sentence,
                            self.stop_measurement(self.sentence_timer)
                        ])
        self.sentence = ""
        self.current_word = ""

    def handleTimer(self):
        if not self.is_running_word:
            self.is_running_word = True
            self.start_measurement(self.word_timer)

        if not self.is_running_sentence:
            self.is_running_sentence = True
            self.start_measurement(self.sentence_timer)

    def start_measurement(self, timer):
        timer.start()

    def stop_measurement(self, timer):
        return timer.elapsed()

    def timestamp(self):
        return QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate)

    # convert log-data from list to csv-string and output it to stdout
    # https://stackoverflow.com/questions/9157314/how-do-i-write-data-into-csv-format-as-string-not-file
    def log_csv(self, data):
        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerow(data)
        print(si.getvalue().strip("\r\n"))


def main():
    app = QtWidgets.QApplication(sys.argv)
    super_text = SuperText()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
