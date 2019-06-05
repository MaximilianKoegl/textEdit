#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtGui, QtCore, QtWidgets
import re
import csv
import io
import json


# https://doc.qt.io/qtforpython/PySide2/QtWidgets/QCompleter.html?highlight=qcompleter
# https://stackoverflow.com/questions/28956693/pyqt5-qtextedit-auto-completion
class TextInputTechnique(QtWidgets.QCompleter):
    insertText = QtCore.pyqtSignal(str)

    def __init__(self, wordlist, parent=None):
        QtWidgets.QCompleter.__init__(self, wordlist, parent)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.highlighted.connect(self.setHighlighted)

    def setHighlighted(self, text):
        self.lastSelected = text

    def getSelected(self):
        return self.lastSelected


class SuperText(QtWidgets.QTextEdit):

    def __init__(self, user_id, method, word_list, sentences, caller_class, parent=None):
        super(SuperText, self).__init__(parent)
        self.caller_class = caller_class
        self.user_id = user_id
        self.method = method
        self.word_list = word_list
        self.sentences = [item for item in sentences]
        self.count = 0
        self.word_timer = QtCore.QTime()
        self.sentence_timer = QtCore.QTime()
        self.is_running_word = False
        self.is_running_sentence = False
        self.sentence = ""
        self.current_word = ""
        self.prev_content = ""

        # https://stackoverflow.com/questions/28956693/pyqt5-qtextedit-auto-completion
        self.completer = TextInputTechnique(self.word_list)
        self.completer.setWidget(self)
        self.completer.insertText.connect(self.insertCompletion)
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 400, 400)
        self.setWindowTitle("SuperText")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)
        self.show()

    # https://stackoverflow.com/questions/28956693/pyqt5-qtextedit-auto-completion
    def insertCompletion(self, completion):
        tc = self.textCursor()
        extra = (len(completion) - len(self.completer.completionPrefix()))
        tc.movePosition(QtGui.QTextCursor.Left)
        tc.movePosition(QtGui.QTextCursor.EndOfWord)
        tc.insertText(completion[-extra:])
        self.current_word = self.current_word + completion[-extra:]
        self.setTextCursor(tc)
        self.completer.popup().hide()
        self.finishedWord(1)

    # https://stackoverflow.com/questions/28956693/pyqt5-qtextedit-auto-completion
    def focusInEvent(self, event):
        if self.completer:
            self.completer.setWidget(self)
        QtWidgets.QTextEdit.focusInEvent(self, event)

    # https://stackoverflow.com/questions/28956693/pyqt5-qtextedit-auto-completion
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Shift or event.key() == QtCore.Qt.Key_Backspace:
            return
        tc = self.textCursor()
        if event.key() == QtCore.Qt.Key_Tab and self.completer.popup().isVisible():

            self.completer.insertText.emit(self.completer.getSelected())
            self.completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
            return

        QtWidgets.QTextEdit.keyPressEvent(self, event)
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        cr = self.cursorRect()

        if len(tc.selectedText()) > 0:
            self.completer.setCompletionPrefix(tc.selectedText())
            popup = self.completer.popup()
            popup.setCurrentIndex(self.completer.completionModel().index(0, 0))

            cr.setWidth(self.completer.popup().sizeHintForColumn(0) +
                        self.completer.popup().
                        verticalScrollBar().sizeHint().width())
            self.completer.complete(cr)

        else:
            self.completer.popup().hide()

        if not event.key() == QtCore.Qt.Key_Tab:
            self.handle_text()

    def handle_text(self):
        self.handleTimer()
        last_char = self.toPlainText()[-1:]
        self.log_csv(["character typed", self.timestamp(), repr(last_char).replace("'", ""), 0])

        # Stop word measuring and add word to sentence
        if last_char == " ":
            self.finishedWord(0)
        elif last_char == "\n":
            self.pressedEnter()
        # Add latest character to word
        else:
            self.current_word += last_char

    def finishedWord(self, num):
        self.is_running_word = False
        self.sentence += self.current_word
        if num:
            text = "completed"
        else:
            text = "typed"
            self.sentence += " "

        if re.search('[a-zA-Z]', self.current_word):
            self.log_csv([
                        str("word "+text),
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
        self.caller_class.setSentence()

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

class TextEditProgram(QtWidgets.QWidget):

    def __init__(self, user_id, method, sentences):
        super(TextEditProgram, self).__init__()
        self.user_id = user_id
        self.method = method
        self.count = 0
        self.sentences = [item for item in sentences]
        self.word_list = self.getWordList()
        self.initUI()
        self.setSentence()

    def initUI(self):
        self.setGeometry(0, 0, 400, 400)
        self.setWindowTitle("TextEditExperiment")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)
        self.layout = QtWidgets.QVBoxLayout()
        self.sentence_box = QtWidgets.QLabel()
        self.super_text = SuperText(self.user_id, self.method, self.word_list, self.sentences, self)
        self.layout.addWidget(self.sentence_box)
        self.layout.addWidget(self.super_text)
        self.setLayout(self.layout)
        self.show()

    def setSentence(self):
        if self.count > len(self.sentences)-1:
            sys.exit()
        self.sentence_box.setText(self.sentences[self.count])
        self.count += 1

    def getWordList(self):
        list = []
        for item in self.sentences:
            placeholder = item.split()
            list.extend([word for word in placeholder if word not in list])
        return list

def main():
    app = QtWidgets.QApplication(sys.argv)
    text_edit_program = TextEditProgram(*parse_setup(sys.argv[1]))
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
