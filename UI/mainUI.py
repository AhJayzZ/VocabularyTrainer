from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from cv2 import imread

from .Ui_init import *

from bs4 import BeautifulSoup
from googletrans import Translator
import text_to_speech
import cv2
import numpy
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
        self.imageLabel.setScaledContents(True)

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

        self.gTTS_thread = gTTS_Thread(self.randomWord)
        self.wordInfoCrawler_thread = wordInfoCrawler(self.randomWord)
        self.wordSentenceCrawler_thread = wordSentenceCrawler(self.randomWord)
        self.wordImageCrawler_thread = wordImageCrawler(self.randomWord)
        self.wordInfoCrawler_thread.finishSingal.connect(self.updateRandomWordInfo)
        self.wordSentenceCrawler_thread.finishSingal.connect(self.updateRandomWordInfo)
        self.wordImageCrawler_thread.finishSingal.connect(self.updateRandomWordInfo)
        self.wordImageCrawler_thread.start()
        self.wordInfoCrawler_thread.start()
        self.wordSentenceCrawler_thread.start()
        self.gTTS_thread.start()
        
        # Avoid too fast refresh
        self.generateButton.setEnabled(False)   
        self.addButton.setEnabled(False)
        self.removeButton.setEnabled(False)

    def updateRandomWordInfo(self):
        """
        update wordInfoLabel and wordSentenceLabel
        """
        if (self.wordInfoCrawler_thread.isFinished() and 
            self.wordSentenceCrawler_thread.isFinished() and 
            self.wordImageCrawler_thread.isFinished()):
                self.addButton.setEnabled(True)
                self.removeButton.setEnabled(True)
                self.generateButton.setEnabled(True)
                self.generateButton.setDefault(True)

        # Word
        if self.wordInfoCrawler_thread.isFinished():
            if not self.wordInfoCrawler_thread.wordInfo:
                translator = Translator()
                self.wordInfoCrawler_thread.wordInfo = translator.translate(self.randomWord, src='en', dest='zh-tw').text
            self.wordInfoLabel.setText(self.wordInfoCrawler_thread.wordInfo)
        # Sentence
        if self.wordSentenceCrawler_thread.isFinished():
            if not self.wordSentenceCrawler_thread.wordSentences:
                self.wordSentenceCrawler_thread.wordSentences = 'Found nothing sentence...'
            self.wordSentenceLabel.setText(self.wordSentenceCrawler_thread.wordSentences)
        # Image
        if self.wordImageCrawler_thread.isFinished():
            if self.wordImageCrawler_thread.image:
                self.imageLabel.setPixmap(self.wordImageCrawler_thread.image)
            else:
                self.wordImageCrawler_thread.image = None
                self.imageLabel.setText('Found nothing image...')

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
        if not self.selectedItem: return
        else:
            self.recordList.takeItem(self.itemIndex)
            with open('localRecord.json','r',encoding='utf-8') as file:
                fileContent = json.load(file)
            with open('localRecord.json','w',encoding='utf-8') as file:
                if self.selectedItem.text() in fileContent[self.itemIndex].values():
                    del fileContent[self.itemIndex]
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
        with open('localRecord.json','r',encoding='utf-8') as file:
            fileContent = json.load(file)
            self.selectedItem = self.recordList.currentItem()
            self.itemIndex = self.recordList.row(self.selectedItem)
            self.wordLabel.setText(fileContent[self.itemIndex]['word'])
            self.wordInfoLabel.setText(fileContent[self.itemIndex]['info'])
            self.wordSentenceLabel.setText(fileContent[self.itemIndex]['sentences'])
            if fileContent[self.itemIndex]['imageUrl']:
                self.generateButton.setEnabled(False)   
                self.addButton.setEnabled(False)
                self.removeButton.setEnabled(False)
                self.imageLabel.setPixmap(self.urlToPyqtImage(fileContent[self.itemIndex]['imageUrl']))
            else:
                self.imageLabel.setText('Found nothing image...')
            self.addButton.setEnabled(True)
            self.removeButton.setEnabled(True)
            self.generateButton.setEnabled(True)
            self.generateButton.setDefault(True)

            file.close()

    def loadRecord(self):
        """
        load local record 
        """
        with open('localRecord.json','r',encoding='utf-8') as file:
            fileContent = json.load(file)
            for index in range(len(fileContent)):
                self.recordList.addItem(fileContent[index]['word'])
            file.close()

    def addRecord(self): 
        """
        add word dictionary to local record
        """
        if not os.path.exists('localRecord.json'):
            open('localRecord.json','w')

        wordDict = {"word":self.randomWord,
                    "info":self.wordInfoCrawler_thread.wordInfo,
                    "sentences":self.wordSentenceCrawler_thread.wordSentences,
                    "imageUrl":self.wordImageCrawler_thread.imageUrl}
        with open('localRecord.json','r+',encoding='utf-8') as file:
            fileContent = json.load(file)
            fileContent.append(wordDict)
            file.seek(0)
            json.dump(fileContent,file,ensure_ascii=False)
            file.close()

    def urlToPyqtImage(self,url):
        imageContent = requests.get(url).content
        image = numpy.array(bytearray(imageContent),dtype="uint8")
        image = cv2.imdecode(image,cv2.IMREAD_COLOR)

        #PyQt image format
        height, width = image.shape[:2]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pyqt_img = QImage(image,width,height,QImage.Format_RGB888)
        pyqt_img = QPixmap.fromImage(pyqt_img)
        return pyqt_img 
        
# ------------------------------------- Threading -------------------------------------
class wordInfoCrawler(QThread):
    """
    get word info crawler 
    """
    finishSingal = pyqtSignal(int)
    def __init__(self,word):
        super().__init__(parent=None)
        self.word = word
        self.infoUrl = "https://www.bing.com/dict/search?q={}".format(word)
        self.infoUrlHeader = {'cookie':'_EDGE_S=F&mkt=zh-cn'} # this is key header

    def run(self):
        self.infoHtmlContent = requests.get(url=self.infoUrl,headers=self.infoUrlHeader).text
        self.infoSoup = BeautifulSoup(self.infoHtmlContent,'html.parser')
        self.wordInfo = self.getWordInfo()
        self.finishSingal.emit(1)
    
    def getWordInfo(self):
        pos = self.infoSoup.find_all('span',class_='pos')
        definitions = self.infoSoup.find_all('span',class_='def b_regtxt')
        wordInfoArray = []
        for index in range(max(len(pos),len(definitions))):
            wordInfoArray.append("{}.(詞性:{}) {}".format(str(index+1),
                                                    pos[index].text, 
                                                    definitions[index].text))
        return '\n'.join(wordInfoArray)


class wordSentenceCrawler(QThread):
    """
    get word sentences crawler
    """
    finishSingal = pyqtSignal(int)
    def __init__(self,word):
        super().__init__(parent=None)
        self.word = word
        self.sentenceUrl = "http://www.iciba.com/word?w={}".format(word)
        self.sentenceUrlHeader={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}

    def run(self):
        self.sentenceHtmlContent = requests.get(url=self.sentenceUrl,headers=self.sentenceUrlHeader).text
        self.sentenceSoup = BeautifulSoup(self.sentenceHtmlContent,'html.parser')
        self.wordSentences = self.getWordSentences()
        self.finishSingal.emit(1)
    
    def getWordSentences(self):
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

class wordImageCrawler(QThread):
    """
    get word image crawler
    """
    finishSingal = pyqtSignal(int)
    def __init__(self,word):
        super().__init__(parent=None)
        self.word = word
        self.imagesUrl = "https://unsplash.com/napi/search?query={}".format(word)
    
    def run(self):
        self.imageHtmlContent = requests.get(url=self.imagesUrl).text
        self.imageSoup = BeautifulSoup(self.imageHtmlContent,'html.parser')
        self.image,self.imageUrl = self.getWordImage()
        self.finishSingal.emit(1)

    def getWordImage(self):
        try:
            imageJson = json.loads(self.imageHtmlContent)
            imageUrl = imageJson['collections']['results'][0]['cover_photo']['urls']['regular']
            imageContent = requests.get(imageUrl).content
            image = numpy.array(bytearray(imageContent),dtype="uint8")
            image = cv2.imdecode(image,cv2.IMREAD_COLOR)

            #PyQt image format
            height, width = image.shape[:2]
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pyqt_img = QImage(image,width,height,QImage.Format_RGB888)
            pyqt_img = QPixmap.fromImage(pyqt_img)
            return pyqt_img,imageUrl 
        except:
            return None,None

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
            self.mainWindow.connectionLabel.setText('Connection: Success')
        except requests.exceptions.ConnectionError:
            self.mainWindow.connectionLabel.setStyleSheet('color:red')
            self.mainWindow.connectionLabel.setText('Connection: Failed')