#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtGui, QtCore, QtWidgets
import re


class SuperText(QtWidgets.QTextEdit):
    def __init__(self, example_text):
        super(SuperText, self).__init__()
        self.numbers=[]
        self.word_timer = QtCore.QTime()
        self.sentence_timer = QtCore.QTime()
        self.is_running_word = False
        self.is_running_sentence = False
        self.template_doc = ""
        self.setHtml(example_text)
        self.prev_content = ""
        self.textChanged.connect(self.changedText)
        self.generate_template()
        self.render_template()
        self.initUI()
        
    def initUI(self):      
        self.setGeometry(0, 0, 400, 400)
        self.setWindowTitle('SuperText')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)
        self.show()

    def changedText(self):
        self.handleTimer()
        self.handleText()
    
    def handleText(self):
        last_char = self.toPlainText()[-1:]
        print("Key Pressed: " + repr(last_char))

        if last_char == " ":
            print("Wordtime: ")
            print(self.stop_measurement(self.word_timer))
            self.is_running_word = False

        elif last_char == "\n":
            print("Sentencetime: ")
            print(self.stop_measurement(self.sentence_timer))
            self.is_running_sentence = False
        
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

    def wheelEvent(self, ev):
        super(SuperText, self).wheelEvent(ev)
        self.generate_template()
        self.render_template()
        anc = self.anchorAt(ev.pos())
        if (anc):
            self.change_value(anc, ev.angleDelta().y())
            print("Hello")

    def change_value(self, val_id, amount):
        self.numbers[int(str(val_id))] += amount / 120 
        self.render_template()
        
    def render_template(self):
        cur = self.textCursor()
        doc = self.template_doc 
        for num_id, num in enumerate(self.numbers):
            doc = doc.replace('$' + str(num_id) + '$', '%d' % (num))
        self.setHtml(doc)
        self.setTextCursor(cur)

    def generate_template(self):
        content = str(self.toPlainText())
        numbers = list(re.finditer(" -?[0-9]+", content))
        numbers = [int(n.group()) for n in numbers]
        self.numbers = numbers
        if len(numbers) == 0:
            self.template_doc = content
            return
        for num_id in range(len(numbers)):
            content = re.sub(" " + str(numbers[num_id])  , " <a href='%d'>$%d$</a>" % (num_id, num_id), content, count=1)
        self.template_doc = content

def main():
    app = QtWidgets.QApplication(sys.argv)
    super_text = SuperText("")
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
