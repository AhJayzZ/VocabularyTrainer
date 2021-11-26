# 單字訓練機 Vocabulary Trainer

## 簡介 Introduction

### ★★★此程式必須連接網路才可使用★★★
單字就如同蓋房子的磚頭數量一樣，是英文能力的一種根基，單字知道得越多，解析某些文章或許會更加流暢與快速，此程式透過隨機產生單字來達到學習，遇到沒學過或是想背誦的單字可以新增到單字清單中，只要想要複習單字即可點開程式進行學習或複習。

主要通過將單字資訊、例句和圖片都分別拆成不同Thread，各自去爬取資訊後返回內容呈現於GUI物件上，但圖片有時會與單字相關性不高，仍有許多功能可以增加或是改善。

- 單字資訊:[Bing搜尋引擎](https://www.bing.com/dict/search)
- 單字例句:[金山辭霸(訪問太多次會被Rejected)](http://www.iciba.com/word)
- 單字圖片:[Unsplash圖庫API](https://unsplash.com/napi/search?query=)

----------------------------------------
## 環境設定 Environment
- 1.開發環境:**Python 3.7.8**
- 2.在終端機執行 ```pip install -r requirements.txt``` 安裝會使用到的套件
- 3.使用工具:
    - 訪問網頁:```requests==2.25.1```
    - 解析網頁元素:```beautifulsoup4==4.10.0```
    - 翻譯單字(如果無結果時):```googletrans==3.0.0```
    - 圖像矩陣化:```numpy==1.19.3```
    - 圖像轉換:```opencv_contrib_python==4.5.3.56```
    - 儲存聲音檔:```gTTS==2.2.2```
    - 撥放聲音:```playsound==1.3.0```
    - GUI設計:```PyQt5==5.15.6```
----------------------------------------
## 運作方式 Operation
- ### 架構圖 Architecture
    ![](https://i.imgur.com/njV4GVn.png)

- ### 其他功能 Other Function
    ![](https://i.imgur.com/KpmDrk9.png)

----------------------------------------
## 成果 Result

- ### 完整結果
    ![](https://i.imgur.com/O5azufk.png)

    ![](https://i.imgur.com/IZIhEfu.png)
    
    ![](https://i.imgur.com/iuJ3iDL.png)

- ### 非完整結果
    ![](https://i.imgur.com/XKCccSK.png)
    
    ![](https://i.imgur.com/Apmr5V6.png)


- ### 點擊單字紀錄
    ![](https://i.imgur.com/nCwfGKc.png)