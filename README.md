### eMag & Altex WebScraping

The Python script extracts all the pages from a given eMag link in less than 20 seconds and saves the data in an Excel output file. In the below example the script extracted all the 25 pages with aprox 1500 products from the mobile phones eMag page (https://www.emag.ro/telefoane-mobile/c). <p>
By sending a different header with each request using https://httpbin.org/user-agent, I managed to bypass the anti spyder/scrapping tools eMag is currently using. Otherwise, the website would lock me out after several requests.

#### Python tools used:

* Pandas
* Requests
* Threading
* BeautifulSoup
* Regular Expressions/Regex

![eMag](emag.gif)
