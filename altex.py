import re
import requests
import pandas
import requests_random_user_agent
from bs4 import BeautifulSoup
from datetime import date

productsTitle = []
productsPrice = []
productsPriceII = []
oldPrice = []
storeLink = []
urlPagesAltex = [
            # "https://mediagalaxy.ro/jocuri-ps4/cpl/filtru/p/",
            # "https://mediagalaxy.ro/jocuri-xbox-one/cpl/filtru/p/",
            # "https://mediagalaxy.ro/jocuri-nintendo-switch/cpl/filtru/p/",
            "https://altex.ro/jocuri-ps4/cpl/filtru/p/", 
            "https://altex.ro/jocuri-xbox-one/cpl/filtru/p/", 
            "https://altex.ro/jocuri-nintendo-switch/cpl/filtru/p/"
        ]

for i in range(len(urlPagesAltex)):
    j = 1
    while True:
        url = urlPagesAltex[i] + str(j)
        # user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0"
        user_agent = str(requests.get('https://httpbin.org/user-agent'))
        data = requests.get(url=url, headers={"user-agent": user_agent})
        soup = BeautifulSoup(data.text, "html.parser")
        products = [x for x in soup.find_all("li", {"class": "Products-item"})]
        if len(products) == 0:
            print("Page: " + str(j - 1))
            break
        productsTitle += [x.find("a", {"class": "Product-name"})["title"] for x in products]
        productsPrice += [x.find("span", {"class": "Price-int"}).text.strip("<span class=\"Price-int\">") for x in products]
        productsPriceII += [x.find("sup", {"class": "Price-dec"}).text.strip("<sup class=\"Price-dec\">,<!-- -->") for x in products]
        oldPrice += [str(x.find("div", {"class": "Price-old"})).strip("<div class=\"Price-old\">") for x in products]
        storeLink += url
        j += 1

# remove empty records and "</"
oldPrice[:] = [str(x).strip("</") for x in oldPrice]
oldPrice[:] = [x if str(x) != "Non" else "" for x in oldPrice]

df = pandas.DataFrame({"Titlu": productsTitle, "productsPrice": productsPrice, "productsPriceII": productsPriceII, "Original Price": oldPrice})
#concat the two temp price columns
df["Final Price"] = df["productsPrice"].astype(str)+ "," + df["productsPriceII"].astype(str)
# drop the no longer needed and empty columns
del df["productsPrice"]
del df["productsPriceII"]
df.to_excel(str(date.today().strftime("%b-%d-%Y")) + "_Altex.xlsx")
