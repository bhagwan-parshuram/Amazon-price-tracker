import requests as req
from bs4 import BeautifulSoup
import sys
import csv
from pathlib import Path
import os
import datetime
import smtplib
import time
header = {
    "User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36 Edg/91.0.864.54'
}

#function to convert string to number

def convertToNum(temp):
    PriceInNum = ""
    for char in temp:
        if (char.isdigit()):
            PriceInNum += char
    PriceInNum = int(PriceInNum) / 100
    return PriceInNum
    



#Class to get the current rate and original Price
class scrape:
    def __init__(self,url):
        self.url = url
        self.currPriceInNum = -1
        self.basePriceInNum = -1

    def findPrice(self):
        page = req.get(self.url,headers=header).text#obtainging the page
        soup = BeautifulSoup(page, "lxml")#creating a soup to search it easily
        Current_price = soup.select("#priceblock_ourprice")#getting the price in string along with some extra characters
        original_price = soup.select(".priceBlockStrikePriceString")#obtaining the original price

        if (len(Current_price) == 0 or len(original_price)==0):
            print("Currently Out of Stock........")
            return -1
        else:
            currrency = "₹"
            temp1 = Current_price[0].text
            temp2=original_price[0].text
            self.currPriceInNum = convertToNum(temp1)
            self.basePriceInNum = convertToNum(temp2)
            return self.currPriceInNum

    def calculateDiscount(self):
        self.findPrice()
        if (self.basePriceInNum == -1 or self.currPriceInNum == -1):
            print("Currently Out of Stock...........")
            return - 1
        diff=(self.basePriceInNum-self.currPriceInNum)
        return (diff*100)/self.basePriceInNum
         
def writeToFile(price,discount):
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    flag=1
    for file in files:
        if (file == "priceData.csv"):
            flag = 0
    with open("priceData.csv", "a") as file:
        writer = csv.writer(file, lineterminator="\n")
        if (flag):
            columns = ["Date","Time","Price(Rupee)", "Discount(%)"]
            writer.writerow(columns)
        current = datetime.datetime.now()
        writer.writerow(
            [str(current.day) + "/" + str(current.month) + "/" + str(current.year),
            (str(current.hour) + ":" + str(current.minute) + ":" + str(current.second)),
             price,
             str(int(discount))+" %"]
            )



def sendMessage(url,mail,currentPrice,OriginalPrice,dicount):
    server=smtplib.SMTP("smtp.gmail.com",587)#setting up connection with the server
    server.ehlo()
    server.starttls()#encrypting messages
    server.ehlo()
    
    myMail = 'amazon.price.tracker0001@gmail.com'
    myPassword="harryisgoodboy123#"
    server.login(myMail,myPassword)
    sub="Congrats!! Your item is now available for purchase with your desired price "
    body=f"Link: {url} \n Current Price: {int(currentPrice)} \n Original Price: {int(OriginalPrice)} \n Discount: {discount}"
    message=f"Subject: {sub}\n\n\n\n {body}  \n\n\n Regards\n Amazon Price Tracker BOT"
    server.sendmail(mail, myMail, message)

    print("Successful....")
    server.quit()




if (__name__ == "__main__"):
    url = input("Enter the url here: ")
    mail = input("Enter your email: ")
    item = scrape(url)
    tim  = int(input("Mention your time interval to check the price in second:"))
    minimumPriceTopurcase = input("Enter the price below which you want to receive the message: ")
    minimumPriceTopurcase=float(minimumPriceTopurcase)
    while (True):
         currentPrice = item.findPrice()
         OriginalPrice=item.basePriceInNum
         discount = item.calculateDiscount()
         if (currentPrice != -1):
            writeToFile(currentPrice, discount)
         if(currentPrice <= minimumPriceTopurcase):
             print("Sending Mail...........")
             sendMessage(url, mail,currentPrice,OriginalPrice,discount)
             break
         time.sleep(tim)
          
       
        