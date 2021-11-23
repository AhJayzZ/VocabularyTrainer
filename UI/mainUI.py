from ntpath import join
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from .Ui_init import *

from bs4 import BeautifulSoup
from googletrans import Translator
import text_to_speech
import requests
import random
import json
import sys,os

class VocabularyTrainer(QMainWindow,Ui_MainWindow):
    """
    Vocabulary Trainer main window
    """
    def __init__(self):
        """
        Initalizing all setting
        """
        super(VocabularyTrainer,self).__init__()

        # unfinished
        self.currentPath = os.path.dirname(__file__) # GUI
        self.dirPath = os.path.split(self.currentPath)[0] # ../ => project_code
        self.filePath = os.path.join(self.dirPath,'localRecord.json')

        self.setupUi(self)
        self.getRandomWord()
        self.updateRandomWord()
        self.loadRecord()
        self.setStyleSheet("background-color:#ABC4A1")
        self.setWindowIcon(QIcon('UI/images/window_icon.png'))
        self.soundButton.setIcon(QIcon('UI/images/sound_icon.png'))
        self.generateButton.setIcon(QIcon('UI/images/generate_icon.png'))
        self.addButton.setIcon(QIcon('UI/images/add_icon.png'))
        self.removeButton.setIcon(QIcon('UI/images/remove_icon.png'))
        self.exitButton.setIcon(QIcon('UI/images/exit_icon.png'))
        
        self.connection_thread = connectCheck_Thread(self)
        self.connectionTimer = QTimer(self,timeout=self.connectionCheck).start(1000)

        self.addButton.clicked.connect(self.addRandomWord)
        self.generateButton.clicked.connect(self.updateRandomWord)
        self.removeButton.clicked.connect(self.removeRandomWord)
        self.soundButton.clicked.connect(self.playSound)
        self.exitButton.clicked.connect(sys.exit)

        self.recordList.itemSelectionChanged.connect(self.setRecord)

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
        self.gTTS_thread = gTTS_Thread(self.randomWord)
        self.gTTS_thread.start()
        self.webCrawler_thread = webCrawler(self.randomWord)
        self.webCrawler_thread.finishSingal.connect(self.updateRandomWordInfo)
        self.webCrawler_thread.start()
        self.wordLabel.setText(self.randomWord)

        # Avoid too fast refresh
        self.generateButton.setEnabled(False)   
        self.addButton.setEnabled(False)
        self.removeButton.setEnabled(False)


    def updateRandomWordInfo(self):
        """
        update wordInfoLabel and wordSentenceLabel
        """
        self.addButton.setEnabled(True)
        self.removeButton.setEnabled(True)
        self.generateButton.setEnabled(True)
        self.generateButton.setDefault(True)
        # Word
        if not self.webCrawler_thread.wordInfo:
            translator = Translator()
            self.webCrawler_thread.wordInfo = translator.translate(self.randomWord, src='en', dest='zh-tw').text
        self.wordInfoLabel.setText(self.webCrawler_thread.wordInfo)
        # Sentence
        if self.webCrawler_thread.wordSentence:
             self.wordSentenceLabel.setText(self.webCrawler_thread.wordSentence)
        else:
            self.webCrawler_thread.wordSentence = 'Found nothing sentence...'
            self.wordSentenceLabel.setText('Found nothing sentence...')
        
    def addRandomWord(self):
        """
        add word to recordList
        """
        self.recordList.addItem(self.randomWord)
        self.addRecord()

    def removeRandomWord(self):
        """
        remove the selected words form recordList
        """
        selectedItem = self.recordList.currentItem()
        if not selectedItem: return
        else:
            itemIndex = self.recordList.row(selectedItem)
            self.recordList.takeItem(itemIndex)
            file = open(self.filePath,'r',encoding='utf-8') 
            self.file = open(self.filePath,'r',encoding='utf-8') 
            fileContent = json.load(self.file)
            with open(self.filePath,'w',encoding='utf-8') as file:
                if selectedItem.text() in fileContent[itemIndex].values():
                    del fileContent[itemIndex]
                json.dump(fileContent,file,ensure_ascii=False)
            file.close()

    def playSound(self):
        """
        play random word mp3 file
        """
        self.gTTS_thread = gTTS_Thread(self.randomWord)
        self.gTTS_thread.start()

    def setRecord(self):
        """
        set label text to local record
        """
        with open(self.filePath,'r',encoding='utf-8') as file:
            fileContent = json.load(file)
            selectedItem = self.recordList.currentItem()
            itemIndex = self.recordList.row(selectedItem)
            self.wordLabel.setText(fileContent[itemIndex]['word'])
            self.wordInfoLabel.setText(fileContent[itemIndex]['info'])
            self.wordSentenceLabel.setText(fileContent[itemIndex]['sentences'])
            file.close()

    def loadRecord(self):
        """
        load local record 
        """
        with open(self.filePath,'r',encoding='utf-8') as file:
            fileData = json.load(file)
            for index in range(len(fileData)):
                self.recordList.addItem(fileData[index]['word'])
            file.close()

    def addRecord(self): 
        """
        add word dictionary to local record
        """
        if not os.path.exists(self.filePath):
            open(self.filePath,'w')

        wordDict = {"word":self.randomWord,
                    "info":self.webCrawler_thread.wordInfo,
                    "sentences":self.webCrawler_thread.wordSentence}
        with open(self.filePath,'r+',encoding='utf-8') as file:
            fileContent = json.load(file)
            fileContent.append(wordDict)
            file.seek(0)
            json.dump(fileContent,file,ensure_ascii=False)
            file.close()
        
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
        self.sentenceUrl = "http://www.iciba.com/word?w={}".format(word)
        self.sentenceUrlHeader={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',}
    
    def run(self):
        # Word
        self.htmlContent = requests.get(url=self.url,headers=self.header).text
        self.soup = BeautifulSoup(self.htmlContent,'html.parser')
        # Sentence
        self.sentenceHtmlContent =requests.get(url=self.sentenceUrl,headers=self.sentenceUrlHeader).text
        self.sentenceSoup = BeautifulSoup(self.sentenceHtmlContent,'html.parser')
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
        sentences = self.sentenceSoup.find_all('p',class_='NormalSentence_en__3Ey8P')
        chineseSentences = self.sentenceSoup.find_all('p',class_='NormalSentence_cn__27VpO')
        sentenceArray = []
        for index in range(len(sentences)):
            if chineseSentences[index].text:
                sentenceArray.append("{}.{}{}{}".format(str(index+1),
                                                        sentences[index].text,
                                                        '\n',
                                                        chineseSentences[index].text))
            if index >= 5 : break # limit output sentence
        return '\n'.join(sentenceArray)

class gTTS_Thread(QThread):
    """
    google Text To Speech threading
    """
    def __init__(self,word,parent=None):
        super().__init__(parent)
        self.word = word
        
    def run(self):
        text_to_speech.TextToSpeech(self.word)

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