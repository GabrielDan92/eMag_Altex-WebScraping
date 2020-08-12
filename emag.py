import re
import requests
import pandas
import threading
import requests_random_user_agent
from bs4 import BeautifulSoup
from datetime import date


### THREADING WEBSCRAPING ###
productsTitle = []
productsPrice = []
productsPriceII = []
productsPriceOld = []
productsPriceOldII = []
productLink = []

def emag(i):
    global productsTitle
    global productsPriceOldII
    global productsPriceOld
    global productsPriceII
    global productsPrice
    global productLink
    url = f"https://www.emag.ro/jocuri-consola-pc/p{i}/c"
    # user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0"
    user_agent = str(requests.get('https://httpbin.org/user-agent'))
    data = requests.get(url=url, headers={"user-agent": user_agent})
    soup = BeautifulSoup(data.text, "html.parser")
    products = [x for x in soup.find_all("div", {"class": "card-item"})]
    print(f"Current page: {i}")
    if len(products) == 0:
        print("Page: " + str(int(i) - 1))
        return
    productsTitleTemp = [x.find("h2", {"class": "card-body"}) for x in products]
    productsTitle += [re.findall(r'(((?<=title=\").*([^\r]*)(?=">)))', str(x)) for x in productsTitleTemp]
    productsPriceTempOld = [x.find("p", {"class": "product-old-price"}) for x in products]
    productsPriceOldII += [re.findall(r'((?<=\<sup>).*([^\r]*)(?=</sup>))', str(x)) for x in productsPriceTempOld]
    productsPriceOld += [re.findall(r'((?<=\<s>).*([^\r]*)(?=<sup>))', str(x)) for x in productsPriceTempOld]
    productsPriceTemp = [x.find("p", {"class": "product-new-price"}) for x in products]
    productsPriceII += [re.findall(r'((?<=\<sup>).*([^\r]*)(?=</sup>))', str(x)) for x in productsPriceTemp]
    productsPrice += [re.findall(r'((?<=\<p class="product-new-price">).*([^\r]*)(?=<sup>))', str(x)) for x in productsPriceTemp]
    productLink += [re.findall(r'(https://www.emag.ro.*?/\")', str(x)) for x in products]

# find the page count
url = "https://www.emag.ro/jocuri-consola-pc/c"
user_agent = str(requests.get('https://httpbin.org/user-agent'))
data = requests.get(url=url, headers={"user-agent": user_agent})
soup = BeautifulSoup(data.text, "html.parser")
count = soup.find("span", {"class": "visible-xs"})
count = re.findall(r'((?<=\">1 din ).*([^\r]*)(?=</span>))', str(count))
count = str(count[0]).strip("('")
count = int(count.strip("', '')"))

# generate threads for each page
threads = []
for i in range(1, count + 1):
    threadObj = threading.Thread(target=emag, args=(i,))
    threads.append(threadObj)
y = [x.start() for x in threads]
y = [x.join() for x in threads]

# clean the retrieved data
badChars = [
    ('\[\(\'', ''),
    ('\,\)\]', ''),
    ('\[\]', ''),
    ('\[\'', ''),
    ('\'', ''),
    ('/\"', ''),
    (', \)\]', ''),
    ('\]', ''),
    ('\&amp\;#039\;', '\'')
]

for old, new in badChars:
    productLink[:] = [re.sub(old, new, str(x)) for x in productLink]
    productsTitle[:] = [re.sub(old, new, str(x)) for x in productsTitle]
    productsPrice[:] = [re.sub(old, new, str(x)) for x in productsPrice]
    productsPriceII[:] = [re.sub(old, new, str(x)) for x in productsPriceII]
    productsPriceOld[:] = [re.sub(old, new, str(x))  for x in productsPriceOld]
    productsPriceOldII[:] = [re.sub(old, new, str(x))  for x in productsPriceOldII]

productsTitle[:] = [str(x).split(",") for x in productsTitle]
productsTitle[:] = [x[0] for x in productsTitle]
productLink[:] = [str(x).split(",") for x in productLink]
productLink[:] = [x[0] for x in productLink]

df = pandas.DataFrame({"Titlu": productsTitle, "productsPrice": productsPrice, "productsPriceII": productsPriceII, "productsPriceOld": productsPriceOld, "productsPriceOldII": productsPriceOldII, "Link": productLink})

# concat the two temp price columns
df["Pret Final"] = df["productsPrice"].astype(str)+ "," + df["productsPriceII"].astype(str)
df["Pret Original"] = df["productsPriceOld"].astype(str)+ "," + df["productsPriceOldII"].astype(str)

# replace empty values "," with blank values
df["Pret Original"][df["Pret Original"] == ","] = ""

# drop empty columns and reassign the columns to the dataframe
df = df[["Titlu", "Pret Original", "Pret Final", "Link"]]
df = df[df.Titlu != '']
df.to_excel(str(date.today().strftime("%b-%d-%Y")) + "_eMag.xlsx")
