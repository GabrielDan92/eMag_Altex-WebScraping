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

j = 1
while True:
    print(f"currently at page: {j}")
    url = f"https://www.emag.ro/jocuri-consola-pc/p{j}/c"
    # user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0"
    user_agent = str(requests.get('https://httpbin.org/user-agent'))
    data = requests.get(url=url, headers={"user-agent": user_agent})
    soup = BeautifulSoup(data.text, "html.parser")
    count = soup.find("span", {"class": "visible-xs"})
    count = re.findall(r'((?<=\">1 din ).*([^\r]*)(?=</span>))', str(count))
    count = str(count[0]).strip("('")
    count = int(count.strip("', '')"))
    products = [x for x in soup.find_all("div", {"class": "card-item"})]
    if j > count:
        print("Page: " + str(j - 1))
        break
    if len(products) == 0:
        print("Page: " + str(j - 1))
        break
    productsTitleTemp = [x.find("h2", {"class": "card-body"}) for x in products]
    productsTitle += [re.findall(r'(((?<=title=\").*([^\r]*)(?=">)))', str(x)) for x in productsTitleTemp]
    productsPriceTemp = [x.find("p", {"class": "product-old-price"}) for x in products]
    productsPriceII += [re.findall(r'((?<=\<sup>).*([^\r]*)(?=</sup>))', str(x)) for x in productsPriceTemp]
    productsPrice += [re.findall(r'((?<=\<s>).*([^\r]*)(?=<sup>))', str(x)) for x in productsPriceTemp]
    storeLink += url
    j += 1

# remove empty records and "</"
oldPrice[:] = [str(x).strip("</") for x in oldPrice]
oldPrice[:] = [x if str(x) != "Non" else "" for x in oldPrice]
productsTitle[:] = [str(x).strip("[('") for x in productsTitle]
productsTitle[:] = [str(x).strip("'')]") for x in productsTitle]
productsPrice[:] = [str(x).strip("[('") for x in productsPrice]
productsPrice[:] = [str(x).strip("', '')]") for x in productsPrice]
productsPriceII[:] = [str(x).strip("[('") for x in productsPriceII]
productsPriceII[:] = [str(x).strip("', '')]") for x in productsPriceII]

df = pandas.DataFrame({"Titlu": productsTitle, "productsPrice": productsPrice, "productsPriceII": productsPriceII})
#concat the two temp price columns
df["Final Price"] = df["productsPrice"].astype(str)+ "," + df["productsPriceII"].astype(str)
# drop the no longer needed and empty columns
del df["productsPrice"]
del df["productsPriceII"]
df.to_excel(str(date.today().strftime("%b-%d-%Y")) + "_eMag.xlsx")
