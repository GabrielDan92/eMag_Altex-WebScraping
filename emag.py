import re
import pandas as pd
import requests
import threading
from bs4 import BeautifulSoup
from datetime import date
import ctypes


class EmagScraper:
    """
    A class for scraping product data from eMag and processing it.

    Attributes:
        products_title (list): A list to store product titles.
        products_price (list): A list to store product prices.
        products_price_ii (list): A list to store product price fractions.
        products_price_old (list): A list to store original product prices.
        products_price_old_ii (list): A list to store original product price fractions.
        product_link (list): A list to store product links.
        page_count (int): The total number of pages to scrape.
    """

    def __init__(self):
        self.products_title = []
        self.products_price = []
        self.products_price_ii = []
        self.products_price_old = []
        self.products_price_old_ii = []
        self.product_link = []

    def scrape_emag(self, url, page):
        """
        Scrape product data from a specific eMag page and store it in class attributes.

        Args:
            url (str): The URL of the eMag page to scrape.
            page (int): The page number being scraped.
        """
        user_agent = str(requests.get('https://httpbin.org/user-agent'))
        data = requests.get(url=url, headers={"user-agent": user_agent})
        soup = BeautifulSoup(data.text, "html.parser")
        products = soup.find_all("div", {"class": "card-item"})

        for product in products:
            self.extract_product_info(product)

        print(f"Scraped page {page}/{self.page_count}")

    def extract_product_info(self, product):
        """
        Extract product information (title, price, and link) from a product card.

        Args:
            product: The BeautifulSoup object representing a product card.
        """
        title = product.find("h2", {"class": "card-body"})
        price_old = product.find("p", {"class": "product-old-price"})
        price_new = product.find("p", {"class": "product-new-price"})

        if title:
            self.products_title.append(title.find("a")["title"])
        if price_old:
            price_old_text = price_old.find("s").text
            price_old_ii = price_old.find("sup").text
            self.products_price_old.append(price_old_text)
            self.products_price_old_ii.append(price_old_ii)
        if price_new:
            price_new_text = price_new.find("span").text
            price_new_ii = price_new.find("sup").text
            self.products_price.append(price_new_text)
            self.products_price_ii.append(price_new_ii)
        if title:
            self.product_link.append("https://www.emag.ro" + title.find("a")["href"])

    def process_data(self, url):
        """
        Process scraped data, clean it, and save it to an Excel file.

        Args:
            url (str): The eMag URL to scrape.
        """
        try:
            self.scrape_emag_pages(url)
            df = self.create_dataframe()
            self.clean_data(df)
            self.save_to_excel(df, url)
            ctypes.windll.user32.MessageBoxW(0, "All prices have been extracted.", "Warning", 0)
        except Exception as e:
            ctypes.windll.user32.MessageBoxW(0, f"Error: {str(e)}", "Error", 0)

    def scrape_emag_pages(self, url):
        """
        Scrape multiple pages of eMag products concurrently using threads.

        Args:
            url (str): The base eMag URL.
        """
        data = requests.get(url)
        soup = BeautifulSoup(data.text, "html.parser")
        page_count = soup.find("span", {"class": "visible-xs"})
        page_count = re.findall(r'((?<=\">1 din ).*([^\r]*)(?=</span>))', str(page_count))
        self.page_count = int(str(page_count[0]).strip("('"))

        threads = []
        for i in range(1, self.page_count + 1):
            thread_obj = threading.Thread(target=self.scrape_emag, args=(url + f"/p{i}/c", i))
            threads.append(thread_obj)
            thread_obj.start()

        for thread in threads:
            thread.join()

    def create_dataframe(self):
        """
        Create a Pandas DataFrame from scraped data.

        Returns:
            pd.DataFrame: The DataFrame containing scraped product data.
        """
        data = {
            "Title": self.products_title,
            "Original Price": [f"{p}, {ii}" for p, ii in zip(self.products_price_old, self.products_price_old_ii)],
            "Current Price": [f"{p}, {ii}" for p, ii in zip(self.products_price, self.products_price_ii)],
            "Link": self.product_link,
        }
        df = pd.DataFrame(data)
        df = df[df['Title'] != '']
        df.set_index("Title", inplace=True)
        return df

    def clean_data(self, df):
        """
        Clean the scraped data by removing unwanted characters.

        Args:
            df (pd.DataFrame): The DataFrame containing scraped data.
        """
        bad_chars = [
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

        for old, new in bad_chars:
            df["Original Price"] = df["Original Price"].str.replace(old, new)
            df["Current Price"] = df["Current Price"].str.replace(old, new)

    def save_to_excel(self, df, url):
        """
        Save the DataFrame to an Excel file.

        Args:
            df (pd.DataFrame): The DataFrame to save.
            url (str): The eMag URL used for generating the file name.
        """
        url_file_name = url.split("/")[-1]
        file_name = f"{date.today().strftime('%b-%d-%Y')}_eMag_{url_file_name}.xlsx"
        df.to_excel(file_name)


if __name__ == "__main__":
    while True:
        user_input = input("Add eMag link here: ")
        if user_input != "":
            break

    scraper = EmagScraper()
    scraper.process_data(user_input)
