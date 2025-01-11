import scrapy
from scrapy.selector import Selector
from locations.items import GeojsonPointItem
from locations.categories import Code
import uuid


class DominosSpider(scrapy.Spider):
    name = "domino_ind_dac"
    start_urls = ["https://www.dominos.co.in/store-location/new-delhi"]
    
    def parse(self, response):
        sel = Selector(response)
        loc_links = sel.css('a.citylink:not([href="#"])::attr(href)').getall()
        
        loc_set = set()
        for link in loc_links:
            linktext = 'https://www.dominos.co.in' + link
            loc_set.add(linktext)
            
        for link in loc_set:
            yield scrapy.Request(link, callback=self.parse_location)
    
    def parse_location(self, response):
        sel = Selector(response)
        stores = sel.css('p.grey-text.mb-0::text').getall()
        phone_no = sel.css('p.fontsize2.bold.zred::text').getall()
        openinghrs = sel.css('div.col-xs-9.col-md-9.pl0.search-grid-right-text::text').getall()

        for store, phone, hours in zip(stores, phone_no, openinghrs):
            data= {
                'ref': uuid.uuid4().hex,
                'addr_full': store.strip(),
                'phone': phone.strip(),
                'opening_hours': hours.strip(),
                'chain_id':"1522",
                'chain_name':"Dominos",
                "brand":"Dominos",
                "website":"https://www.dominos.co.in/",
            }
            yield GeojsonPointItem(**data)