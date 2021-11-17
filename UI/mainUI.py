from datetime import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from .Ui_init import *

from bs4 import BeautifulSoup
import requests
import googletrans
import random
import sys

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
        self.setStyleSheet("background-color:#E8B4BC")
        
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
        self.webCrawler_thread = webCrawler(self.randomWord)
        self.webCrawler_thread.finishSingal.connect(self.updateRandomWordInfo)
        self.webCrawler_thread.start()
        
        self.nextButton.setEnabled(False)   # Avoid too fast refresh
        self.wordLabel.setText(self.randomWord)

    def updateRandomWordInfo(self):
        """
        update wordInfoLabel and wordSentenceLabel
        """
        self.nextButton.setEnabled(True)
        self.nextButton.setDefault(True)
        self.wordInfoLabel.setText(self.webCrawler_thread.wordInfo)
        self.wordSentenceLabel.setText(self.webCrawler_thread.wordSentence)

    def addRandomWord(self):
        """
        add word to recordList
        """
        self.recordList.addItem(self.randomWord)

    def removeRandomWord(self):
        """
        remove the selected words form recordList
        """
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
    finishSingal = pyqtSignal(int)
    def __init__(self,word):
        super().__init__(parent=None)
        
        self.word = word
        self.url = "https://www.bing.com/dict/search?q={}".format(word)
        self.header = {'cookie':'_EDGE_S=F&mkt=zh-cn'} # this is key header
    
    def run(self):
        self.htmlContent = requests.get(url=self.url,headers=self.header).text
        self.soup = BeautifulSoup(self.htmlContent,'html.parser')
        self.wordInfo = self.getWordInfo()
        self.wordSentence = self.getWordSentence()
        self.finishSingal.emit(1)
    
    def getWordInfo(self):
        pos = self.soup.find_all('span',class_='pos')
        definitions = self.soup.find_all('span',class_='def b_regtxt')
        wordInfoArray = []
        for index in range(max(len(pos),len(definitions))):
            wordInfoArray.append("{}.(詞性:{}) {}".format(str(index+1),
                                                    pos[index].text, 
                                                    definitions[index].text))
        return '\n'.join(wordInfoArray)

    def getWordSentence(self):
        return "unfinished"

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