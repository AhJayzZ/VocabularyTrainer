from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from .Ui_init import *

import requests
import googletrans
import random
import os,sys,json

class VocabularyTrainer(QMainWindow,Ui_MainWindow):
    """
    Vocabulary Trainer main window
    """
    def __init__(self):
        """
        Initalizing all setting
        """
        super(VocabularyTrainer,self).__init__()
        self.setupUi(self)
        self.getRandomWord()
        self.updateRandomWord()
        
        self.connection_thread = connectCheck_Thread(self)
        self.connectionTimer = QTimer(self,timeout=self.connectionCheck).start(1000)

        self.addButton.clicked.connect(self.addRandomWord)
        self.nextButton.clicked.connect(self.updateRandomWord)
        self.removeButton.clicked.connect(self.removeRandomWord)
        self.exitButton.clicked.connect(sys.exit)

    def connectionCheck(self):
        """
        Check network connection
        """
        self.connection_thread.start()

    def getRandomWord(self):
        """
        generator a random word in random_words.txt
        """
        wordsFile = 'random_words.txt'
        wordData = open(wordsFile).read()
        wordList = wordData.split('","')
        randomNumber = random.randint(0,len(wordList))
        return wordList[randomNumber]
    
    def updateRandomWord(self):
        """
        update wordLabel
        """
        self.randomWord = self.getRandomWord()
        self.wordLabel.setText(self.randomWord)

    def addRandomWord(self):
        self.recordList.addItem(self.randomWord)

    def removeRandomWord(self):
        selectedItems = self.recordList.selectedItems()
        if not selectedItems: return
        for item in selectedItems:
            itemIndex = self.recordList.row(item)
            self.recordList.takeItem(itemIndex)

# ------------------------------------- Threading -------------------------------------


class webCrawler(QThread):
    """
    web scraping thread
    """
    def __init__(self,mainWindow):
        super().__init__(parent=None)
        self.mainWindow = mainWindow
        self.dictUrl = 'https://www.bing.com/dict/?q='
    
    #def run(self):





class connectCheck_Thread(QThread):
    """
    Connection check thread
    """
    def __init__(self,mainWindow):
        super().__init__(parent=None)
        self.url = 'http://www.google.com'
        self.mainWindow = mainWindow

    def run(self):
        try:
            requests.get(url=self.url,timeout=1)
            self.mainWindow.connectionLabel.setStyleSheet('color:blue')
            self.mainWindow.connectionLabel.setText('網路連線狀態: 正常')
        except requests.exceptions.ConnectionError:
            self.mainWindow.connectionLabel.setStyleSheet('color:red')
            self.mainWindow.connectionLabel.setText('網路連線狀態: 失敗')