#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtGui, QtCore, QtWidgets
import re
import csv
import io
import json


class SuperText(QtWidgets.QWidget):

    def __init__(self, user_id, method, sentences):
        super(SuperText, self).__init__()
        self.user_id = user_id
        self.method = method
        self.sentences = [item for item in sentences]
        self.count = 0
        self.word_timer = QtCore.QTime()
        self.sentence_timer = QtCore.QTime()
        self.is_running_word = False
        self.is_running_sentence = False
        self.sentence = ""
        self.current_word = ""
        self.prev_content = ""
        self.initUI()
        self.setTestText()

    def initUI(self):
        self.setGeometry(0, 0, 400, 400)
        self.setWindowTitle("SuperText")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.sentence_box = QtWidgets.QLabel(self)
        self.text_edit = QtWidgets.QTextEdit(self)
        self.layout.addWidget(self.sentence_box)
        self.layout.addWidget(self.text_edit)
        self.setLayout(self.layout)
        self.text_edit.textChanged.connect(self.changedText)

        self.show()

    def setTestText(self):
        self.sentence_box.setText(self.sentences[self.count])

    def changedText(self):
        self.handleTimer()
        if not len(self.prev_content) > len(self.text_edit.toPlainText()):
            self.handleText()
        self.prev_content = self.text_edit.toPlainText()

    def handleText(self):
        last_char = self.text_edit.toPlainText()[-1:]
        if last_char == " ":
            self.pressedSpacebar()
        elif last_char == "\n":
            self.pressedEnter()
        else:
            self.current_word += last_char
            self.log_csv(["character typed", self.timestamp(), last_char, 0])

    def pressedSpacebar(self):
        self.is_running_word = False
        self.sentence += self.current_word + " "
        if re.search('[a-zA-Z]', self.current_word):
            self.log_csv([
                        "word typed",
                        self.timestamp(),
                        self.current_word,
                        self.stop_measurement(self.word_timer)
                        ])
        self.current_word = ""

    def pressedEnter(self):
        self.is_running_sentence = False
        self.is_running_word = False
        self.sentence += self.current_word
        if self.current_word != "":
            self.log_csv([
                            "word typed",
                            self.timestamp(),
                            self.current_word,
                            self.stop_measurement(self.word_timer)
                        ])
        if self.sentence != "":
            self.log_csv([
                            "sentence typed",
                            self.timestamp(),
                            self.sentence,
                            self.stop_measurement(self.sentence_timer)
                        ])

        self.sentence = ""
        self.current_word = ""
        self.checkForNextSentence()

    def checkForNextSentence(self):
        if self.count >= len(self.sentences)-1:
            sys.exit()
        self.count += 1
        self.setTestText()

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
        data.extend([self.method, self.user_id])
        cw.writerow(data)
        print(si.getvalue().strip("\r\n"))


def main():
    app = QtWidgets.QApplication(sys.argv)
    super_text = SuperText(*parse_setup(sys.argv[1]))
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
