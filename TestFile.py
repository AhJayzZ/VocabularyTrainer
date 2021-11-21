from bs4 import BeautifulSoup
import requests
import json,os

# mystr = "bad"
# url = "http://www.iciba.com/word?w={}".format(mystr)
# header ={
#     'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
# }

# text = requests.get(url=url,headers=header).text
# soup = BeautifulSoup(text,'html.parser')

# sentences = soup.find_all('p',class_='NormalSentence_en__3Ey8P')
# chineseSentences = soup.find_all('p',class_='NormalSentence_cn__27VpO')

# for index in range(len(sentences)):
#     if chineseSentences[index].text:
#         print(sentences[index].text)
#         print(chineseSentences[index].text)


a = '測'

print(a.encode('utf-8').decode())



