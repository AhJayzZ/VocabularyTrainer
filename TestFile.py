from bs4 import BeautifulSoup
import requests

mystr = "asshole"
url = "https://www.bing.com/dict/search?q={}".format(mystr)
myheader = {
    'cookie':'_EDGE_S=F&mkt=zh-cn' # this is key header
}

text = requests.get(url=url,headers=myheader).text
soup = BeautifulSoup(text,'html.parser')

# part of speech(詞性),definitions(定義)
pos = soup.find_all('span',class_='pos')
definitions = soup.find_all('span',class_='def b_regtxt')
infoArray = []

for index in range(max(len(pos),len(definitions))):
    infoArray.append("{}.(詞性:{}) {}".format(str(index+1),
                                           pos[index].text, 
                                           definitions[index].text))

wordInfo = '\n'.join(infoArray)
print(wordInfo)