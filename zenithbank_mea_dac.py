import scrapy
from bs4 import BeautifulSoup
import requests as req
from locations.items import GeojsonPointItem
import uuid

class zenithbank(scrapy.Spider):
    name = 'zenithbank_mea_dac'
    start_urls = ['https://www.zenithbank.com/atm-locator/atmlocatorall']
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'}

     
    def parse(self, response):
         soup = BeautifulSoup(response.text, 'html.parser')
         soup_class=soup.find('tbody')
         soup_class=soup_class.find_all('tr')
        

         for one in soup_class:
             all=one.find_all('td')
             name=all[2].get_text()
             state=all[1].get_text()
             address=all[3].get_text()
            


             singledata = {
                'ref': uuid.uuid4().hex,
                'addr_full': address,
                'name': name,
                'state':state,
                'website':"https://www.zenithbank.com/atm-locator/atmlocatorall",
                'brand':"Zenith Bank",
                'chain_name':"Zenith Bank",
                'chain_id':"4401"
                
             }
             yield GeojsonPointItem(**singledata)
           
           
